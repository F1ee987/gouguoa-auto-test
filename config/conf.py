"""
@Project:gouguoa-auto-test
@File   :conf.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 13:27
"""
from pathlib import Path
from typing import Dict
from time import time

#URL信息
BASE_URL = "http://192.168.198.133:81"  # 基础URL
LOGIN_URL = f"{BASE_URL}/home/login/login_submit" # 登录URL
CAPTCHA_URL = f"{BASE_URL}/captcha.html?t={int(time() * 1000)}" # 验证码URL，带时间戳参数防止缓存
ADD_AND_EDIT_ACCOUNT_URL = f"{BASE_URL}/user/user/add" # 添加or修改账号
EDIT_PERSONAL = f"{BASE_URL}/home/index/edit_personal" # 编辑个人信息
DELETE_ACCOUNT_URL = f"{BASE_URL}/user/user/delete" # 删除账号
FILE_UPLOAD = f"{BASE_URL}/api/index/upload" # 文件上传
SUBMIT_CHECK = f"{BASE_URL}/api/check/submit_check" # 提交审核
APPROVE_URL = f"{BASE_URL}/api/check/flow_check" # 获取审核信息

#数据库配置
DB: Dict[str, str|int] = {
    "host" : "192.168.198.133",
    "port" : 3306,
    "user" : "root",
    "password" : "root",
    "database" : "oa"
}

#文件路径
HOME = Path(__file__).parent.parent