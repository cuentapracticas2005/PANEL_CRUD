from flask import Flask
from dotenv import load_dotenv
import os

def create_app(config_name=None):
    load_dotenv()

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    print(f"Usando configuración: {config_name}")
    
    app = Flask(__name__)
    
    # Configuración
    from app.config import config # traemos app/config 
    app.config.from_object(config[config_name])# cargar las configuracion a Flask

    
    # Inicializar extensiones
    from app.extensions import login_manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # ruta donde redirigir si no esta autenticado
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    # Registrar Blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.planos import planos_bp
    from app.archivos import archivos_bp
    from app.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(planos_bp, url_prefix='/planos')
    app.register_blueprint(archivos_bp, url_prefix='/files')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Callback para cargar usuario
    from app.extensions import login_manager
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))
    
    return app