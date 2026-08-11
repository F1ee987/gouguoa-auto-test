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
    return captcha_text

def calc_captcha(captcha_text: str) -> int:
    """根据识别的算式计算结果 v1版本"""
    from re import sub
    is_num = 0
    cleaned = sub(r'\s+', '',captcha_text)
    for c in cleaned:
        if c not in string.digits:
            break
        is_num += 1
    num1, num2 = int(cleaned[:is_num]), int(cleaned[is_num+1:])
    return num1 + num2

if __name__ == '__main__':
    r = ocr_captcha_image('img.png')
    s = "30 + 4"
    print(r)