"""
@Project:gouguoa-auto-test
@File   :conf.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 13:27
"""
from pathlib import Path

#URL信息
BASE_URL = "http://192.168.198.133:81"  # 基础URL
LOGIN_URL = f"{BASE_URL}/home/login/login_submit"
ADD_ACCOUNT_URL = f"{BASE_URL}/user/user/add"
LOGIN_TIP_LOC = ("XPASS", '//*[@id="layui-layer8"]')
EDIT_PERSONAL = f"{BASE_URL}/home/index/edit_personal"
FILE_UPLOAD = f"{BASE_URL}/api/index/upload"

#数据库配置
DB = {
    "host" : "192.168.198.133",
    "port" : 3306,
    "user" : "root",
    "password" : "root",
    "database" : "oa"
}

#文件路径
HOME = Path(__file__).parent.parent