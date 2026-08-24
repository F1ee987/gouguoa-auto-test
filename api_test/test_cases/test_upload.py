"""
文件上传接口测试。

用例数据来自 api_test/data/upload_data.csv：
    file_type, path, expected_result, description
其中 path 为相对于项目根目录的文件路径；expected_result 为期望的接口返回 code。
"""
import allure
import pytest
from pathlib import Path
from config.conf import FILE_UPLOAD, PROJECT_ROOT, FILE_DELETE
from utils import Logger, RequestHandle, delete_cache, load_parametrized_csv
from api_test.helpers import assert_api_success, assert_http_ok

UPLOAD_DIR = Path(PROJECT_ROOT) / "api_test" / "data" / "upload_data"
UPLOAD_CSV = Path(PROJECT_ROOT) / "api_test" / "data" / "upload_data.csv"


def _ensure_dummy_files() -> None:
    """保证上传测试所需的占位文件存在（缺失时创建空文件，便于全新环境运行）。"""
    for ext in (".csv", ".txt", ".pdf"):
        target = UPLOAD_DIR / f"upload{ext}"
        if not target.exists():
            target.write_text(f"filetype={ext}", encoding="utf-8")


_ensure_dummy_files()

TEST_DATA, TEST_IDS = load_parametrized_csv(
    UPLOAD_CSV, data_columns=[0, 1, 2], id_column=3, min_fields=4
)

@allure.story("文件上传接口测试")
@allure.step("上传文件 {file_type}")
@pytest.mark.upload
@pytest.mark.parametrize("file_type, relative_path, expected_code", TEST_DATA, ids=TEST_IDS)
def test_upload_and_delete(
        file_type: str, relative_path: str, expected_code: str,
        admin_api_login: RequestHandle, logger: Logger,
):
    # --- 上传 ---
    with allure.step(f"上传文件 {file_type}"):
        file_path = str(PROJECT_ROOT) + relative_path
        with open(file_path, "rb") as fp:
            response = admin_api_login.post(FILE_UPLOAD, files={"file": fp})

        assert_http_ok(response)
        try:
            body = response.json()
        except ValueError:
            pytest.fail(f"❌ 响应不是有效的 JSON: {response.text}")

    actual_code = str(body.get("code"))

    try:
        with allure.step("断言上传结果"):
            assert actual_code == str(expected_code), \
                f"预期结果：{expected_code}, 实际结果：{actual_code}, 消息：{body.get('msg')}"

        # 上传成功后执行删除
        if actual_code == "0":
            file_id = body["data"]["id"]
            logger.info(f"✅ 上传成功，类型={file_type}，ID={file_id} | 消息：{body.get('msg')}")

            with allure.step("删除上传的文件"):
                del_response = admin_api_login.delete(FILE_DELETE, params={'ids': file_id})
                # 使用 try-except 单独处理删除断言，避免与上传异常混淆
                try:
                    assert_api_success(del_response, expected_msg="操作成功")
                    logger.info(f"✅ 删除成功，ID={file_id}")
                except AssertionError as e:
                    logger.error(f"❌ 删除失败，ID={file_id}，错误：{e}")
                    raise  # 可根据需求选择是否中断测试
        else:
            logger.info(f"✅ 预期文件上传失败测试通过 | 类型={file_type} | code={actual_code} | 消息：{body.get('msg')}")

    except AssertionError as e:
        logger.error(f"❌ 文件上传失败 | 类型={file_type} | {e}")
        raise

    finally:
        with allure.step("清理本地上传测试文件（保留 png 素材）"):
            if not relative_path.endswith(".png"):
                delete_cache(file_path)