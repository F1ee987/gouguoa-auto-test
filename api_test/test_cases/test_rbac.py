"""
@Project:gouguoa-auto-test
@File   :test_rbac.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 14:34
"""
import pytest
from config.conf import ADD_ACCOUNT_URL, DB
from string import digits
from requests import Response
from random import choice
from utils import RequestHandle, DataBaseConnection, Logger

def random_str(length: int =9):
    return ''.join(choice(digits) for _ in range(length))

@pytest.mark.skip(reason="暂时不执行该测试用例")
class TestRbac:
    """测试rbac权限控制"""
    mobile = "13" + random_str(9)
    email = random_str(6) + "@gougucms.com"
    change_data = {
        # 员工基本信息
        "name": "赵启",                  # 员工姓名（必填）
        "mobile": mobile,         # 手机号码（必填，用于登录）
        "reg_pwd": "123456",
        "email": email,    # 电子邮箱（必填）
        "sex": str(choice([1,2])),                      # 员工性别：1-男，2-女（必填）
        "entry_time": "2026-08-15",      # 入职日期（必填，格式：YYYY-MM-DD）

        # 组织架构信息
        "did": str(choice([i for i in range(1,16)])),                      # 主部门ID（必填，对应部门表的ID）
        "position_id": str(choice([i for i in range(1,5)])),              # 岗位职称ID（必填，对应岗位表的ID）
        "department_ids": "",            # 次要部门ID（多个用逗号分隔，可为空）
        "pid": "0",                      # 上级主管ID（0表示无上级）

        # 员工属性
        "type": "2",                     # 员工类型：1-正式，2-试用，3-实习（必填）
        "is_staff": "1",                 # 身份类型：1-企业员工，2-劳动派遣，3-兼职员工（必填）
        "is_hide": "0",                  # 是否隐藏联系方式：0-否，1-是

        # 权限控制
        "auth_did": "3",                 # 数据权限范围：
        # 0-仅自己，1-主部门，2-次部门，3-主次部门，
        # 4-主部门及子部门，5-次部门及子部门，6-主次部门及子部门，
        # 7-主部门顶级及子部门，8-次部门顶级及子部门，9-主次顶级及子部门，10-所有部门
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
        "X-Requested-With": "XMLHttpRequest"
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
        print(res)   # 便于调试

    @pytest.mark.auth
    @pytest.mark.rbac
    def test_add_account_with_normal_user(self, normal_api_login: RequestHandle, db_connect: DataBaseConnection, logger: Logger):
        """"使用普通用户权限添加用户or修改用户信息接口, 预期返回405状态码"""
        db_connect.get_db_connection(
            **DB
        )
        resp = normal_api_login.post(ADD_ACCOUNT_URL, data=self.change_data, headers=self.headers)
        #验证
        self.verify_success_response(resp, expected_code=405, expected_msg='没有权限')   # 验证接口返回的成功响应
        logger.info("✅ 测试通过, 该用户无法修改用户信息")

    @pytest.mark.auth
    @pytest.mark.rbac
    def test_add_account_with_admin(self, admin_api_login: RequestHandle, db_connect: DataBaseConnection, logger: Logger):
        """"使用管理员权限添加or修改用户信息接口"""
        db_connect.get_db_connection(
            **DB
        )
        # 添加用户数据
        resp = admin_api_login.post(ADD_ACCOUNT_URL, data=self.change_data, headers=self.headers)
        #验证
        self.verify_success_response(resp)
        logger.info("✅ 测试通过, 该用户可以修改用户信息")