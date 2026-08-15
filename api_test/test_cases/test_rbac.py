"""
@Project:gouguoa-auto-test
@File   :test_rbac.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 14:34
"""
import pytest
from config.conf import ADD_ACCOUNT_URL, DB

@pytest.mark.rbac
def test_add_account(admin_api_login, db_connect):
    """"添加用户接口"""
    change_data = {
        "name": "王五",
        "mobile": "13345678918",
        "email": "2296543813@qq.com",
        "file": "",
        "sex": "1",
        "entry_time": "2026-08-15",
        "did": "7",
        "department_ids": "",
        "position_id": "4",
        "pid": "0",
        "type": "2",
        "is_staff": "1",
        "is_hide": "0",
        "auth_did": "3",
        "id": "6"
    }
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        "content-type": "application/json; charset=utf-8"
    }
    resp = admin_api_login.request("POST" ,ADD_ACCOUNT_URL, data=change_data, headers=headers)
    assert '没有权限' not in resp.text, '操作失败'       # 显式排除失败页
    db = db_connect.get_db_connection(
        **DB
    )