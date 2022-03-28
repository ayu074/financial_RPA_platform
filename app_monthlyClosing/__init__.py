from flask import Blueprint

monthlyClosing = Blueprint('monthlyClosing', __name__)

from . import view_monthlyClosing, function_monthlyClosing

