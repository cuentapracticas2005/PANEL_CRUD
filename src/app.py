from flask import Flask, render_template, request, redirect, url_for
import os
import database as db
# CAMBIO: Añadimos utilidades para manejo de archivos y descarga
from flask import send_from_directory, abort
from werkzeug.utils import secure_filename
import uuid


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

# CAMBIO: Configuración de subida de archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'umploads')
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CAMBIO: Garantizamos columnas para archivo en la tabla si no existen
try:
    cursor = db.database.cursor()
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
    except Exception:
        pass


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


#Rutas de la app
@app.route('/')
def home():
    # Consulta en la base de datos
    cursor = db.database.cursor() # Usamos la funcion cursor para la conexion a la base de datos
    cursor.execute("SELECT * FROM planos")
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

    # CAMBIO: procesamiento de archivo (pdf o imagen)
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
        # CAMBIO: incluimos columnas de archivo si se subió algo
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
