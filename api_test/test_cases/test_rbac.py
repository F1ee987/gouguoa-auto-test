"""
RBAC 权限控制接口测试。

覆盖场景：
- 普通用户无权限新增账号（期望 405）；
- 管理员可按唯一姓名新增用户；
- 管理员可修改已存在用户（以 id=7 为例）；
- 删除用户接口未开放（期望 405）。
"""
from string import digits
from random import choice
from typing import Dict
import pytest
from config.conf import ADD_AND_EDIT_ACCOUNT_URL, DELETE_ACCOUNT_URL
from utils import DataBaseConnection, Logger, RequestHandle
from api_test.helpers.response import assert_api_success


class TestRbac:
    """RBAC 权限控制测试套件。"""

    # 新增用例使用的固定姓名（用于唯一性校验，避免重复创建）
    NEW_USER_NAME = "赵启"
    # 部门 / 岗位在用例间保持一致，仅生成一次
    DEPARTMENT_ID = str(choice(range(1, 16)))
    POSITION_ID = str(choice(range(1, 5)))

    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    @pytest.fixture
    def new_user_payload(self) -> Dict[str, str]:
        """构造一个待新增的用户数据（每次调用随机生成易变字段）。"""
        email_local = ''.join(choice(digits) for _ in range(4))
        return {
            "name": self.NEW_USER_NAME,
            "mobile": "13" + ''.join(choice(digits) for _ in range(9)),
            "email": f"{email_local}@gougucms.com",
            "reg_pwd": "123456",
            "sex": str(choice([1, 2])),
            "entry_time": "2026-08-15",
            "did": self.DEPARTMENT_ID,
            "position_id": self.POSITION_ID,
            "department_ids": "",
            "pid": "0",
            "type": "2",
            "is_staff": "1",
            "is_hide": "0",
            "auth_did": "3",
        }

    # --------------------------- 数据库辅助 ---------------------------
    @staticmethod
    def _user_exists(db: DataBaseConnection, user_id: int) -> bool:
        """判断指定 id 的用户是否存在。"""
        result = db.query("SELECT id FROM oa_admin WHERE id = %s", (user_id,))
        return bool(result)

    @staticmethod
    def _is_username_available(db: DataBaseConnection, username: str, logger: Logger) -> bool:
        """判断姓名是否未被占用（True=可创建）。

        查询异常时保守返回 False，避免重复创建脏数据。
        """
        result = db.query("SELECT name FROM oa_admin WHERE name = %s", (username,))
        if result is None:
            logger.error("❌ 数据库查询出错，无法判断姓名是否存在，保守拒绝创建")
            return False
        if not result:  # 空列表表示无记录
            logger.info("✅ 员工姓名不存在，允许创建")
            return True
        logger.info("❌ 员工姓名已存在，不允许创建")
        return False

    # --------------------------- 测试用例 ---------------------------
    @pytest.mark.auth
    @pytest.mark.rbac
    def test_normal_user_cannot_add_account(
        self, normal_api_login: RequestHandle, new_user_payload: Dict[str, str], logger: Logger
    ):
        """普通用户调用新增账号接口应返回 405（无权限）。"""
        response = normal_api_login.post(
            ADD_AND_EDIT_ACCOUNT_URL, data=new_user_payload, headers=self.REQUEST_HEADERS
        )
        assert_api_success(response, expected_code=405, expected_msg="没有权限")
        logger.info("✅ 普通用户无权限，返回 405")

    @pytest.mark.auth
    @pytest.mark.rbac
    def test_admin_add_account(
        self,
        admin_api_login: RequestHandle,
        new_user_payload: Dict[str, str],
        logger: Logger,
        db_connect: DataBaseConnection,
    ):
        """管理员新增用户（姓名不存在时才真正创建）。"""
        if self._is_username_available(db_connect, self.NEW_USER_NAME, logger):
            response = admin_api_login.post(
                ADD_AND_EDIT_ACCOUNT_URL, data=new_user_payload, headers=self.REQUEST_HEADERS
            )
            assert_api_success(response)
            logger.info("✅ 管理员成功添加用户")
        else:
            pytest.skip("测试数据中用户已存在，跳过本次添加测试")

    def test_admin_edit_account(
        self, admin_api_login: RequestHandle, db_connect: DataBaseConnection, logger: Logger
    ):
        """管理员修改已存在用户（以 id=7 为例）。"""
        user_id = 7
        if not self._user_exists(db_connect, user_id):
            pytest.skip(f"用户 ID={user_id} 不存在")

        email_local = ''.join(choice(digits) for _ in range(4))
        edit_payload: Dict[str, str] = {
            "id": user_id,
            "mobile": "13" + ''.join(choice(digits) for _ in range(9)),
            "name": "赵武",
            "email": f"{email_local}@gougucms.com",
            "sex": str(choice([1, 2])),
            "entry_time": "2026-08-15",
            "did": self.DEPARTMENT_ID,
            "position_id": self.POSITION_ID,
            "department_ids": "",
            "pid": "0",
            "type": "2",
            "is_staff": "1",
            "is_hide": "0",
            "auth_did": "3",
        }

        sql = "SELECT did, position_id, email, sex, mobile FROM oa_admin WHERE id = %s"
        before = db_connect.query(sql, (user_id,))
        logger.info(f"修改前用户信息：{before}")

        response = admin_api_login.post(
            ADD_AND_EDIT_ACCOUNT_URL, data=edit_payload, headers=self.REQUEST_HEADERS
        )
        assert_api_success(response)

        db_connect.commit()  # 提交事务，使修改生效
        after = db_connect.query(sql, (user_id,))
        logger.info(f"修改后用户信息：{after}")
        logger.info("✅ 管理员成功修改用户")

    def test_del_account_unavailable(
        self, admin_api_login: RequestHandle, new_user_payload: Dict[str, str], logger: Logger
    ):
        """删除用户接口未开放，应返回 405。"""
        response = admin_api_login.post(
            DELETE_ACCOUNT_URL, data=new_user_payload, headers=self.REQUEST_HEADERS
        )
        assert_api_success(response, expected_code=405, expected_msg="你没有权限,请联系管理员或者人事部")
        logger.info("✅ 删除接口未开放，返回 405")
