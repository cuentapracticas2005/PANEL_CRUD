import os
from flask import current_app

"""
COMPROVACION DE PERMISOS EN CARPETAS:
- os.envirio.get('UPLOAD_FOLDER') -> buscamos en nuestras variables de entorno UPLOAD_FOLDER para obtener la ruta de la carpeta donde guardare los planos (sistema_gestion_h/.env)
- current_app.config.get('ALLOWED_EXTENSIONS', '....') -> obtiene os formatos permitidos de modulo configuracion de la app
FUNCIONES CREADAS EN ESTE MODULO:
    - ubi_archivos() -> verificacion de permisos y obtencion de la ruta donde ubicar planos
    - validar_archivos() -> valida que el archivo subido sea en formato pdf, png, jpg o jpeg
"""
def ubi_archivos():
    ubi_archivos = os.environ.get('UPLOAD_FOLDER')

    if not ubi_archivos:
        ubi_archivos = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'archivos_local')
        print(f"NO SE ENCONTRO UPLOAD_FOLDER EN RED, SE CREO CARPETA EN LOCAL")

    try:
        os.makedirs(ubi_archivos, exist_ok=True)
        # Verificar permisos de lectura
        try:
            os.listdir(ubi_archivos)
            print(f"LECTURA CORRECTA EN: {ubi_archivos}")
        except PermissionError as p:
            print(f"NO HAY PERMISOS DE LECTURA EN {ubi_archivos}, ERROR: {p}")
            raise
        # Verificar permisos de escritura
        try:
            test = os.path.join(ubi_archivos, 'test.tmp')
            with open(test, 'w') as t:
                t.write('hola')
            print(f"ESCRITURA CORRECTA EN: {ubi_archivos}")
            os.remove(test)
        except PermissionError as p:
            print(f"NO HAY PERMISOS DE ESCRITURA EN {ubi_archivos} ERROR: {p}")
            raise
    except Exception as p:
        print(f"ERROR {p}")
        raise

    return ubi_archivos

def validar_archivo(filename: str) -> bool:
    ALLOWED_EXTENSIONS = current_app.config.get('ALLOWED_EXTENSIONS', 
                                                {'pdf', 'png', 'jpg', 'jpeg'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS