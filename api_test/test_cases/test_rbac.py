"""
@Project:gouguoa-auto-test
@File   :test_rbac.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 14:34
"""
import pytest
from config.conf import ADD_AND_EDIT_ACCOUNT_URL, DB, DELETE_ACCOUNT_URL
from string import digits
from requests import Response
from random import choice
from utils import DataBaseConnection, Logger, RequestHandle
from typing import Dict

class TestRbac:
    """测试 RBAC 权限控制"""
    name = "赵启"
    mobile = "13" + ''.join(choice(digits) for _ in range(9))
    email = str(choice(digits) * 4) + "@gougucms.com",
    did = str(choice(range(1, 16)))
    position_id = str(choice(range(1, 5)))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
        "X-Requested-With": "XMLHttpRequest"
    }
    @pytest.fixture
    def unique_user_data(self) -> Dict[str, str]:

        return {
                "name": self.name,
                "mobile": self.mobile,
                "email": str(self.email),
                "reg_pwd": "123456",
                "sex": str(choice([1, 2])),
                "entry_time": "2026-08-15",
                "did": self.did,
                "position_id": self.position_id,
                "department_ids": "",
                "pid": "0",
                "type": "2",
                "is_staff": "1",
                "is_hide": "0",
                "auth_did": "3",
            }

    @staticmethod
    def verify_success_response(response: Response, expected_code: int = 0, expected_msg: str = '操作成功'):
        """
        验证接口返回的成功响应
        :param response: requests.Response 对象
        :param expected_code: 期望的 code 值，默认 0
        :param expected_msg: 期望的 msg 值，默认 '操作成功'
        """
        assert response.status_code == 200, f"响应失败, 当前响应码为：{response.status_code}"
        res = response.json()
        code = res.get('code')
        msg = res.get('msg')
        assert code == expected_code, f'操作失败，code={code}, msg={msg}'
        assert expected_msg in msg, f'操作失败，当前信息: {msg}'

    @pytest.mark.auth
    @pytest.mark.rbac
    def test_normal_user_cannot_add_account(self, normal_api_login: RequestHandle, unique_user_data: Dict[str, str], logger: Logger):
        """普通用户调用添加用户接口应返回 405"""
        resp = normal_api_login.post(ADD_AND_EDIT_ACCOUNT_URL, data=unique_user_data, headers=self.headers)
        self.verify_success_response(resp, expected_code=405, expected_msg='没有权限')
        logger.info("✅ 普通用户无权限，返回 405")

    @pytest.mark.auth
    @pytest.mark.rbac
    def test_admin_add_account(self, admin_api_login: RequestHandle, unique_user_data: Dict[str, str], logger: Logger, db_connect: DataBaseConnection):
        """管理员添加新用户"""
        if self._verify_name_exist(db_connect, logger):  # 姓名不存在
            resp = admin_api_login.post(ADD_AND_EDIT_ACCOUNT_URL, data=unique_user_data, headers=self.headers)
            self.verify_success_response(resp)
            logger.info("✅ 管理员成功添加用户")
        else:
            pytest.skip("测试数据中用户已存在，跳过本次添加测试")

    def test_admin_edit_account(self, admin_api_login: RequestHandle, db_connect: DataBaseConnection, logger: Logger):
        """管理员修改已存在用户"""
        userid = 7
        edit_data: Dict[str, str|int] = {
            "id": userid,
            "mobile": "13" + ''.join(choice(digits) for _ in range(9)),
            "name": "赵武",
            "email": str(choice(digits) * 4) + "@gougucms.com",
            "sex": str(choice([1, 2])),
            "entry_time": "2026-08-15",
            "did": self.did,
            "position_id": self.position_id,
            "department_ids": "",
            "pid": "0",
            "type": "2",
            "is_staff": "1",
            "is_hide": "0",
            "auth_did": "3",
        }
        # 可选：验证用户存在
        if not self._user_exists_by_id(db_connect, userid):
            pytest.skip(f"用户 ID= {userid} 不存在")
        sql = "SELECT did, position_id, email, sex, mobile FROM oa_admin WHERE id = %s"
        old_user = db_connect.query(sql, (userid,))
        logger.info(f"修改前用户信息：{old_user}")

        resp = admin_api_login.post(ADD_AND_EDIT_ACCOUNT_URL, data=edit_data, headers=self.headers)
        self.verify_success_response(resp)

        db_connect.commit() # 提交事务
        new_user = db_connect.query(sql, (userid,))
        logger.info(f"修改后用户信息：{new_user}")
        logger.info("✅ 管理员成功修改用户")

    def test_del_account_unavailable(self, admin_api_login: RequestHandle, unique_user_data: Dict[str, str], logger: Logger):
        """删除用户接口未开放，应返回 405"""
        resp = admin_api_login.post(DELETE_ACCOUNT_URL, data=unique_user_data, headers=self.headers)
        self.verify_success_response(resp, expected_code=405, expected_msg='你没有权限,请联系管理员或者人事部')
        logger.info("✅ 删除接口未开放，返回 405")

    # 辅助方法
    @staticmethod
    def _user_exists_by_id(db_connect: DataBaseConnection, user_id: int) -> bool:
        db_connect.get_db_connection(**DB)
        result = db_connect.query("SELECT id FROM oa_admin WHERE id = %s", (user_id,))
        return bool(result)

    def _verify_name_exist(self, db_connect: DataBaseConnection, logger: Logger) -> bool:
        """
        验证员工姓名是否已存在
        :param db_connect: 数据库连接对象
        :param logger: 日志记录对象
        :return: True 表示姓名不存在（允许创建），False 表示已存在或查询出错
        """
        db_connect.get_db_connection(**DB)

        # 参数化查询，%s 占位符
        sql = "SELECT name FROM oa_admin WHERE name = %s"
        params = (self.name,)

        result = db_connect.query(sql, params=params)

        if result is None:
            logger.error("❌ 数据库查询出错，无法判断姓名是否存在，保守拒绝创建")
            return False
        elif not result:   # 空列表表示没有记录
            logger.info("✅ 员工姓名不存在，允许创建")
            return True
        else:
            logger.info("❌ 员工姓名已存在，不允许创建")
            return False