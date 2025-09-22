from flask import Blueprint

models_bp = Blueprint('models', __name__)

from app.models import user