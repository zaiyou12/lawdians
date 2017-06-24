from copy import deepcopy

import requests
from flask import flash, render_template

from config import AuthEmail


def send_email(template, email, **kwargs):
    send_data = deepcopy(AuthEmail.email_data)
    send_data["body"] = render_template(template + '.txt', **kwargs)
    send_data["receiverList"][0]["receiveMailAddr"] = email
    res = requests.post(AuthEmail.url, json=send_data)
