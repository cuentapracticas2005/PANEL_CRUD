from flask import request, redirect, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.planos import planos_bp
from app.planos.utils import (
    obtener_tipo_plano, obtener_siguiente_numero, obtener_tamanio,
    obtener_revision, obtener_sub_revision, guardar_archivo_info,
    generar_identificador_plano
)
from app.archivos.utils import validar_archivo, get_upload_folder
import database as db
import os
import uuid

@planos_bp.route('/add', methods=['POST'])
@login_required
def add_plano():
    # Obtener datos del formulario
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    numero_plano_rep = request.form.get('numero_plano','').strip()
    identificador_plano_rep = request.form.get('identificador_plano','').strip()
    cod_tipo_plano = request.form.get('tipo_plano','').strip()
    tamanio = request.form.get('tamano','').strip()
    revision = request.form.get('revision','').strip()
    sub_revision = request.form.get('sub_revision','').strip()
    dibujante = request.form.get('dibujante','').strip()
    
    if not all([fecha, descripcion, cod_tipo_plano, tamanio, revision, dibujante]):
        print("Faltan datos")
        return redirect(url_for('main.home'))
    
    # Obtener IDs de tablas relacionadas
    id_tipo_plano = obtener_tipo_plano(cod_tipo_plano)
    id_tamanio = obtener_tamanio(tamanio)
    id_revision = obtener_revision(revision)
    id_sub_revision = obtener_sub_revision(sub_revision) if sub_revision else None

    # Verificar si el número de plano existe
    cursor = db.database.cursor()
    cursor.execute("SELECT id_num_plano FROM num_plano")
    numeros_existentes = cursor.fetchall()
    cursor.close()
    
    numero_existe = any(str(numero_plano_rep) == str(num[0]) for num in numeros_existentes)
    
    if numero_existe:
        identificador_plano = generar_identificador_plano(
            cod_tipo_plano, numero_plano_rep, tamanio, revision, sub_revision
        )
        id_num_plano = numero_plano_rep
    else:
        id_num_plano = obtener_siguiente_numero()
        identificador_plano = generar_identificador_plano(
            cod_tipo_plano, id_num_plano, tamanio, revision, sub_revision
        )

    # Procesar archivo si existe
    id_archivo = None
    file = None
    
    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file = request.files['imagen']

    if file and file.filename and validar_archivo(file.filename):
        UBI_ARCHIVO = get_upload_folder()
        nombre_original = secure_filename(file.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        ruta_archivo = f"{uuid.uuid4().hex}.{extension}"
        ubicacion = os.path.join(UBI_ARCHIVO, ruta_archivo)
        file.save(ubicacion)

        if extension == 'pdf':
            mime = 'application/pdf'
        elif extension in ('png', 'jpg', 'jpeg'):
            mime = 'image/jpeg' if extension in ('jpg', 'jpeg') else f"image/{extension}"

        id_archivo = guardar_archivo_info(
            nombre_original, ruta_archivo, mime, uuid.uuid4().hex
        )
    
    # Verificar duplicados y guardar
    cursor = db.database.cursor()
    cursor.execute("SELECT identificador_plano FROM registros WHERE identificador_plano = %s", 
                  (identificador_plano,))
    existe = cursor.fetchone()
    
    if not existe:
        sql = """INSERT INTO registros
                (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano,
                id_num_plano, id_tamanio, id_revision, id_sub_revision, id_archivo)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        data = (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano,
                id_num_plano, id_tamanio, id_revision, id_sub_revision, id_archivo)
        cursor.execute(sql, data)
        db.database.commit()
    cursor.close()
    
    return redirect(url_for('main.home'))

@planos_bp.route('/edit/<string:id_registro>', methods=['POST'])
@login_required
def edit_plano(id_registro):
    # Implementación similar a la función edit original
    # pero usando las funciones utils del módulo
    # ... (código de edición)
    return redirect(url_for('main.home'))

@planos_bp.route('/delete/<string:id_registro>')
@login_required
def delete_plano(id_registro):
    # Implementación similar a la función delete original
    # ... (código de eliminación)
    return redirect(url_for('main.home'))