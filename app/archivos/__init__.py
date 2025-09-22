from flask import Blueprint

archivos_bp = Blueprint('archivos', __name__)

from app.archivos import routes