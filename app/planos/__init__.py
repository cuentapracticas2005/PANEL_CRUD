from flask import Blueprint

planos_bp = Blueprint('planos', __name__, template_folder='templates')

from app.planos import routes