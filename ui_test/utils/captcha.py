"""
@Project:gouguoa-auto-test
@File   :captcha.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 14:10
"""

import ddddocr
import string

def ocr_captcha_image(img_path: str) -> str:
    """orc识别验证码"""
    orc = ddddocr.DdddOcr(show_ad=False)
    with open(img_path, mode='rb') as f:
        img_bytes = f.read()
    captcha_text = orc.classification(img_bytes)
    print(f"识别内容>>{captcha_text}")
    return captcha_text

def calc_captcha(captcha_text: str) -> int:
    """根据识别的算式计算结果 v3版本"""
    from re import sub
    replace_map = {
        '>': '7',
        'q': '9',
        'o': '0',
        ']': '1'
    }
    first_num_len = 0
    for old, new in replace_map.items():
        text = captcha_text.replace(old, new)
    cleaned = sub(r'\s+', '', text)
    for c in cleaned:
        if c not in string.digits:
            break
        first_num_len += 1
    num1, num2 = int(cleaned[:first_num_len]), int(cleaned[first_num_len+1:])
    return num1 + num2

if __name__ == '__main__':
    r = ocr_captcha_image('img.png')
    print(calc_captcha(r))