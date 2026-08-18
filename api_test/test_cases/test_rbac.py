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
        "email": "2296543810@qq.com",
        "sex": "1",
        "entry_time": "2026-08-15",
        "did": "7",
        "position_id": "4",
        "department_ids": "",
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
        "X-Requested-With": "XMLHttpRequest"
    }
    resp = admin_api_login.post(ADD_ACCOUNT_URL, data=change_data, headers=headers)
    assert '没有权限' not in resp.json(), '操作失败'       # 显式排除失败页
    db_connect.get_db_connection(
        **DB
    )
    res = resp.json()
    code = res.get('code')
    msg = res.get('msg')
    assert code == 0, '操作失败'
    assert msg == '操作成功', f'操作失败, 当前信息: {msg}'
    print(res)
    print(db_connect.run_query('SELECT * FROM oa_admin where username = "wangliu"')[0].get('email'))