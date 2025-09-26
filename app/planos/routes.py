from flask import request, redirect, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.planos import planos_bp
from app.planos.utils import (
    obtener_tipo_plano, 
    obtener_siguiente_numero, 
    obtener_tamanio,
    obtener_revision, 
    obtener_sub_revision, 
    guardar_archivo_info, 
    generar_identificador_plano)
from app.archivos.utils import validar_archivo, ubi_archivos
import database as db
import os
import uuid
UBI_ARCHIVO = ubi_archivos()
"""
Se implementa manejo de los registros como el agregar, editar y eliminar planos
"""
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
    fecha = request.form.get('fecha', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    cod_tipo_plano = request.form.get('tipo_plano', '').strip()
    tamanio = request.form.get('tamanio', '').strip()
    revision = request.form.get('revision', '').strip()
    sub_revision = request.form.get('sub_revision', '').strip()
    dibujante = request.form.get('dibujante', '').strip()
    
    print(f"DATOS RECIBIDOS PARA ACTUALIZAR: ")
    print(f"ID Plano: {id_registro}")
    print(f"Fecha: {fecha}")
    print(f"Descripcion: {descripcion}")
    print(f"Tipo de plano: {cod_tipo_plano}")
    print(f"Codigo tipo: {cod_tipo_plano}")
    print(f"Tamaño: {tamanio}")
    print(f"Revision: {revision}")
    print(f"Sub revision: {sub_revision}")
    print(f"Dibujante: {dibujante}")

    cursor = db.database.cursor()
    cursor.execute("""SELECT np.id_num_plano, r.id_num_plano, r.id_archivo
                   FROM registros r
                   JOIN num_plano np ON r.id_num_plano = np.id_num_plano
                   WHERE r.id_registro = %s""", (id_registro, ))
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

    # Validar si se duplica registro antes de actualizar
    cursor = db.database.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM registros
        WHERE identificador_plano = %s AND id_registro != %s
    """, (identificador_plano, id_registro))
    existe = cursor.fetchone()[0]
    cursor.close()

    if existe > 0:
        return redirect(url_for('home'))

    # Si es que hay un archivo se procede a hacer la actualizacion
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

        # Se actualiza la tabla archivos
        id_archivo = guardar_archivo_info(archivo_nombre, archivo_path, archivo_mime, archivo_token)
    
    # Actualizar los planos de la base de datos
    if all([fecha, descripcion, dibujante]):
        cursor = db.database.cursor()
        sql = """UPDATE registros SET
                identificador_plano=%s, descripcion=%s, dibujante=%s, fecha=%s,
                id_tipo_plano=%s, id_tamanio=%s, id_revision=%s, id_sub_revision=%s, id_archivo=%s
                WHERE id_registro=%s"""
        data = (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano,
                id_tamanio, id_revision, id_sub_revision, id_archivo, id_registro)

        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
    
    print(f"Plano actualizado correctamente: {identificador_plano}")
    return redirect(url_for('main.home'))

@planos_bp.route('/delete/<string:id_registro>')
@login_required
def delete_plano(id_registro):
    try:
        cursor = db.database.cursor()
        # Obtenemos informacion del archivo
        cursor.execute("""SELECT a.archivo_path, r.id_archivo, a.id_archivo
                       FROM registros r
                       LEFT JOIN archivos a ON r.id_archivo = a.id_archivo
                       WHERE r.id_registro = %s""", (id_registro,))
        row = cursor.fetchone()
        cursor.close()
        
        if row and row[0]:
            # Eliminar archivo fisico
            try:
                os.remove(os.path.join(UBI_ARCHIVO, row[0]))
            except FileNotFoundError as p:
                print(f'Archivo no encontrado: {p}')
            # Eliminar de la base de datos
            try:
                cursor = db.database.cursor()
                sql = "DELETE FROM registros WHERE id_registro = %s"
                cursor.execute(sql, (id_registro,))
                db.database.commit()
                cursor.close()
                if row[2]:
                    cursor = db.database.cursor()
                    cursor.execute("DELETE FROM archivos WHERE id_archivo = %s", (row[2],))
                    db.database.commit()
                    cursor.close()
                    print(f"Se elimino correctamente {row[2]}")
            except Exception as p:
                print(f"Error eliminando datos de la DB: {p}")
        else:
            try:
                cursor = db.database.cursor()
                sql = "DELETE FROM registros WHERE id_registro = %s"
                cursor.execute(sql, (id_registro,))
                db.database.commit()
                cursor.close()
            except Exception as p:
                print(f"Error eliminando datos de la DB: {p}")
    except Exception as p:
        print(f'Error: {p}')

    return redirect(url_for('main.home'))