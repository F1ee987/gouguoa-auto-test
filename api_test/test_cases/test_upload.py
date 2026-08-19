"""
@Project:gouguoa-auto-test
@File   :test_upload.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/18 14:58
"""
import pytest
from config.conf import FILE_UPLOAD, HOME
from utils import Reader

def load_upload_test_data():
    """读取上传文件的csv文件"""
    print("开始读取上传文件的csv文件")
    r = Reader()
    filepath = f'{HOME}/api_test/data/upload_data.csv'
    print(f'读取文件路径：{filepath}')
    result = r.read_csv(filepath)
    if not result:
        pytest.skip("上传文件的csv文件不存在")
    data = []
    for row in result[1:]:
        if len(row) < 3:
            print(f"⚠ 跳过字段不完整的数据行：{row}")
            continue

        data.append((row[0], row[1], row[2]))
        print(f"✅ 加载测试数据：{row}")

    if not data:
        pytest.skip("没有有效的测试数据")

    return data

@pytest.mark.parametrize("filetype, path, expected", load_upload_test_data())
def test_upload(filetype, path, expected, admin_api_login, logger):
    with open(f'{str(HOME)+path}', 'rb') as f:
        upload_res = admin_api_login.post(
            FILE_UPLOAD,
            files={'file': f}
        )
    assert upload_res.status_code == 200
    try:
        upload_json = upload_res.json()
    except ValueError:
        pytest.fail(f"响应不是有效的JSON: {upload_res.text}")

    code = upload_json.get('code')
    msg = upload_json.get('msg', '')
    assert str(code) == expected, f'上传失败, 当前状态：{msg}'
    logger.info(f"✅ 上传文件成功，状态码：{code}, 消息：{msg}")