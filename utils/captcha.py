"""
@Project:gouguoa-auto-test
@File   :captcha.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 14:10
"""

import ddddocr
import string
from utils.logger import Logger

logger = Logger(__file__)

class CaptchaSolver:
    """
    验证码识别与计算器
    集成 OCR 识别、字符清洗、算式计算功能
    """
    @staticmethod
    def ocr_captcha_image(img_path: str) -> str:
        """orc识别验证码"""
        orc = ddddocr.DdddOcr(show_ad=False)
        with open(img_path, mode='rb') as f:
            img_bytes = f.read()
        captcha_text = orc.classification(img_bytes)
        print(f"识别内容：{captcha_text}")
        return captcha_text

    @staticmethod
    def clean_captcha_text(raw_text: str) -> str:
        """
        清洗 OCR 识别后的验证码文本：
        - 替换常见混淆字符（数字、运算符）
        - 移除所有空白字符
        - 返回可用于计算的干净表达式
        """
        if not raw_text:
            return ""
        from re import sub
        replace_map = {
            '>': '7',
            'q': '9',
            'o': '0',
            ']': '1',
            'z': '2',
            'I': '1',
            'g': '9',
            '十': '+'
        }
        trans_table = str.maketrans(replace_map)
        text = raw_text.translate(trans_table)
        cleaned = sub(r'\s+', '', text)
        print(f"清洗结果>>{cleaned}")
        return cleaned

    @staticmethod
    def calc_captcha(cleaned: str) -> int:
        """根据识别的算式计算结果 v4版本"""
        first_num_len = 0
        for c in cleaned:
            if c not in string.digits:
                break
            first_num_len += 1
        first_operand, second_operand = int(cleaned[:first_num_len]), int(cleaned[first_num_len+1:])
        result = first_operand + second_operand
        if result > 40:
            logger.warning('ValueError("⚠️计算结果超出验证码范围")')
        logger.info("验证码识别成功")
        return result

if __name__ == '__main__':
    solve = CaptchaSolver()
    r = solve.ocr_captcha_image('captcha_temp.png')

    print(solve.calc_captcha(solve.clean_captcha_text(r)))