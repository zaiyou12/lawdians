from flask import Blueprint

hos = Blueprint('hos', __name__)

from . import views