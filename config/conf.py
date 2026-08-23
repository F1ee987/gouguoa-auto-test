"""
环境配置中心：集中管理 URL、数据库与文件路径。

配置来源（12-Factor / 企业实践）：
- 所有配置项优先读取环境变量，未设置时回退到默认值；
- 本地开发可将变量写入项目根目录的 `.env`（已被 .gitignore 忽略），
  并提交 `.env.example` 作为模板；
- 生产 / CI 环境通过流水线 Secrets 注入同名环境变量，仓库不含任何
  真实地址或数据库密码。

约定：
- 所有 URL 基于 BASE_URL 拼接；BASE_URL 统一去除结尾斜杠；
- 验证码接口 URL 通过 get_captcha_url() 动态生成（附带时间戳防缓存），
  不要在导入期缓存成固定常量，否则多次请求会命中同一张过期验证码；
- DB 连接信息同样来自环境变量，避免把数据库密码提交进仓库。
"""
from pathlib import Path
from time import time
from typing import Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """应用运行配置，全部从环境变量读取（前缀 GOUGUOA_）。

    字段即文档：变量名 = 前缀 + 字段名（大写）。
    例如 base_url 对应环境变量 GOUGUOA_BASE_URL。
    """

    model_config = SettingsConfigDict(
        env_prefix="GOUGUOA_",
        env_file=".env",            # 本地开发用，不存在也不报错
        env_file_encoding="utf-8",
        extra="ignore",             # 忽略无关环境变量，避免误报
    )

    # 系统基础地址（不含结尾斜杠）
    base_url: str = "http://192.168.198.133:81"

    # 数据库配置
    db_host: str = "192.168.198.133"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "root"
    db_name: str = "oa"


# 全局唯一配置实例；导入本模块即完成环境变量加载与校验
settings = AppSettings()

# ------------------------- 接口地址 -------------------------
BASE_URL = settings.base_url.rstrip("/")                       # 系统基础地址
LOGIN_URL = f"{BASE_URL}/home/login/login_submit"              # 登录提交
ADD_AND_EDIT_ACCOUNT_URL = f"{BASE_URL}/user/user/add"         # 新增 / 修改账号
EDIT_PERSONAL = f"{BASE_URL}/home/index/edit_personal"         # 编辑个人信息
DELETE_ACCOUNT_URL = f"{BASE_URL}/user/user/delete"            # 删除账号
FILE_UPLOAD = f"{BASE_URL}/api/index/upload"                   # 文件上传
SUBMIT_CHECK = f"{BASE_URL}/api/check/submit_check"            # 提交审核（请假申请）
APPROVE_URL = f"{BASE_URL}/api/check/flow_check"               # 审批接口


def get_captcha_url() -> str:
    """构造验证码接口地址，每次调用都附带新的时间戳以防止缓存。"""
    return f"{BASE_URL}/captcha.html?t={int(time() * 1000)}"


# 兼容旧代码的常量形式（时间戳为加载时的快照，建议优先使用 get_captcha_url()）
CAPTCHA_URL = get_captcha_url()

# ------------------------- 数据库配置 -------------------------
# 由环境变量驱动，结构与原有 DB 字典保持一致，下游调用方无需改动
DB: Dict[str, str | int] = {
    "host": settings.db_host,
    "port": settings.db_port,
    "user": settings.db_user,
    "password": settings.db_password,
    "database": settings.db_name,
}

# ------------------------- 路径配置 -------------------------
# 项目根目录（config 的上一级）
HOME = Path(__file__).parent.parent
# 验证码图片运行期缓存目录
CAPTCHA_DIR = HOME / "api_test" / "data" / "captcha_data"
