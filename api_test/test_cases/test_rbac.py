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
from random import choice

def random_str(length=9):
    return ''.join(choice(digits) for _ in range(length))

@pytest.mark.rbac
def test_add_account(admin_api_login, db_connect):
    """"添加用户接口"""
    db_connect.get_db_connection(
        **DB
    )
    p_num = db_connect.run_query('SELECT count(*) FROM oa_admin')[0].get('count(*)')  # 获取当前员工总数
    # 添加用户数据
    change_data = {
        # 员工基本信息
        "name": "赵启",                  # 员工姓名（必填）
        "mobile": "13"+''.join(random_str()),         # 手机号码（必填，用于登录）
        "reg_pwd": "123456",
        "email": random_str()+"@gougucms.com",    # 电子邮箱（必填）
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
    resp = admin_api_login.post(ADD_ACCOUNT_URL, data=change_data, headers=headers)
    assert '没有权限' not in resp.json(), '操作失败'       # 显式排除失败页
    res = resp.json()
    print(res)
    code = res.get('code')
    msg = res.get('msg')
    assert code == 0, '操作失败'
    assert msg == '操作成功', f'操作失败, 当前信息: {msg}'
    print(db_connect.run_query('SELECT * FROM oa_admin where username = "zhaoqi"'))