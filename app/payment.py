from copy import deepcopy

from flask import flash
from iamport import Iamport

from config import Payment


def simple_payment(amount, card_number, expiry, birth, pwd_2digit):
    send_data = deepcopy(Payment.payload)
    send_data['amount'] = amount
    send_data['card_number'] = card_number
    send_data['expiry'] = expiry
    send_data['birth'] = birth
    send_data['pwd_2digit'] = pwd_2digit
    try:
        response = Payment.iamport.pay_onetime(**send_data)
    except Iamport.ResponseError as e:
        flash(e.message)
        return None
    else:
        return response
