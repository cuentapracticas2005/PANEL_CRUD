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

# Ruta para guardar documentos en la db_h
@app.route('/user', methods=['POST'])
def addUser():
    # A traves de request.form obtenemos los datos del formulario
    fecha = request.form['fecha']
    descripcion = request.form['descripcion']
    
    # Lógica para manejar numero_plano y numero_plano_manual
    numero_plano_select = request.form.get('numero_plano', '').strip()
    numero_plano_manual = request.form.get('numero_plano_manual', '').strip()
    
    # DEBUG: Imprime los valores para verificar
    print(f"DEBUG - numero_plano_select: '{numero_plano_select}'")
    print(f"DEBUG - numero_plano_manual: '{numero_plano_manual}'")
    
    # Verificar cuál campo usar para num_plano
    if numero_plano_select:
        num_plano = numero_plano_select
        print(f"DEBUG - Usando numero_plano_select: '{num_plano}'")
    elif numero_plano_manual:
        num_plano = numero_plano_manual
        print(f"DEBUG - Usando numero_plano_manual: '{num_plano}'")
    else:
        num_plano = None
        print("DEBUG - Ambos campos están vacíos")
    
    tamano = request.form['tamano']
    version = request.form['version']
    dibujante = request.form['dibujante']
    
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
    
    # Verificar que todos los campos requeridos estén presentes (incluyendo num_plano)
    print(f"DEBUG - Valores antes de validación:")
    print(f"  fecha: '{fecha}'")
    print(f"  descripcion: '{descripcion}'") 
    print(f"  num_plano: '{num_plano}'")
    print(f"  tamano: '{tamano}'")
    print(f"  version: '{version}'")
    print(f"  dibujante: '{dibujante}'")
    
    if all([fecha, descripcion, num_plano, tamano, version, dibujante]):
        print("DEBUG - Todos los campos están presentes, insertando en BD...")
        cursor = db.database.cursor() # Permite ejecutas consultas SQL sobre la base de datos
        # Incluimos columnas de archivo si se subió algo
        if archivo_nombre and archivo_path:
            sql = "INSERT INTO planos (fecha, descripcion, num_plano, tamanio, version, dibujante, archivo_nombre, archivo_path, archivo_mime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            data = (fecha, descripcion, num_plano, tamano, version, dibujante, archivo_nombre, archivo_path, archivo_mime)
        else:
            sql = "INSERT INTO planos (fecha, descripcion, num_plano, tamanio, version, dibujante) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (fecha, descripcion, num_plano, tamano, version, dibujante)
        cursor.execute(sql, data) # Envía la consulta SQL al servidor, pero no la guarda todavía de forma permanente en la base de datos.
        db.database.commit() # Confirma (commit) los cambios hechos por la consulta, y los hace definitivos.
        cursor.close() # CAMBIO: cierre explícito del cursor
        print("DEBUG - Datos insertados correctamente")
    else:
        print("DEBUG - Faltan campos requeridos, no se insertó en BD")
    
    return redirect(url_for('home'))