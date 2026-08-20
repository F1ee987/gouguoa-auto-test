"""
@Project:gouguoa-auto-test
@File   :captcha_solver.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 14:10
"""

import re
import ddddocr
from utils.logger import Logger
from typing import Any

logger = Logger(__file__)


class CaptchaSolver:
    """验证码识别与计算器（仅支持加法算式）"""

    REPLACE_MAP = {
        '>': '7', 'q': '9', 'o': '0', ']': '1',
        'z': '2', 'I': '1', 'g': '9', '十': '+'
    }

    def __init__(self):
        self._ocr = ddddocr.DdddOcr(show_ad=False)

    def solve(self, img_path: str) -> int:
        """一键识别验证码并返回计算结果"""
        raw = self._recognize(img_path)
        cleaned = self._clean(raw)
        return self._calc(cleaned)

    def _recognize(self, img_path: str) -> Any:
        with open(img_path, 'rb') as f:
            text = self._ocr.classification(f.read())
        logger.info(f"OCR 识别结果: {text}")
        return text

    def _clean(self, raw: str) -> str:
        """数据清洗

        Args:
            raw (str): 待清洗的OCR识别结果

        Raises:
            ValueError: OCR 识别为空

        Returns:
            str: 清洗后的表达式
        """
        if not raw:
            raise ValueError("OCR 识别为空")
        cleaned = raw.translate(str.maketrans(self.REPLACE_MAP))
        cleaned = re.sub(r'\s+', '', cleaned)
        logger.info(f"清洗后表达式: {cleaned}")
        return cleaned

    def _calc(self, expr: str) -> int:
        """计算表达式结果（仅支持加法）"""
        # 找到 '+' 的位置
        idx = expr.find('+')
        if idx == -1:
            raise ValueError(f"表达式中未找到 '+' 号: {expr}")

        a = int(expr[:idx])
        b = int(expr[idx + 1:])

        # 特殊处理：OCR 把数字识别过大时的修正
        if a > 70:
            a -= 50
        if b > 70:
            b -= 50

        result = a + b
        if result > 40:
            logger.warning(f"计算结果 {result} 超出预期范围，可能存在识别偏差")

        logger.info(f"验证码计算结果: {a} + {b} = {result}")
        return result

if __name__ == '__main__':
    solve = CaptchaSolver()
    r = solve.solve('captcha_temp.png')

    print(r)