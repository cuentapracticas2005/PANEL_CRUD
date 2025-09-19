import database as db
from flask_login import UserMixin

''' Se crea clase que representa un usuario en el sistema.
    Se hereda lo que UserMixin agrega automaticamente:
    - is_authenticated: Indica si el usuario esta autenticado.
    - is_activate: Indica si el usuario esta activo.
    - is_anonymoues: Indica si el usuario es anonimo.
    - get_id(): Devuelve el identificador unico del usuario -> se usa self.id
    
    La clase la usara Flask-Login para gestionar:
    - Autenticacion (login/logout)
    - Recordar la sesion del usuario
    - Recuperar usuario en cada request
'''
class User(UserMixin):
    '''Se crea el constructor de la clase User.
    Parametros:
        - id_usuario: ID unico del usuario en la base de datos.
        - username: Nombre usado por el usuario para el login.
        - nombre_completo: (opcional)
        - rol: (trabajador por defecto)
    '''
    def __init__(self, id_usuario, username, nombre_completo=None, rol="trabajador"):
        self.id = id_usuario
        self.username = username
        self.nombre_completo = nombre_completo
        self.rol = rol

    
    @staticmethod
    def get_by_username(username):
        '''Se obtiene un usuario de la base de datos a partir del username.

        return: diccionario con:
            - 'user': instancia de User con los datos cargados
            - 'password_hash': hash de la contraseña para validacion
            En caso no se encuentre usuario o este inactivo se devuelve None        
        '''
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
        
        if user_data:
            return {
                'user': User(user_data[0], user_data[1], user_data[2], user_data[4]),
                'password_hash': user_data[3]
            }
        return None
    
    @staticmethod
    def get_by_id(user_id):
        '''Obtiene un usuario desde la base de datos a partir de su ID.
            Se usa en user_loader para poder mantener la sesion activa.

            return: Instancia de User si el usuario existe y esta activo, de lo contrario None.
        '''
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
            return User(user_data[0], user_data[1], user_data[2], user_data[3])
        return None
