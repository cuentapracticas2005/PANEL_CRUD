from flask import Flask, request, render_template, redirect, url_for, abort, send_from_directory
import os
from dotenv import load_dotenv
import database as db
from werkzeug.utils import secure_filename
import uuid
load_dotenv()

app = Flask(
    __name__,
    static_folder = os.path.join(os.path.dirname(__file__),'static'),
    template_folder = os.path.join(os.path.dirname(__file__),'templates')
)
# ======================= CONFIGURACION DE SUBIDA DE ARCHIVOS =======================
def comprobar_archivos():
    ubi_archivos = os.environ.get('UPLOAD_FOLDER')

    if not ubi_archivos:
        ubi_archivos = os.path.join(os.path.dirname(__file__),'archivos_local')
        print(f"NO SE ENCONTRO UPLOAD_FOLDER EN RED, SE CREO CARPETA EN LOCAL")

    try:
        os.makedirs(ubi_archivos, exist_ok=True)
        try:
            os.listdir(ubi_archivos)
            print(f"✅LECTURA CONRRECTA EN: {ubi_archivos}")
        except PermissionError as p:
            print(f"❌NO HAY PERMISOS DE LECTURA EN {ubi_archivos}, ERROR: {p}")
            raise        
        try:
            test = os.path.join(ubi_archivos,'test.tmp')
            with open(test, 'w') as t:
                t.write('hola')
            print(f"✅ECRITURA CORRECTA EN: {ubi_archivos}")
            os.remove(test)
        except PermissionError as p:
            print(f"❌NO HAY PERMISOS DE ESCRITURA EN {ubi_archivos} ERROR: {p}")
            raise
    except Exception as p:
        print(f"ERROR {p}")
        raise

    return ubi_archivos

UBI_ARCHIVO = comprobar_archivos()
ALL_EXTENSIONS = {"pdf","png","jpg","jpeg"}

def validar_archivo(filename: str)->bool:
    valor = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALL_EXTENSIONS
    return valor

# ======== FUNCIONES PARA EL MANEJO DE TABLAS RELACIONADAS ==========
def obtener_tipo_plano(cod_tipo_plano):
    cursor = db.database.cursor()
    cursor.execute("SELECT id_tipo_plano FROM tipo_plano WHERE cod_tipo_plano = %s", (cod_tipo_plano))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def obtener_siguiente_numero():
    cursor = db.database.cursor()
    cursor.execute("INSERT INTO num_plano (num_plano) VALUES (NULL)")
    db.database.commit()
    id_num_plano = cursor.lastrowid

    cursor.execute("SELECT num_plano FROM num_plano WHERE id_num_plano = %s", (id_num_plano))
    num_plano = cursor.fetchone()

    cursor.close()
    return id_num_plano, num_plano

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
    cursor.execute("SELECT id_sub_revision FROM sub_revision WHERE sub_revision = %s", (sub_revision))
    result = cursor.fetchone()
    return result[0] if result else None

def guardar_archivo_info(archivo_nombre, archivo_path, archivo_mime, archivo_token):
    cursor = db.database.cursor()
    cursor.execute("""INSERT INTO archivos (archivo_nombre, archivo_path, archivo_mime, archivo_token)
                    VALUES (%s,%s,%s,%s)""",
                    (archivo_nombre, archivo_path, archivo_mime, archivo_token))
    db.database.commit()
    id_archivo = cursor.lastrowid
    return id_archivo

def generar_identificador_plano(cod_tipo_plano, num_plano, tamanio, revision, sub_revision):
    identificador = f"{cod_tipo_plano}-{num_plano}-{tamanio}{revision}"
    if sub_revision and sub_revision !='0':
        identificador += str(sub_revision)
    return identificador

# ==================== RUTAS DE LA APP ============================

@app.route('/')
def home():
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    identificador = request.form.get('identificador_plano','').strip()
    dibujante = request.form.get('dibujante','').strip()

    query = """
        SELECT 
            p.id_plano,
            p.identificador_plano,
            p.descripcion,
            p.dibujante,
            p.fecha,
            tp.tipo_plano,
            tp.cod_tipo_plano,
            np.numero_plano,
            t.tamanio,
            r.revision,
            sr.sub_revision,
            a.archivo_nombre,
            a.archivo_token
        FROM planos p
        LEFT JOIN tipo_plano tp ON p.id_tipo_plano = tp.id_tipo_plano
        LEFT JOIN num_plano np ON p.id_num_plano = np.id_num_plano
        LEFT JOIN tamanio t ON p.id_tamio = t.id_tamanio
        LEFT JOIN revision r ON p.revision = r.id_revision
        LEFT JOIN sub_revision sr ON p.id_sub_revision = sr.id_sub_revision
        LEFT JOIN archivos a ON p.id_archivo = a.id_archivo
        WHERE 1=1
    """
    params = []

    if fecha:
        query += " AND p.fecha = %s"
        params.append(fecha)
    if descripcion:
        query += " AND p.descripcion LIKE %s"
        params.append(f"%{descripcion}%")
    if identificador:
        query += " AND identificador_plano LIKE %s"
        params.append(f"%{identificador}%")
    if dibujante:
        query += " AND dibujante LIKE %s"
        params.append(f"%{dibujante}%")

    query += " ORDER BY p.id_plano DESC"
    cursor = db.database.cursor()
    cursor.execute(query, tuple(params))
    tuplas = cursor.fetchall()

    nameColums = []
    for x in cursor.description:
        nameColums.append(x[0])
    
    union = []
    for x in tuplas:
        union.append(dict(zip(nameColums, x)))

    cursor.close()
    return render_template('index.html', data=union)

# RUTA PARA GUARDAR DATOS
@app.route('user', methods=['POST'])
def addUser():
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    cod_tipo_plano = request.form.get('tipo_plano','').strip()
    tamanio = request.form.get('tamanio','').strip()
    revision = request.form.get('revision','').strip()
    sub_revision = request.form.get('sub_revision','').strip()
    dibujante = request.form.get('dibujante','').strip()

    print(f"DATOS RECIBIDOS: ")
    print(f"fecha: {fecha}")
    print(f"descripcion: {descripcion}")
    print(f"tipo_plano: {cod_tipo_plano}")
    print(f"tamanio: {tamanio}")
    print(f"revision: {revision}")
    print(f"sub_revision: {sub_revision}")
    print(f"dibujante: {dibujante}")

    if not all([fecha, descripcion, cod_tipo_plano, tamanio, revision, dibujante]):
        print("Faltan datos")
        return redirect(url_for('home'))
    
    id_tipo_plano = obtener_tipo_plano(cod_tipo_plano)
    id_num_plano, num_plano = obtener_siguiente_numero()
    id_tamanio = obtener_tamanio(tamanio)
    id_revision = obtener_revision(revision)
    id_sub_revision = obtener_sub_revision(sub_revision) if sub_revision else None

    identificador_plano = generar_identificador_plano(cod_tipo_plano, num_plano, tamanio, revision, sub_revision)
    
    archivo_name = None
    archivo_path = None
    archivo_mime = None
    archivo_token = None
    id_archivo = None
    file = None
    
    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file = request.files['imagen']

    # Validacion de archivo
    if file and file.filename and validar_archivo(file.filename):
        nombre_original = secure_filename(file.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        ruta_archivo = f"{uuid.uuid4().hex}.{extension}"
        ubicacion = os.path.join(UBI_ARCHIVO, ruta_archivo)
        file.save(ubicacion)

        if extension == 'pdf':
            mime = 'application/pdf'
        elif extension in ('png', 'jpg', 'jpeg'):
            mime = 'image/jpeg' if extension in ('jpg', 'jpeg') else f"image/{extension}"

        archivo_name = nombre_original
        archivo_path = ruta_archivo
        archivo_token = uuid.uuid4().hex
        archivo_mime = mime

        id_archivo = guardar_archivo_info(archivo_name, archivo_path, archivo_mime, archivo_token)

    cursor = db.database.cursor()
    sql = """INSERT INTO planos
            (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano, id_tipo_plano,
             id_num_plano, id_tamanio, id_revision, id_sub_revision, id_archivo)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    data = (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano,
            id_num_plano, id_tamanio, id_revision, id_sub_revision, id_archivo)
    
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    print(f"Plano e identificador insertado en la base de datos correctamente: {identificador_plano}")
    return redirect(url_for('home'))
    
# RUTA PARA ACTUALIZAR DATOS
@app.route('/edit/<string:id_plano>', methods=['POST'])
def edit(id_plano):
    fecha = request.form.get('fecha', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    cod_tipo_plano = request.form.get('tipo_plano', '').strip()
    tamanio = request.form.get('tamanio', '').strip()
    revision = request.form.get('revision', '').strip()
    sub_revision = request.form.get('sub_revision', '').strip()
    dibujante = request.form.get('dibujante', '').strip()

    print(f"DATOS RECIBIDOS PARA ACTUALIZAR: ")
    print(f"ID Plano: {id_plano}")
    print(f"Fecha: {fecha}")
    print(f"Descripcion: {descripcion}")
    print(f"Tipo de plano: {cod_tipo_plano}")
    print(f"Codigo tipo: {cod_tipo_plano}")
    print(f"Tamaño: {tamanio}")
    print(f"Revision: {revision}")
    print(f"Sub revision: {sub_revision}")
    print(f"Dibujante: {dibujante}")

    cursor = db.database.cursor()
    cursor.execute("""SELECT np.num_plano, p.id_num_plano, p.id_archivo
                   FROM planos p
                   JOIN num_plano np ON p.id_num_plano = np.id_num_plano
                   WHERE p.id_plano = %s""", (id_plano, ))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        print("Plano no encontrado")
        return redirect(url_for('home'))
    
    num_plano_actual = result[0]
    id_num_plano_actual = result[1]
    id_archivo_actual = result[2]

    # Obetener ids de las tablas relacionadas
    id_tipo_plano = obtener_tipo_plano(cod_tipo_plano) if cod_tipo_plano else None
    id_tamanio = obtener_tamanio(tamanio) if tamanio else None
    id_revision = obtener_revision(revision) if revision else None
    id_sub_revision = obtener_sub_revision(sub_revision) if sub_revision else None

    identificador_plano = generar_identificador_plano(cod_tipo_plano, num_plano_actual, tamanio, revision, sub_revision)

    # Procesar archivo si se sube uno nuevo
    id_archivo = id_archivo_actual # Se mantiene archivo actual por defecto
    file = None

    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file = request.files['imagen']

    if file and file.filename and validar_archivo(file.filename):
        # Eliminar archivo anterior si existe
        if id_archivo_actual:
            cursor = db.database.cursor()
            cursor.execute("SELECT archivo_path FROM archivos WHERE id_archivo = %s", (id_archivo_actual,))
            old_file = cursor.fetchone()
            cursor.close()
            
            if old_file and old_file[0]:
                try:
                    os.remove(os.path.join(UBI_ARCHIVO, old_file[0]))
                except FileNotFoundError as p:
                    print(f"No se encontro el archivo: {p}")
                    raise

        nombre_original = secure_filename(file.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        ruta_archivo = f"{uuid.uuid4().hex}.{extension}"
        ubicacion = os.path.join(UBI_ARCHIVO, ruta_archivo)
        file.save(ubicacion)

        if extension == 'pdf':
            mime = 'application/pdf'
        elif extension in ('png', 'jpg', 'jpeg'):
            mime = 'image/jpeg' if extension in ('jpg', 'jpeg') else f'image/{extension}'

        archivo_nombre = nombre_original
        archivo_path = ruta_archivo
        archivo_token = uuid.uuid4().hex
        archivo_mime = mime        

        id_archivo = guardar_archivo_info(archivo_nombre, archivo_path, archivo_mime, archivo_token)
    # Actualizar los planos de la base de datos
    if all([fecha, descripcion, dibujante]):
        cursor = db.database.cursor()
        sql = """UPDATE planos SET
                identificador_plano=%s, descripcion=%s, dibujante=%s, fecha=%s, 
                id_tipo_plano=%s, id_tamanio=%s, id_revision=%s, id_sub_revision=%s, id_archivo=%s
                WHERE id_plano=%s"""
        data = (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano,
                id_tamanio, id_revision, id_sub_revision, id_archivo, id_plano)

        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
    
    print(f"Plano actualizado correctamente: {identificador_plano}")
    return redirect(url_for('home'))
        
# RUTA PARA ELIMINAR
@app.route('/delete/<string:id_plano>')
def delete(id_plano):
    try:
        cursor = db.database.cursor()
        # Obtenemos informacion del archivo
        cursor.execute("""SELECT a.archivo_path, p.id_archivo
                       FROM planos p
                       LEFT JOIN archivos a ON p.id_archivos = a.id_archivo
                       WHERE p.id_plano = %s""", (id_plano,))
        row = cursor.fetchone()
        cursor.close()
        
        if row and row[0]:
            # Eliminar archivo fisico
            try:
                os.remove(os.path.join(UBI_ARCHIVO, row[0]))
            except FileNotFoundError as p:
                print(f'Archivo no encontrado: {p}')
            # Eliminar de la base de datos
            if row[1]:
                cursor = db.database.cursor()
                cursor.execute("DELETE FROM archivos WHERE id_archivos = %s", (row[1],))
                db.database.commit()
                cursor.close()

    except Exception as p:
        print(f'Error: {p}')    

    try:
        # Eliminar plano de la base de datos
        cursor = db.database.cursor()
        sql = "DELETE FROM planos WHERE id_plano = %s"
        cursor.execute(sql, (id_plano,))
        db.database.commit()
        cursor.close()
    except Exception as p:
        print(f"Error eliminando plano en la DB: {p}")

    return redirect(url_for('home'))

# RUTA PARA VER ARCHIVO
@app.route('/file/view/<string:token>')
def view_file(token: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_mame FROM planos WHERE archivo_token=%s", (token,))
    row = cursor.fetchone()
    if not row or not row[0]:
        abort(404)
    
    file_on_disk = row[0]
    mime_type = row[1] if row[1] else None

    return send_from_directory(UBI_ARCHIVO, file_on_disk, mimetype=mime_type)

# RUTA PARA DESCARGR ARCHIVO
@app.route('/file/download/<string:token>')
def download_file(token: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_nombre FROM archivos WHERE archivo_token=%s", (token,))
    row = cursor.fetchone()
    cursor.close()
    if not row or not row[0]:
        abort(404)
    file_on_disk = row[0]
    file_name = row[1] if row[1] else file_on_disk

    return row and send_from_directory(UBI_ARCHIVO, file_on_disk, as_attachemet=True, download_name=file_name)

# LAZAMOS APP
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=4000)