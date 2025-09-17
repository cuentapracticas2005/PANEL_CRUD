import database as db
from flask_login import UserMixin

# CLASE DE MODELO DE USUARIOS
class User(UserMixin):
    """
    Clase que representa un usuario en el sistema.
    UserMixin proporciona metodos por defecto de:
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()
    """
    def __init__(self, id_usuario, username, nombre_completo=None, rol="editor"):
        self.id = id_usuario  # Flask-Login usa 'id' por defecto
        self.username = username
        self.nombre_completo = nombre_completo
        self.rol = rol
    
    @staticmethod
    def get_by_username(username):
        """Buscar usuario por username en la base de datos"""
        cursor = db.database.cursor()
        cursor.execute("""
            SELECT id_usuario, username, nombre_completo, password_hash, rol
            FROM usuarios 
            WHERE username = %s AND activo = TRUE
        """, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data:
            return {
                'user': User(user_data[0], user_data[1], user_data[2], user_data[4]),
                'password_hash': user_data[3]
            }
        return None
    
    @staticmethod
    def get_by_id(user_id):
        """Buscar usuario por ID (usado por Flask-Login)"""
        cursor = db.database.cursor()
        cursor.execute("""
            SELECT id_usuario, username, nombre_completo, rol
            FROM usuarios 
            WHERE id_usuario = %s AND activo = TRUE
        """, (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3])
        return None
