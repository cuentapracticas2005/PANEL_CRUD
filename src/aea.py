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
    fecha = request.args.get('fecha','').strip()
    descripcion = request.args.get('descripcion','').strip()
    numero_plano = request.args.get('numero_plano','').strip()
    tamano = request.args.get('tamano','').strip()
    revision = request.args.get('revision','').strip()
    sub_revision = request.args.get('sub_revision','').strip()
    dibujante = request.args.get('dibujante','').strip()

    query = "SELECT * FROM planos WHERE 1=1"
    params = []

    if fecha:
        query += " AND fecha = %s"
        params.append(fecha)
    if descripcion:
        query += " AND descripcion = %s"
        params.append(descripcion)
    if numero_plano:
        query+= " AND num_plano LIKE %s"
        params.append(f"%{numero_plano}%")
    if tamano:
        query += " AND tamanio = %s"
        params.append(tamano)
    if revision:
        query += " AND revision LIKE %s"
        params.append(f"%{revision}%")
    if sub_revision:
        query += " AND sub_revision LIKE %s"
        params.append(f"%{sub_revision}%")
    if dibujante:
        query += " AND dibujante LIKE %s"
        params.append(f"%{dibujante}%")

    query += " ORDER BY id_plano DESC"

    cursor = db.database.cursor()
    cursor.execute(query, tuple(params))
    tuplas = cursor.fetchall()

    nameColumns = []
    for x in cursor.description:
        nameColumns.append(x[0])
    
    union = []
    for x in tuplas:
        union.append(dict(zip(nameColumns, x)))
    
    return render_template('index.html', data=union)

# RUTA PARA GUARDAR DATOS
@app.route('/user', methods=['POST'])
def addUser():
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    num_plano = request.form.get('numero_plano','').strip()
    tipo_plano = request.form.get('tipo_plano','').strip()
    tamano = request.form.get('tamano','').strip()
    revision = request.form.get('revision','').strip()
    sub_revision = request.form.get('sub_revision','').strip()
    dibujante = request.form.get('dibujante','').strip()

    print(f"DATOS RECIBIDOS:")
    print(f"fecha: {fecha}")
    print(f"descripcion: {descripcion}")
    print(f"numero_plano: {num_plano}")
    print(f"tipo_plano: {tipo_plano}")
    print(f"tamano: {tamano}")
    print(f"revision: {revision}")
    print(f"sub_revision: {sub_revision}")
    print(f"dibujante: {dibujante}")

    if not all([fecha, descripcion, tipo_plano, tamano, revision, sub_revision, dibujante]):
        print("Faltan datos")
        return redirect(url_for('home'))
    
    archivo_nombre = None
    archivo_path = None
    archivo_mime = None
    file = None

    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file = request.files['imagen']

    # Validacion del archivo y asignacion en atributos de db
    if file and file.filename and validar_archivo(file.filename):
        nombre_unico = secure_filename(file.filename)
        extension = nombre_unico.rsplit('.', 1)[1].lower()
        ruta_archivo = f"{uuid.uuid4().hex}.{extension}"
        ubicacion = os.path.join(UBI_ARCHIVO,ruta_archivo)
        file.save(ubicacion)

        archivo_nombre = nombre_unico
        archivo_path = ruta_archivo

        if extension == 'pdf':
            archivo_mime = 'aplication/pdf'
        elif extension in ('png', 'jpg', 'jpeg'):
            if extension in ('jpg', 'jpeg'):
                archivo_mime = 'image/jpeg'
            else:
                archivo_mime = f"image/{extension}"

    # Insercion en la DB
    if all([fecha, descripcion, num_plano, tamano, revision, dibujante]):
        cursor = db.database.cursor()
        if archivo_nombre and archivo_path:
            sql = """INSERT INTO planos
                    (fecha, descripcion, tipo_plano, num_plano, tamanio, revision, sub_revision, dibujante, archivo_nombre, archivo_path, archivo_mime)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (fecha, descripcion, tipo_plano, num_plano, tamano, revision, sub_revision, dibujante, archivo_nombre, archivo_path, archivo_mime)
        else:
            sql = """INSERT INTO planos
                    (fecha, descripcion, tipo_plano, num_plano, tamanio, revision, sub_revision, dibujante)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (fecha, descripcion, tipo_plano, num_plano, tamano, revision, sub_revision, dibujante)

        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()

    print("Datos insertados correctamente")
    return redirect(url_for('home'))
    
# RUTA PARA ACTUALIZAR DOCUMENTOS
@app.route('/edit/<string:id_plano>', methods=['POST'])
def edit(id_plano):
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    tipo_plano = request.form.get('tipo_plano','').strip()
    numero_plano = request.form.get('numero_plano','').strip()
    tamano = request.form.get('tamano','').strip()
    revision = request.form.get('revision','').strip()
    sub_revision = request.form.get('sub_revision','').strip()
    dibujante = request.form.get('dibujante','').strip()

    print(f"DATOS RECIBIDOS:")
    print(f"Fecha: {fecha}")
    print(f"Descripcion: {descripcion}")
    print(f"Tipo de plano: {tipo_plano}")
    print(f"Numero de plano: {numero_plano}")
    print(f"Tamano: {tamano}")
    print(f"Revision: {revision}")
    print(f"Sub revision: {sub_revision}")
    print(f"Dibujante: {dibujante}")

    archivo_nombre = None
    archivo_path = None
    archivo_mime = None
    file = None

    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file = request.files['imagen']

    if file and file.filename and validar_archivo(file.filename):
        nombre_original = secure_filename(file.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        ruta_archivo = f"{uuid.uuid4().hex}.{extension}"
        ubicacion = os.path.join(UBI_ARCHIVO, ruta_archivo)
        file.save(ubicacion)

        archivo_nombre = nombre_original
        archivo_path = ubicacion

        if extension == 'pdf':
            archivo_mime = 'aplication/pdf'
        elif extension in ('png', 'jpg', 'jpeg'):
            if extension in ('jpg', 'jpeg'):
                archivo_mime = 'image/jpeg'
            else:
                archivo_mime = f'image/{extension}'

    if all([fecha, descripcion, numero_plano, tamano, revision, dibujante]):
        cursor = db.database.cursor()
        if archivo_nombre and archivo_path:
            sql = "UPDATE planos SET fecha=%s, descripcion=%s, tipo_plano=%s, num_plano=%s, tamanio=%s, revision=%s, sub_revision=%s, dibujante=%s, archivo_nombre=%s, archivo_path=%s, archivo_mime=%s WHERE id_plano=%s"
            data = (fecha, descripcion, tipo_plano, numero_plano, tamano, revision, sub_revision, dibujante, archivo_nombre, archivo_path, archivo_mime, id_plano)
        else:
            sql = "UPDATE planos SET fecha=%s, descripcion=%s, tipo_plano=%s, num_plano=%s, tamanio=%s, revision=%s, sub_revision=%s, dibujante=%s WHERE id_plano=%s"
            data = (fecha, descripcion, tipo_plano, numero_plano, tamano, revision, sub_revision, dibujante, id_plano)

        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        
    print("Datos actualizados correctamente")
    return redirect(url_for('home'))

# RUTA PARA ELIMINAR
@app.route('/delete/<string:id_plano>')
def delete(id_plano):
    try:
        cursor = db.database.cursor()
        cursor.execute("SELECT archivo_path FROM planos WHERE id_plano = %s", (id_plano,))
        row = cursor.fetchone()

        if row and row[0]:
            try:
                os.remove(os.path.join(UBI_ARCHIVO, row[0]))
            except FileNotFoundError as p:
                print(f'Archivo no encontrado: {p}')
    except Exception as p:
        print(f'Error: {p}')    
    finally:
        if 'cursor' in locals():
            cursor.close()
    
    try:
        cursor = db.database.cursor()
        sql = "DELETE FROM planos WHERE id_plano = %s"
        cursor.execute(sql, (id_plano,))
        db.database.commit()
    except Exception as p:
        print(f"Error eliminando en la DB: {p}")
    finally:
        if 'cursor' in locals():
            cursor.close()
    
    return redirect(url_for('home'))

# RUTA PARA VER ARCHIVO
@app.route('/file/view/<string:id_plano>')
def view_file(id_plano: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_mame FROM planos WHERE id_plano=%s", (id_plano,))
    row = cursor.fetchone()
    if not row or not row[0]:
        abort(404)
    
    file_on_disk = row[0]
    mime_type = row[1] if row[1] else None

    return send_from_directory(UBI_ARCHIVO, file_on_disk, mimetype=mime_type)

# RUTA PARA DESCARGR ARCHIVO
@app.route('/file/download/<string:id_plano>')
def download_file(id_plano: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_nombre FROM planos WHERE id_plano=%s", (id_plano,))
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