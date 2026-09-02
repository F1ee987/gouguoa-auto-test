"""
验证码识别与计算工具（仅支持「加法算式」类型验证码）。

处理流程：
    读取验证码图片 -> ddddocr 识别原始文本 -> 字符清洗/纠错 -> 解析加法表达式 -> 求和。

由于 OCR 对部分字符识别不稳定，内置了常见误识别映射 CHAR_CORRECTION_MAP 做纠正；
当两个加数被识别得过大时，按经验做偏移修正。
"""
from datetime import datetime
from pathlib import Path
import re
import ddddocr
from typing import Any, Optional
from utils.logger import Logger
from config.conf import PROJECT_ROOT

logger = Logger(__name__)


class CaptchaSolver:
    """验证码识别与计算器（仅支持加法算式）。"""

    # OCR 引擎在所有实例间共享：模型只需加载一次，
    # 否则每条用例实例化一次就重新加载一遍模型，白白拖慢登录。
    _shared_ocr = None

    # OCR 常见误识别字符 -> 正确字符 的纠正映射
    CHAR_CORRECTION_MAP = {
        '>': '7', 'q': '9', 'o': '0', ']': '1', '之': '7',
        'z': '2', 'I': '1', 'g': '9', '十': '+', '了': '7',
        # 括号类常被误当成 0/1：如 "30+5" 被识别成 "3)+5"
        ')': '0', '(': '0', '[': '1', '{': '1', '}': '1',
        'l': '1', 'i': '1', '|': '1', 'S': '5', 's': '5',
        'B': '8', 'b': '6', 'A': '4', 'D': '0', 'O': '0',
    }

    # 合法加法表达式（a+b，加数最多两位）
    _ADDITION_PATTERN = re.compile(r'^(\d{1,2})\+(\d{1,2})$')

    # 算式中单个加数的经验上限，超过则视为 OCR 把数字识别过大并做修正
    ADDEND_UPPER_BOUND = 70
    # 计算结果的经验上限，超过则预警可能存在识别偏差
    RESULT_UPPER_BOUND = 40

    def __init__(self):
        if CaptchaSolver._shared_ocr is None:
            CaptchaSolver._shared_ocr = ddddocr.DdddOcr(show_ad=False)
        self._ocr = CaptchaSolver._shared_ocr

    def solve(self, image_path: str) -> int:
        """识别验证码图片并返回算式计算结果。

        Args:
            image_path: 验证码图片的本地路径。
        Returns:
            算式求和后的整数结果。
        """
        with open(image_path, 'rb') as fp:
            image_bytes = fp.read()
        raw_text = self._recognize(image_bytes)
        expression = self._normalize_expression(raw_text)
        return self._evaluate_addition(expression, image_bytes)

    def _recognize(self, image_bytes: bytes) -> Any:
        """调用 ddddocr 识别图片，返回原始文本。"""
        text = self._ocr.classification(image_bytes)
        logger.info(f"OCR 识别结果: {text}")
        return text

    def _normalize_expression(self, raw_text: str) -> str:
        """清洗并纠偏 OCR 文本，得到可用的加法表达式。

        Args:
            raw_text: OCR 原始识别文本。
        Raises:
            ValueError: 识别结果为空。
        Returns:
            去除空白、完成字符纠偏后的表达式字符串。
        """
        if not raw_text:
            raise ValueError("❌ OCR 识别结果为空，无法解析验证码")
        # 1) 纠正常见误识别字符（如把 ')' 当作 '0'）
        corrected = raw_text.translate(str.maketrans(self.CHAR_CORRECTION_MAP))
        # 2) 去除所有空白字符
        expression = re.sub(r'\s+', '', corrected)
        # 3) 丢弃剩余无法参与计算的杂点符号，避免直接解析崩溃
        expression = re.sub(r'[^0-9+]', '', expression)
        return expression

    def _evaluate_addition(self, expression: str, image_bytes: Optional[bytes] = None) -> int:
        """计算加法表达式结果（仅支持 a+b 形式）。

        Args:
            expression: 清洗后的表达式，形如 "12+34"。
            image_bytes: 原始图片字节，识别异常时用于转储排查。
        Raises:
            ValueError: 表达式不是合法的 a+b 形式。
        """
        matched = self._ADDITION_PATTERN.match(expression)
        if not matched:
            self._dump_error_image(expression, image_bytes)
            raise ValueError(f"❌ 无法解析加法表达式: {expression}")

        left = int(matched.group(1))
        right = int(matched.group(2))

        # OCR 偶尔会把数字识别得过大（如把 12 识别成 62），做经验修正
        if left > self.ADDEND_UPPER_BOUND:
            left -= 50
        if right > self.ADDEND_UPPER_BOUND:
            right -= 50

        calc_result = left + right
        if calc_result > self.RESULT_UPPER_BOUND:
            logger.warning(f"❌ 计算结果 {calc_result} 超出预期范围，可能存在识别偏差")
            self._dump_error_image(expression, image_bytes)

        return calc_result

    @staticmethod
    def _dump_error_image(expression: str, image_bytes: Optional[bytes]) -> None:
        """识别异常时把原始图片转储到 docs/ 便于人工排查。

        修复说明：早期实现误把文件路径字符串写入图片文件（文本模式），
        这里改为写入真实的图片字节。
        """
        if not image_bytes:
            return
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        error_path = Path(PROJECT_ROOT) / 'docs' / f'error_captcha_{timestamp}.png'
        error_path.parent.mkdir(parents=True, exist_ok=True)
        error_path.write_bytes(image_bytes)
        logger.error(f"❌ 验证码解析异常，已保存原始图片至: {error_path} (表达式: {expression})")


if __name__ == '__main__':
    solver = CaptchaSolver()
    result = solver.solve('captcha_temp.png')
    print(result)
