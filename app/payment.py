from copy import deepcopy

from flask import flash
from iamport import Iamport

from app import db
from .models import Point
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
        flash("code: " + e.code)
        flash("message: " + e.message)
        return None
    else:
        return response


def is_payment_completed(current_user, imp_uid, product_price, body):
    iamport = Payment.iamport

    point = Point(user_id=current_user.id, point=product_price, body=body)
    db.session.add(point)
    db.session.commit()

    '''   
        if iamport.is_paid(product_price, imp_uid=imp_uid):
            point = Point(user_id=current_user.id, point=product_price, body=body)
            db.session.add(point)
            db.session.commit()
            # TODO: add payment to RecommendBonus Table
            return True
        else:
            return False
    '''

    return True

