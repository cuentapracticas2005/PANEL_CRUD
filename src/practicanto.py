from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
import os
import database as db
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv
load_dotenv()

# =========== CONFIGURACION INICIAL DE LA APP FLASK ==============
# configuracion de directorios para templates y static
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

# =========== CONFIGURACION DE SUBIDA DE ARCHIVOS ==============
def get_upload_folder():
    # 1. Intentar obtener la ruta de una variable de entorno
    upload_path = os.environ.get('UPLOAD_FOLDER')

    # 2. Si no está definida, usar carpeta local por defecto
    if not upload_path:
        upload_path = os.path.join(os.path.dirname(__file__), 'uploads')
        print("⚠️ UPLOAD_FOLDER no definido, usando carpeta local")

    try:
        # 3. Crear carpeta si no existe
        os.makedirs(upload_path, exist_ok=True)
        # 4. Verificar permisos de lectura
        os.listdir(upload_path) 
        print(f"✅ Permisos de lectura OK en: {upload_path}")
        # 5. Verificar permisos de escritura
        test_file = os.path.join(upload_path, 'permission_test.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✅ Permisos de escritura OK en: {upload_path}")

    except PermissionError as e:
        print(f"❌ Sin permisos en {upload_path}: {e}")
        raise
    except Exception as e:
        print(f"❌ Error inesperado en {upload_path}: {e}")
        raise

    return upload_path


# CONFIGURACION DE UPLOADS
UPLOAD_FOLDER = get_upload_folder()             # carpeta donde se almacenaran los archivos subidos
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

# =========== CONFIGURACION DE BASE DE DATOS PARA ALMACENAR ARCHIVOS =============
try:
    cursor = db.database.cursor() # cursor para la base de datos
    cursor.execute(
        """
        ALTER TABLE planos
            ADD COLUMN IF NOT EXISTS archivo_nombre VARCHAR(255) NULL,
            ADD COLUMN IF NOT EXISTS archivo_path VARCHAR(300) NULL,
            ADD COLUMN IF NOT EXISTS archivo_mime VARCHAR(100) NULL
        """
    )
    db.database.commit()
    cursor.close()
except Exception:
    try:
        cursor = db.database.cursor()
        for stmt in [
            "ALTER TABLE planos ADD COLUMN archivo_nombre VARCHAR(255) NULL",
            "ALTER TABLE planos ADD COLUMN archivo_path VARCHAR(300) NULL",
            "ALTER TABLE planos ADD COLUMN archivo_mime VARCHAR(100) NULL",
        ]:
            try:
                cursor.execute(stmt)
                db.database.commit()
            except Exception:
                pass
        cursor.close()
    except Exception:
        pass

# funcion de seguridad para validacion de extension de archivos
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# =========== RUTAS DE LA APP =================
@app.route('/')
def home():
    """ Ruta principal, pagina de inicio con filtros   
        * con request.args.get() se obtiene parametro de la url
        * ('') se define un valor por defecto si es que no existe un parametro
        * .strip() elimina espacios al inicio y al final
        * todos los filtros opcionales
    """
    fecha = request.args.get('fecha', '').strip()
    descripcion = request.args.get('descripcion', '').strip()
    numero_plano = request.args.get('numero_plano', '').strip()
    tamano = request.args.get('tamano', '').strip()
    revision = request.args.get('revision', '').strip()
    sub_revision = request.args.get('sub_revision', '').strip()
    dibujante = request.args.get('dibujante', '').strip()

    # Construcción dinámica del WHERE con parámetros para evitar inyección SQL
    query = "SELECT * FROM planos WHERE 1=1" # simplificacion de la consulta
    params = [] # lista adonde se almacenaran los parametros
    if fecha:
        query += " AND fecha = %s"
        params.append(fecha)
    if descripcion:
        query += " AND descripcion LIKE %s"
        params.append(f"%{descripcion}%")
    if numero_plano:
        query += " AND num_plano LIKE %s"
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
    cursor.execute(query, tuple(params)) # ejecucion segura con parametros separados 
    myresult = cursor.fetchall() # fetchall() obtiene todos los registros de la consulta
    # Convertir los datos a diccionario
    insertObject = [] # array vacio para poder almacenar los registros de planos
    columnNames = [column[0] for column in cursor.description] # Obtenemos los nombres de las columnas de la tabla
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record))) # Convertimos cada registro en un diccionario
    cursor.close()
    return render_template('index.html', data=insertObject) # Pasamos el array de diccionarios a la plantilla index.html

# ============== RUTA PARA GUARDAR DOCUMENTOS EN LA DB ==============
@app.route('/user', methods=['POST'])
def addUser():
    # Obtener datos del formulario
    fecha = request.form.get('fecha', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    num_plano = request.form.get('numero_plano', '').strip()
    tipo_plano = request.form.get('tipo_plano', '').strip()
    tamano = request.form.get('tamano', '').strip()
    revision = request.form.get('revision', '').strip()
    sub_revision = request.form.get('sub_revision', '').strip()
    dibujante = request.form.get('dibujante', '').strip()

    # --- Debug ---
    print(f"DEBUG - Datos recibidos:")
    print(f"  fecha: '{fecha}'")
    print(f"  descripcion: '{descripcion}'")
    print(f"  num_plano: '{num_plano}'")
    print(f"  tipo_plano: '{tipo_plano}'")
    print(f"  tamano: '{tamano}'")
    print(f"  revision: '{revision}'")
    print(f"  sub_revision: '{sub_revision}'")
    print(f"  dibujante: '{dibujante}'")

    # Validación de campos requeridos
    if not all([fecha, descripcion, num_plano, dibujante]):
        print("DEBUG - Faltan campos requeridos")
        return redirect(url_for('home'))

    # se inicializa variable donde se guardaran archivos
    archivo_nombre = None
    archivo_path = None
    archivo_mime = None
    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file_storage = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file_storage = request.files['imagen']

    # proceso del archivo si es valido
    file_storage = request.files.get('pdf')
    if file_storage and file_storage.filename and allowed_file(file_storage.filename):
        original_name = secure_filename(file_storage.filename)
        extension = original_name.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file_storage.save(save_path)
        
        # se preparan los datos del archivo
        archivo_nombre = original_name
        archivo_path = unique_name
        
        if extension == 'pdf':
            archivo_mime = 'application/pdf'
        elif extension in ('png', 'jpg', 'jpeg', 'gif'):
            archivo_mime = f"image/{'jpeg' if extension in ('jpg','jpeg') else extension}"

    # Inserción en db solo si todos los campos requeridos están presentes
    if all([fecha, descripcion, num_plano, tamano, revision, dibujante]):
        cursor = db.database.cursor()
        # se inserta a la db tomando en cuenta dos caminos, si es hay o no hay archivo
        if archivo_nombre and archivo_path:
            sql = """INSERT INTO planos
                    (fecha, descripcion, tipo_plano, num_plano, tamanio, revision, sub_revision, dibujante, archivo_nombre, archivo_path, archivo_mime)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (fecha, descripcion, tipo_plano, num_plano, tamano, revision, sub_revision, dibujante, archivo_nombre, archivo_path, archivo_mime)
        else:
            sql = """INSERT INTO planos
                    (fecha, descripcion, tipo_plano, num_plano, tamanio, revision, sub_revision, dibujante)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (fecha, descripcion, tipo_plano, num_plano, tamano, revision, sub_revision, dibujante)
        
        # se inserta a la db
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        
        print("DEBUG - Datos insertados correctamente")
        return redirect(url_for('home'))

# ============= RUTA PARA ACTUALIZAR DOCUMENTOS EN LA DB ==============
@app.route('/edit/<string:id_plano>', methods=['POST'])
def edit (id_plano):
    fecha = request.form['fecha']
    descripcion = request.form['descripcion']
    tipo_plano = request.form['tipo_plano']
    numero_plano = request.form['numero_plano']
    tamano = request.form['tamano']
    revision = request.form['revision']
    sub_revision = request.form['sub_revision']
    dibujante = request.form['dibujante']

    # inicializacion de variable donde se van a almacenar los datos del archivo
    archivo_nombre = None
    archivo_path = None
    archivo_mime = None
    file_storage = None

    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file_storage = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file_storage = request.files['imagen']

    if file_storage and allowed_file(file_storage.filename):
        original_name = secure_filename(file_storage.filename)
        extension = original_name.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file_storage.save(save_path)
        archivo_nombre = original_name
        archivo_path = unique_name

        if extension == 'pdf':
            archivo_mime = 'application/pdf'
        elif extension in ('png', 'jpg', 'jpeg', 'gif'):
            archivo_mime = f"image/{'jpeg' if extension in ('jpg','jpeg') else extension}"

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

    return redirect(url_for('home'))


# ============== RUTA PARA ELIMINAR DOCUMENTOS DE LA DB ==============
@app.route('/delete/<string:id_plano>')
def delete(id_plano):
    try:
        cursor = db.database.cursor()
        # consulta del archivo a eliminar
        cursor.execute("SELECT archivo_path FROM planos WHERE id_plano=%s", (id_plano,))
        row = cursor.fetchone()

        if row and row[0]: # si existe un archivo asociado se elimina del sistema
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, row[0])) # eliminamos el archivo del sistema
            except FileNotFoundError:
                pass
        cursor.close()
    except Exception:
        pass

    # eliminacion de la db
    cursor = db.database.cursor()
    sql = "DELETE FROM planos WHERE id_plano=%s"
    data = (id_plano,)
    cursor.execute(sql, data)
    db.database.commit() 
    cursor.close()  
    return redirect(url_for('home'))

# ================= RUTA PARA VER ARCHIVO EN EL NAVEGADOR =================
@app.route('/file/view/<string:id_plano>')
def view_file(id_plano: str):
    cursor = db.database.cursor()
    # consulta de ruta y tipo del archivo
    cursor.execute("SELECT archivo_path, archivo_mime FROM planos WHERE id_plano=%s", (id_plano,))
    row = cursor.fetchone()
    cursor.close()
    # verificacion de existencia del archivo
    if not row or not row[0]:
        abort(404)
        
    file_on_disk = row[0]
    mime_type = row[1] if row[1] else None
    
    # servir el archivo
    return send_from_directory(UPLOAD_FOLDER, file_on_disk, mimetype=mime_type)

# ================= RUTA PARA DESCARGAR ARCHIVO =================
@app.route('/file/download/<string:id_plano>')
def download_file(id_plano: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_nombre FROM planos WHERE id_plano=%s", (id_plano,))
    row = cursor.fetchone()
    cursor.close()
    if not row or not row[0]:
        abort(404)
    file_on_disk = row[0]
    original_name = row[1] if row[1] else file_on_disk
    return row and send_from_directory(UPLOAD_FOLDER, file_on_disk, as_attachment=True, download_name=original_name)

# Lanzamos la app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=4000)  # host=0.0.0.0 para acceso externo
    