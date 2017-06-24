from random import randint
from copy import deepcopy

import requests
from flask import render_template, flash

from config import AuthSms


def send_sms(template, phone_num, **kwargs):
    send_data = deepcopy(AuthSms.sns_data)
    send_data["body"] = render_template(template+'.txt', **kwargs)
    send_data["recipientList"][0]["recipientNo"] = str(phone_num)
    res = requests.post(AuthSms.url, json=send_data)


def get_rand_num():
    return str(randint(0, 999999)).zfill(6)
