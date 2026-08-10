"""
@Project:gouguoa-auto-test
@File   :run.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/9 14:08
"""
import requests
from time import time
import random

session = requests.Session()
possible_values = list(range(10, 40))
random.shuffle(possible_values)
i = []
for answer in possible_values:
    login_data = {
        'username': "zhangsan",
        'password': '123456',
        'captcha': str(answer)
    }
    session.get(f"http://192.168.198.129:81/captcha.html?t={int(time()*1000)}")
    res = session.post(url="http://192.168.198.129:81/home/login/login_submit", data=login_data)
    print(res.json())
    if "验证码不正确" in res.json().get('msg'):
        print(f"当前答案>>{answer}")
        i.append(answer)
        continue
    else:
        break
print(sorted(i))