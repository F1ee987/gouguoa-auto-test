"""
@Project:gouguoa-auto-test
@File   :conf.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 13:27
"""
BASE_URL = "http://192.168.198.133:81"  # 基础URL
LOGIN_URL = f"{BASE_URL}/home/login/login_submit"
ADD_ACCOUNT_URL = f"{BASE_URL}/user/user/add_user"
LOGIN_TIP_LOC = ("XPASS", '//*[@id="layui-layer8"]')