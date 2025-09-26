import os
"""
SE CREA UNA CLASE LA CUAL LA HEREDAN LAS DOS QUE SIGUEN, EN EL CONFIG PADRE TENEMOS:
    - SECRET_KEY -> obtiene la secret key de .env, en caso no encuentre usa 'para-desarrollo'
    - UPLOAD_FOLDER -> de igual manera obtine la ruta de .env
    - ALLOWED_EXTENSIONS -> extensiones permitidas
"""
class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'para-desarrollo')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}













