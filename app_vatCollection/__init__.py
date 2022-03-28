from flask import Blueprint

vatCollection = Blueprint('vatCollection', __name__)


from . import view_vatCollection, function_vatCollection
