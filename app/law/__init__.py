from flask import Blueprint

law = Blueprint('law', __name__)

from . import views, forms
