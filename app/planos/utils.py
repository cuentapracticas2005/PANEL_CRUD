import database as db


def obtener_tipo_plano(cod_tipo_plano):
    cursor = db.database.cursor()
    cursor.execute("SELECT id_tipo_plano FROM tipo_plano WHERE cod_tipo_plano = %s", 
                  (cod_tipo_plano,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def obtener_siguiente_numero():
    cursor = db.database.cursor()
    cursor.execute("INSERT INTO num_plano (id_num_plano) VALUES (NULL)")
    db.database.commit()
    id_num_plano = cursor.lastrowid
    cursor.close()
    return id_num_plano

def obtener_tamanio(tamanio):
    cursor = db.database.cursor()
    cursor.execute("SELECT id_tamanio FROM tamanio WHERE tamanio = %s", (tamanio,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def obtener_revision(revision):
    cursor = db.database.cursor()
    cursor.execute("SELECT id_revision FROM revision WHERE revision = %s", (revision,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def obtener_sub_revision(sub_revision):
    cursor = db.database.cursor()
    cursor.execute("SELECT id_sub_revision FROM sub_revision WHERE sub_revision = %s", 
                  (sub_revision,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def guardar_archivo_info(archivo_nombre, archivo_path, archivo_mime, archivo_token):
    cursor = db.database.cursor()
    cursor.execute("""INSERT INTO archivos (archivo_nombre, archivo_path, archivo_mime, archivo_token)
                    VALUES (%s,%s,%s,%s)""",
                  (archivo_nombre, archivo_path, archivo_mime, archivo_token))
    db.database.commit()
    id_archivo = cursor.lastrowid
    cursor.close()
    return id_archivo

def generar_identificador_plano(cod_tipo_plano, num_plano, tamanio, revision, sub_revision):
    identificador = f"{cod_tipo_plano}-{num_plano}-{tamanio}{revision}"
    if sub_revision and sub_revision != '0':
        identificador += str(sub_revision)
    return identificador