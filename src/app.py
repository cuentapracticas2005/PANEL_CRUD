from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
import os
import database as db
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv
load_dotenv()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

# Configuración de subida de archivos
def get_upload_folder():
    """Obtiene la carpeta de uploads con validaciones"""
    upload_path = os.environ.get('UPLOAD_FOLDER')
    
    if not upload_path:
        # Fallback para desarrollo local
        upload_path = os.path.join(os.path.dirname(__file__), 'uploads')
        print("⚠️  UPLOAD_FOLDER no definido, usando carpeta local")
    
    # Verificar que la carpeta existe y es accesible
    try:
        os.makedirs(upload_path, exist_ok=True)
        # Prueba de escritura
        test_file = os.path.join(upload_path, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✅ Carpeta de uploads configurada: {upload_path}")
    except PermissionError:
        print(f"❌ Sin permisos de escritura en: {upload_path}")
        raise
    except Exception as e:
        print(f"❌ Error al acceder a la carpeta: {e}")
        raise
    
    return upload_path

# Puedes agregar esta función para verificar permisos
def verificarPermisos(folder_path):
    """Verifica permisos de la carpeta"""
    try:
        # Verificar lectura
        os.listdir(folder_path)
        print(f"✅ Permisos de lectura OK en: {folder_path}")
        
        # Verificar escritura
        test_file = os.path.join(folder_path, 'permission_test.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✅ Permisos de escritura OK en: {folder_path}")
        
        return True
    except PermissionError as e:
        print(f"❌ Error de permisos en {folder_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error al verificar {folder_path}: {e}")
        return False


UPLOAD_FOLDER = get_upload_folder()
verificarPermisos(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Crear acrpeta umploads si es que no existe

# Garantizamos columnas para archivo en la tabla si no existen
try:
    cursor = db.database.cursor() # Abrimos un cursor para la base de datos
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
    # Si falla (versiones antiguas de MySQL), intentamos añadir una por una ignorando errores
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
    except Exception: # Si ambos casos fallan se ignoran los errores
        pass

def allowed_file(filename: str) -> bool: # Verifica si el archivo tiene una extensión permitida
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS # Verifica si la extensión del archivo es permitida


#Rutas de la app
@app.route('/')
def home():
    # CAMBIO: Soporte de filtros opcionales via query params (GET)
    # Doc: Ahora puedes buscar con cualquier combinación de criterios. 
    # Si no envías nada, se listan todos.
    anio = request.args.get('anio', '').strip()
    mes = request.args.get('mes', '').strip()
    descripcion = request.args.get('descripcion', '').strip()
    numero_plano = request.args.get('numero_plano', '').strip()
    tamano = request.args.get('tamano', '').strip()
    version = request.args.get('version', '').strip()
    dibujante = request.args.get('dibujante', '').strip()
    dibujado_en = request.args.get('dibujado_en', '').strip()

    # Construcción dinámica del WHERE con parámetros para evitar inyección SQL
    query = "SELECT * FROM planos WHERE 1=1"
    params = []
    if anio:
        query += " AND anio = %s"  # igualdad exacta para año
        params.append(anio)
    if mes:
        query += " AND mes = %s"   # igualdad exacta para mes
        params.append(mes)
    if descripcion:
        query += " AND descripcion LIKE %s"  # búsqueda parcial en descripción
        params.append(f"%{descripcion}%")
    if numero_plano:
        query += " AND num_plano LIKE %s"    # permite búsqueda parcial por número de plano
        params.append(f"%{numero_plano}%")
    if tamano:
        query += " AND tamanio = %s"         # igualdad exacta para tamaño
        params.append(tamano)
    if version:
        query += " AND version LIKE %s"      # búsqueda parcial para versión
        params.append(f"%{version}%")
    if dibujante:
        query += " AND dibujante LIKE %s"    # búsqueda parcial por dibujante
        params.append(f"%{dibujante}%")
    if dibujado_en:
        query += " AND dibujado_en = %s"     # igualdad exacta para herramienta
        params.append(dibujado_en)

    cursor = db.database.cursor() # Usamos la funcion cursor para la conexion a la base de datos
    cursor.execute(query, tuple(params))
    myresult = cursor.fetchall() # fetchall() obtiene todos los registros de la consulta
    # Convertir los datos a diccionario
    insertObject = [] # Declaramos un array vacio para poder almacenar los registros de planos
    columnNames = [column[0] for column in cursor.description] # Obtenemos los nombres de las columnas de la tabla
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record))) # Convertimos cada registro en un diccionario
    cursor.close()
    return render_template('index.html', data=insertObject) # Pasamos el array de diccionarios a la plantilla index.html


# Ruta para guardar documentos en la db_h
@app.route('/user', methods=['POST'])
def addUser():
    # A traves de request.form obtenemos los datos del formulario
    anio = request.form['anio']
    mes = request.form['mes']
    descripcion = request.form['descripcion']
    numero_plano = request.form['numero_plano']
    tamano = request.form['tamano']
    version = request.form['version']
    dibujante = request.form['dibujante']
    dibujado_en = request.form['dibujado_en']

    #Procesamiento de archivo (pdf o imagen)
    archivo_nombre = None
    archivo_path = None
    archivo_mime = None
    file_storage = None
    # Aceptamos tanto campo 'pdf' como 'imagen' del formulario
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
        # Mime básico por extension
        if extension == 'pdf':
            archivo_mime = 'application/pdf'
        elif extension in ('png', 'jpg', 'jpeg', 'gif'):
            archivo_mime = f"image/{'jpeg' if extension in ('jpg','jpeg') else extension}"

    if all([anio, mes, descripcion, numero_plano, tamano, version, dibujante, dibujado_en]):
        cursor = db.database.cursor() # Permite ejecutas consultas SQL sobre la base de datos
        # Incluimos columnas de archivo si se subió algo
        if archivo_nombre and archivo_path:
            sql = "INSERT INTO planos (anio, mes, descripcion, num_plano, tamanio, version, dibujante, dibujado_en, archivo_nombre, archivo_path, archivo_mime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            data = (anio, mes, descripcion, numero_plano, tamano, version, dibujante, dibujado_en, archivo_nombre, archivo_path, archivo_mime)
        else:
            sql = "INSERT INTO planos (anio, mes, descripcion, num_plano, tamanio, version, dibujante, dibujado_en) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            data = (anio, mes, descripcion, numero_plano, tamano, version, dibujante, dibujado_en)
        cursor.execute(sql, data) # Envía la consulta SQL al servidor, pero no la guarda todavía de forma permanente en la base de datos.
        db.database.commit() # Confirma (commit) los cambios hechos por la consulta, y los hace definitivos.
        cursor.close() # CAMBIO: cierre explícito del cursor
    return redirect(url_for('home'))


# Ruta para actualizar documentos en la db_h
@app.route('/edit/<string:id_plano>', methods=['POST'])
def edit (id_plano):
    anio = request.form['anio']
    mes = request.form['mes']
    descripcion = request.form['descripcion']
    numero_plano = request.form['numero_plano']
    tamano = request.form['tamano']
    version = request.form['version']
    dibujante = request.form['dibujante']
    dibujado_en = request.form['dibujado_en']

    # CAMBIO: manejo opcional de nuevo archivo
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

    if all([anio, mes, descripcion, numero_plano, tamano, version, dibujante, dibujado_en]):
        cursor = db.database.cursor() 
        # CAMBIO: si hay nuevo archivo, actualizamos columnas correspondientes
        if archivo_nombre and archivo_path:
            sql = "UPDATE planos SET anio=%s, mes=%s, descripcion=%s, num_plano=%s, tamanio=%s, version=%s, dibujante=%s, dibujado_en=%s, archivo_nombre=%s, archivo_path=%s, archivo_mime=%s WHERE id_plano=%s"
            data = (anio, mes, descripcion, numero_plano, tamano, version, dibujante, dibujado_en, archivo_nombre, archivo_path, archivo_mime, id_plano)
        else:
            sql = "UPDATE planos SET anio=%s, mes=%s, descripcion=%s, num_plano=%s, tamanio=%s, version=%s, dibujante=%s, dibujado_en=%s WHERE id_plano=%s"
            data = (anio, mes, descripcion, numero_plano, tamano, version, dibujante, dibujado_en, id_plano)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
    return redirect(url_for('home'))


# Ruta para eliminar documentos de la db_h
@app.route('/delete/<string:id_plano>')
def delete(id_plano):
    # CAMBIO: eliminamos archivo del disco si existe
    try:
        cursor = db.database.cursor()
        cursor.execute("SELECT archivo_path FROM planos WHERE id_plano=%s", (id_plano,))
        row = cursor.fetchone()
        if row and row[0]:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, row[0]))
            except FileNotFoundError:
                pass
        cursor.close()
    except Exception:
        pass

    cursor = db.database.cursor()
    sql = "DELETE FROM planos WHERE id_plano=%s"
    data = (id_plano,)
    cursor.execute(sql, data)
    db.database.commit() 
    cursor.close()  
    return redirect(url_for('home'))

# CAMBIO: ruta para ver archivo en el navegador
@app.route('/file/view/<string:id_plano>')
def view_file(id_plano: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_mime FROM planos WHERE id_plano=%s", (id_plano,))
    row = cursor.fetchone()
    cursor.close()
    if not row or not row[0]:
        abort(404)
    file_on_disk = row[0]
    mime_type = row[1] if row[1] else None
    return send_from_directory(UPLOAD_FOLDER, file_on_disk, mimetype=mime_type)

# CAMBIO: ruta para descargar archivo
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
    return send_from_directory(UPLOAD_FOLDER, file_on_disk, as_attachment=True, download_name=original_name)

# Lanzamos la app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=4000)  # host=0.0.0.0 para acceso externo