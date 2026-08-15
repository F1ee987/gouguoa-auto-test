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
        "name": "王六",
        "mobile": "14345678918",
        "email": "2296543815@qq.com",
        "sex": "1",
        "entry_time": "2026-08-15",
        "did": "7",
        "position_id": "4",
        "pid": "0",
        "type": "2",
        "is_staff": "1",
        "is_hide": "0",
        "auth_did": "3",
        'id': 7
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" 
        "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
        "Cookies" : 'province_id=1; city_id=72; district_id=2799; PHPSESSID=bf4aed18d346534ac3654a0f7a1d4e22; gougutab={"tab_id":"97","tab_array"'
    }
    resp = admin_api_login.request("POST" ,ADD_ACCOUNT_URL, data=change_data, headers=headers)
    print(resp.text)
    assert '没有权限' not in resp.text, '操作失败'       # 显式排除失败页
    db_connect.get_db_connection(
        **DB
    )
    print(db_connect.run_query('SELECT * FROM oa_admin where username = "wangliu"')[0].get('email'))