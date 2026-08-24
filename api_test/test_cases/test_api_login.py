"""
登录接口测试：通过 OCR 识别验证码并完成登录，校验返回 code 与用例预期一致。

数据来源：config/accounts.csv（由 prepare_account 解析为参数化数据）。
预期约定：expected_code=0 表示登录成功，=1 表示登录失败（禁用/密码错/空用户名等）。
"""
import pytest
import shutil
from datetime import datetime
from config.conf import CAPTCHA_DIR
from utils import (
    Logger,
    RequestHandle,
    delete_cache,
    fetch_captcha,
    prepare_account,
    solve_captcha,
    submit_login,
)
from api_test.helpers.response import assert_api_success
import allure

TEST_DATA, TEST_IDS = prepare_account()

@allure.feature("登录接口")
@allure.severity("critical")
@pytest.mark.api
@pytest.mark.login
@pytest.mark.parametrize("username,password,expected_code", TEST_DATA, ids=TEST_IDS)
def test_login_with_ocr_captcha(username: str, password: str, expected_code: str, logger: Logger):
    """OCR 解码验证码并登录，校验业务返回码与预期一致。"""
    session = RequestHandle(use_session=True)
    image_path = str(CAPTCHA_DIR / f"captcha_{username}.png")

    try:
        with allure.step("获取验证码"):
            # 1. 下载并识别验证码
            fetch_captcha(session, image_path)
            try:
                captcha_value = solve_captcha(image_path)
            except Exception:
                shutil.copy2(image_path, f"api_error_{username}_captcha_{datetime.now().strftime('%Y%m%d%-H%M%S')}.png")
                raise Exception("验证码识别失败，无法执行登录操作。")
            logger.info(f"OCR 解码验证码: {captcha_value}")

        # 2. 提交登录
        with allure.step("提交登录"):
            response = submit_login(session, username, password, captcha_value)
            with allure.step("断言接口业务返回符合预期"):
                body = assert_api_success(response, int(expected_code),context=f"用户名={username}")

        # 3. 校验业务返回码与用例预期一致
        with allure.step("校验业务返回码"):
            assert str(body.get('code')) == str(expected_code), \
                f"预期 code={expected_code}，实际 code={body.get('code')}, msg={body.get('msg')}"
            logger.info(
                f"✅ 登录结果符合预期 | 用户名={username} | 预期 code={expected_code} | 实际 code={body.get('code')} | msg={body.get('msg')}"
            )
    finally:
        with allure.step("清理资源"):
            delete_cache(image_path)
            session.close()