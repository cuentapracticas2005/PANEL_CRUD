from flask_login import UserMixin
import database as db

'''
Se usa la clase UserMixin el cual me da los parametros basicos para que mi objeto user funcione adecuadamente junto con Flask-Login
metodos incluidos:
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id
FUNCIONES CREADAS EN ESTE MODULO:
- get_by_username() -> Buscar usuario por username y lo entrega como un diccionario
- get_by_id() -> Buscar usuario por ID, esto permite que el usuario quede guardado cada ver que navege por el sistema
'''

class User(UserMixin):
    def __init__(self, id_usuario, username, nombre_completo=None, rol="trabajador"):
        self.id = id_usuario # PK en mi tabla planos
        self.username = username
        self.nombre_completo = nombre_completo # opcional(campo descriptivo)
        self.rol = rol

    @staticmethod
    def get_by_username(username):
        cursor = db.database.cursor()
        cursor.execute("""
            SELECT 
                u.id_user, 
                u.username, 
                u.nombre_completo, 
                u.password_hash, 
                r.rol
            FROM user u
            JOIN roles r ON u.id_rol = r.id_rol
            WHERE u.username = %s AND u.activo = TRUE
        """, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        
        # esta data se va a usar en la ruta login de auth, se envia como diccionario para acceder a el de manera mas agil
        if user_data:
            return {
                'user': User(user_data[0], user_data[1], user_data[2], user_data[4]),
                'password_hash': user_data[3]
            }
        return None
    
    @staticmethod
    def get_by_id(user_id):
        cursor = db.database.cursor()
        cursor.execute("""
            SELECT u.id_user, u.username, u.nombre_completo, r.rol
            FROM user u
            JOIN roles r ON u.id_rol = r.id_rol
            WHERE u.id_user = %s AND u.activo = TRUE
        """, (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3]) # devuelve objeto usuario con sus datos, para mantener la sesion iniciada
        return None