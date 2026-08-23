"""
环境配置中心：集中管理 URL、数据库与文件路径。

约定：
- 所有 URL 基于 BASE_URL 拼接；
- 验证码接口 URL 通过 get_captcha_url() 动态生成（附带时间戳防缓存），
  不要在导入期缓存成一个固定常量，否则多次请求会命中同一张过期验证码；
- 敏感信息（如数据库密码）建议改用环境变量或 CI Secrets 注入。
"""
from pathlib import Path
from time import time
from typing import Dict

# ------------------------- 接口地址 -------------------------
BASE_URL = "http://192.168.198.133:81"                       # 系统基础地址
LOGIN_URL = f"{BASE_URL}/home/login/login_submit"            # 登录提交
ADD_AND_EDIT_ACCOUNT_URL = f"{BASE_URL}/user/user/add"       # 新增 / 修改账号
EDIT_PERSONAL = f"{BASE_URL}/home/index/edit_personal"       # 编辑个人信息
DELETE_ACCOUNT_URL = f"{BASE_URL}/user/user/delete"          # 删除账号
FILE_UPLOAD = f"{BASE_URL}/api/index/upload"                 # 文件上传
SUBMIT_CHECK = f"{BASE_URL}/api/check/submit_check"          # 提交审核（请假申请）
APPROVE_URL = f"{BASE_URL}/api/check/flow_check"             # 审批接口


def get_captcha_url() -> str:
    """构造验证码接口地址，每次调用都附带新的时间戳以防止缓存。"""
    return f"{BASE_URL}/captcha.html?t={int(time() * 1000)}"


# 兼容旧代码的常量形式（时间戳为加载时的快照，建议优先使用 get_captcha_url()）
CAPTCHA_URL = get_captcha_url()

# ------------------------- 数据库配置 -------------------------
DB: Dict[str, str | int] = {
    "host": "192.168.198.133",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "oa",
}

# ------------------------- 路径配置 -------------------------
# 项目根目录（config 的上一级）
HOME = Path(__file__).parent.parent
# 验证码图片运行期缓存目录
CAPTCHA_DIR = HOME / "api_test" / "data" / "captcha_data"
