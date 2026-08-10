import ddddocr

def ocr_captcha_image(img_path: str) -> str:
    """orc识别验证码"""
    orc = ddddocr.DdddOcr(show_ad=False)
    with open(img_path, mode='rb') as f:
        img_bytes = f.read()
    captcha_text = orc.classification(img_bytes)
    return captcha_text

def calc_captcha(captcha_text: str) -> str:
    """根据识别的算式计算结果"""

if __name__ == '__main__':
    ocr_captcha_image('img_1.png')