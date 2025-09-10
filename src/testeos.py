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
    """
    Verifica y configura la carpeta de archivos subidos
    Retorna: La ruta de la carpeta de archivos
    """
    ubi_archivos = os.environ.get('UPLOAD_FOLDER')

    if not ubi_archivos:
        ubi_archivos = os.path.join(os.path.dirname(__file__),'archivos_local')
        print(f"NO SE ENCONTRO UPLOAD_FOLDER EN RED, SE CREO CARPETA EN LOCAL")

    try:
        os.makedirs(ubi_archivos, exist_ok=True)
        try:
            os.listdir(ubi_archivos)
            print(f"✅LECTURA CORRECTA EN: {ubi_archivos}")
        except PermissionError as p:
            print(f"❌NO HAY PERMISOS DE LECTURA EN {ubi_archivos}, ERROR: {p}")
            raise        
        try:
            test = os.path.join(ubi_archivos,'test.tmp')
            with open(test, 'w') as t:
                t.write('hola')
            print(f"✅ESCRITURA CORRECTA EN: {ubi_archivos}")
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
    """
    Valida si el archivo tiene una extensión permitida
    Parámetros: filename - nombre del archivo
    Retorna: True si es válido, False si no
    """
    valor = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALL_EXTENSIONS
    return valor

# ======== FUNCIONES PARA EL MANEJO DE TABLAS RELACIONADAS ==========

def obtener_tipo_plano(cod_tipo_plano):
    """
    Obtiene el ID del tipo de plano o lo crea si no existe
    Parámetros: 
        tipo_plano - descripción del tipo de plano
        cod_tipo_plano - código abreviado del tipo (3 caracteres)
    Retorna: id_tipo_plano
    """
    cursor = db.database.cursor()
    cursor.execute("SELECT id_tipo_plano FROM tipo_plano WHERE cod_tipo_plano = %s", (cod_tipo_plano,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None
    
def obtener_siguiente_numero_plano():
    """
    Obtiene el siguiente número de plano disponible
    Retorna: tuple (id_num_plano, num_plano)
    """
    cursor = db.database.cursor()
    
    # Insertar nuevo número de plano (auto_increment desde 30000)
    cursor.execute("INSERT INTO num_plano (num_plano) VALUES (NULL)")
    db.database.commit()
    id_num_plano = cursor.lastrowid
    
    # Obtener el número generado
    cursor.execute("SELECT num_plano FROM num_plano WHERE id_num_plano = %s", (id_num_plano,))
    num_plano = cursor.fetchone()[0]
    
    cursor.close()
    return id_num_plano, num_plano

def obtener_tamanio(tamanio):
    """
    Obtiene el ID del tamaño o lo crea si no existe
    Parámetros: tamanio - código del tamaño (A0, A1, A2, etc)
    Retorna: id_tamanio
    """
    cursor = db.database.cursor()
    cursor.execute("SELECT id_tamanio FROM tamanio WHERE tamanio = %s", (tamanio,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def obtener_revision(revision):
    """
    Obtiene el ID de la revisión o la crea si no existe
    Parámetros: revision - código de revisión (A, B, C, etc)
    Retorna: id_revision
    """
    cursor = db.database.cursor()
    cursor.execute("SELECT id_revision FROM revision WHERE revision = %s", (revision,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def obtener_sub_revision(sub_revision):
    """
    Obtiene el ID de la sub-revisión o la crea si no existe
    Parámetros: sub_revision - número de sub-revisión
    Retorna: id_sub_revision
    """
    cursor = db.database.cursor()

    # Si no hay sub_revision, retornar None
    if not sub_revision or sub_revision == '0':
        cursor.close()
        return None
    
    cursor.execute("SELECT id_sub_revision FROM sub_revision WHERE sub_revision = %s", (sub_revision,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def guardar_archivo_info(archivo_nombre, archivo_path, archivo_mime, archivo_token):
    """
    Guarda la información del archivo en la tabla archivos
    Parámetros:
        archivo_nombre - nombre original del archivo
        archivo_path - ruta donde se guardó el archivo
        archivo_mime - tipo MIME del archivo
        archivo_token - token UUID único para el archivo
    Retorna: id_archivo
    """
    cursor = db.database.cursor()
    cursor.execute("""INSERT INTO archivos (archivo_nombre, archivo_path, archivo_mime, archivo_token) 
                     VALUES (%s, %s, %s, %s)""",
                  (archivo_nombre, archivo_path, archivo_mime, archivo_token))
    db.database.commit()
    id_archivo = cursor.lastrowid
    cursor.close()
    return id_archivo

def generar_identificador_plano(cod_tipo_plano, num_plano, tamanio, revision, sub_revision):
    """
    Genera el identificador único del plano según el formato especificado
    Formato: COD_TIPO-NUMERO-TAMAÑO+REVISION+SUBREVISION
    Ejemplo: MEC-30001-A1B2
    """
    identificador = f"{cod_tipo_plano}-{num_plano}-{tamanio}{revision}"
    if sub_revision and sub_revision != '0':
        identificador += str(sub_revision)
    return identificador

# ==================== RUTAS DE LA APP ============================

@app.route('/')
def home():
    """
    Ruta principal que muestra el listado de planos con filtros
    """
    fecha = request.args.get('fecha','').strip()
    descripcion = request.args.get('descripcion','').strip()
    identificador = request.args.get('identificador_plano','').strip()
    dibujante = request.args.get('dibujante','').strip()

    # Query con JOINs para obtener todos los datos relacionados
    query = """
        SELECT 
            p.id_plano,
            p.identificador_plano,
            p.descripcion,
            p.dibujante,
            p.fecha,
            tp.tipo_plano,
            tp.cod_tipo_plano,
            np.num_plano,
            t.tamanio,
            r.revision,
            sr.sub_revision,
            a.archivo_nombre,
            a.archivo_token
        FROM planos p
        LEFT JOIN tipo_plano tp ON p.id_tipo_plano = tp.id_tipo_plano
        LEFT JOIN num_plano np ON p.id_num_plano = np.id_num_plano
        LEFT JOIN tamanio t ON p.id_tamanio = t.id_tamanio
        LEFT JOIN revision r ON p.id_revision = r.id_revision
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
        query += " AND p.identificador_plano LIKE %s"
        params.append(f"%{identificador}%")
    if dibujante:
        query += " AND p.dibujante LIKE %s"
        params.append(f"%{dibujante}%")

    query += " ORDER BY p.id_plano DESC"

    cursor = db.database.cursor()
    cursor.execute(query, tuple(params))
    tuplas = cursor.fetchall()

    nameColumns = []
    for x in cursor.description:
        nameColumns.append(x[0])
    
    union = []
    for x in tuplas:
        union.append(dict(zip(nameColumns, x)))
    
    cursor.close()
    return render_template('index.html', data=union)

# RUTA PARA GUARDAR DATOS
@app.route('/user', methods=['POST'])
def addUser():
    """
    Ruta para agregar un nuevo plano
    Procesa los datos del formulario y crea registros en todas las tablas relacionadas
    """
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    tipo_plano = request.form.get('tipo_plano','').strip()
    cod_tipo_plano = request.form.get('cod_tipo_plano','').strip()[:3]  # Máximo 3 caracteres
    tamanio = request.form.get('tamanio','').strip()
    revision = request.form.get('revision','').strip()
    sub_revision = request.form.get('sub_revision','').strip()
    dibujante = request.form.get('dibujante','').strip()

    print(f"DATOS RECIBIDOS:")
    print(f"fecha: {fecha}")
    print(f"descripcion: {descripcion}")
    print(f"tipo_plano: {tipo_plano}")
    print(f"cod_tipo_plano: {cod_tipo_plano}")
    print(f"tamanio: {tamanio}")
    print(f"revision: {revision}")
    print(f"sub_revision: {sub_revision}")
    print(f"dibujante: {dibujante}")

    if not all([fecha, descripcion, tipo_plano, cod_tipo_plano, tamanio, revision, dibujante]):
        print("Faltan datos obligatorios")
        return redirect(url_for('home'))
    
    # Obtener IDs de las tablas relacionadas
    id_tipo_plano = obtener_tipo_plano(tipo_plano, cod_tipo_plano)
    id_num_plano, num_plano = obtener_siguiente_numero_plano()
    id_tamanio = obtener_tamanio(tamanio)
    id_revision = obtener_revision(revision)
    id_sub_revision = obtener_sub_revision(sub_revision) if sub_revision else None
    
    # Generar identificador del plano
    identificador_plano = generar_identificador_plano(cod_tipo_plano, num_plano, tamanio, revision, sub_revision)
    
    # Procesar archivo si existe
    id_archivo = None
    file = None

    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file = request.files['imagen']

    # Validación del archivo y asignación en base de datos
    if file and file.filename and validar_archivo(file.filename):
        nombre_original = secure_filename(file.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        
        # Generar token único para el archivo
        archivo_token = uuid.uuid4().hex
        
        # Crear nombre único para el archivo en disco
        ruta_archivo = f"{archivo_token}.{extension}"
        ubicacion = os.path.join(UBI_ARCHIVO, ruta_archivo)
        file.save(ubicacion)

        # Determinar tipo MIME
        if extension == 'pdf':
            archivo_mime = 'application/pdf'
        elif extension in ('png', 'jpg', 'jpeg'):
            archivo_mime = 'image/jpeg' if extension in ('jpg', 'jpeg') else f"image/{extension}"
        else:
            archivo_mime = 'application/octet-stream'

        # Guardar información del archivo
        id_archivo = guardar_archivo_info(nombre_original, ruta_archivo, archivo_mime, archivo_token)

    # Inserción en la tabla principal de planos
    cursor = db.database.cursor()
    sql = """INSERT INTO planos
            (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano, 
             id_num_plano, id_tamanio, id_revision, id_sub_revision, id_archivo)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    data = (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano, 
            id_num_plano, id_tamanio, id_revision, id_sub_revision, id_archivo)
    
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    print(f"Plano insertado correctamente con identificador: {identificador_plano}")
    return redirect(url_for('home'))
    
# RUTA PARA ACTUALIZAR DOCUMENTOS
@app.route('/edit/<string:id_plano>', methods=['POST'])
def edit(id_plano):
    """
    Ruta para actualizar un plano existente
    Solo actualiza los campos modificables, mantiene el número de plano original
    """
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    tipo_plano = request.form.get('tipo_plano','').strip()
    cod_tipo_plano = request.form.get('cod_tipo_plano','').strip()[:3]
    tamanio = request.form.get('tamanio','').strip()
    revision = request.form.get('revision','').strip()
    sub_revision = request.form.get('sub_revision','').strip()
    dibujante = request.form.get('dibujante','').strip()

    print(f"DATOS RECIBIDOS PARA ACTUALIZAR:")
    print(f"ID Plano: {id_plano}")
    print(f"Fecha: {fecha}")
    print(f"Descripcion: {descripcion}")
    print(f"Tipo de plano: {tipo_plano}")
    print(f"Codigo tipo: {cod_tipo_plano}")
    print(f"Tamaño: {tamanio}")
    print(f"Revision: {revision}")
    print(f"Sub revision: {sub_revision}")
    print(f"Dibujante: {dibujante}")

    # Obtener el número de plano actual (no se debe cambiar)
    cursor = db.database.cursor()
    cursor.execute("""SELECT np.num_plano, p.id_num_plano, p.id_archivo 
                     FROM planos p 
                     JOIN num_plano np ON p.id_num_plano = np.id_num_plano 
                     WHERE p.id_plano = %s""", (id_plano,))
    result = cursor.fetchone()
    cursor.close()
    
    if not result:
        print("Plano no encontrado")
        return redirect(url_for('home'))
    
    num_plano = result[0]
    id_num_plano_actual = result[1]
    id_archivo_actual = result[2]

    # Obtener IDs de las tablas relacionadas
    id_tipo_plano = obtener_tipo_plano(tipo_plano, cod_tipo_plano) if tipo_plano and cod_tipo_plano else None
    id_tamanio = obtener_tamanio(tamanio) if tamanio else None
    id_revision = obtener_revision(revision) if revision else None
    id_sub_revision = obtener_sub_revision(sub_revision) if sub_revision else None
    
    # Regenerar identificador del plano
    identificador_plano = generar_identificador_plano(cod_tipo_plano, num_plano, tamanio, revision, sub_revision)
    
    # Procesar archivo si se sube uno nuevo
    id_archivo = id_archivo_actual  # Mantener el archivo actual por defecto
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
                except FileNotFoundError:
                    pass

        nombre_original = secure_filename(file.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        
        # Generar nuevo token para el archivo
        archivo_token = uuid.uuid4().hex
        ruta_archivo = f"{archivo_token}.{extension}"
        ubicacion = os.path.join(UBI_ARCHIVO, ruta_archivo)
        file.save(ubicacion)

        # Determinar tipo MIME
        if extension == 'pdf':
            archivo_mime = 'application/pdf'
        elif extension in ('png', 'jpg', 'jpeg'):
            archivo_mime = 'image/jpeg' if extension in ('jpg', 'jpeg') else f'image/{extension}'
        else:
            archivo_mime = 'application/octet-stream'

        # Guardar nueva información del archivo
        id_archivo = guardar_archivo_info(nombre_original, ruta_archivo, archivo_mime, archivo_token)

    # Actualizar plano en la base de datos
    if all([fecha, descripcion, dibujante]):
        cursor = db.database.cursor()
        sql = """UPDATE planos SET 
                identificador_plano=%s, descripcion=%s, dibujante=%s, fecha=%s,
                id_tipo_plano=%s, id_tamanio=%s, id_revision=%s, id_sub_revision=%s, id_archivo=%s
                WHERE id_plano=%s"""
        
        data = (identificador_plano, descripcion, dibujante, fecha,
                id_tipo_plano, id_tamanio, id_revision, id_sub_revision, id_archivo, id_plano)
        
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        
    print(f"Plano actualizado correctamente: {identificador_plano}")
    return redirect(url_for('home'))

# RUTA PARA ELIMINAR
@app.route('/delete/<string:id_plano>')
def delete(id_plano):
    """
    Ruta para eliminar un plano y su archivo asociado
    """
    try:
        cursor = db.database.cursor()
        # Obtener información del archivo
        cursor.execute("""SELECT a.archivo_path, p.id_archivo 
                         FROM planos p 
                         LEFT JOIN archivos a ON p.id_archivo = a.id_archivo 
                         WHERE p.id_plano = %s""", (id_plano,))
        row = cursor.fetchone()
        cursor.close()

        if row and row[0]:
            # Eliminar archivo físico
            try:
                os.remove(os.path.join(UBI_ARCHIVO, row[0]))
            except FileNotFoundError as p:
                print(f'Archivo no encontrado: {p}')
            
            # Eliminar registro de archivo de la base de datos
            if row[1]:
                cursor = db.database.cursor()
                cursor.execute("DELETE FROM archivos WHERE id_archivo = %s", (row[1],))
                db.database.commit()
                cursor.close()
                
    except Exception as p:
        print(f'Error al eliminar archivo: {p}')    
    
    try:
        # Eliminar plano de la base de datos
        cursor = db.database.cursor()
        sql = "DELETE FROM planos WHERE id_plano = %s"
        cursor.execute(sql, (id_plano,))
        db.database.commit()
        cursor.close()
    except Exception as p:
        print(f"Error eliminando plano de la DB: {p}")
    
    return redirect(url_for('home'))

# RUTA PARA VER ARCHIVO CON TOKEN
@app.route('/file/view/<string:token>')
def view_file(token: str):
    """
    Ruta para visualizar un archivo usando su token único
    El token proporciona una capa de seguridad/ofuscación en la URL
    """
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_mime FROM archivos WHERE archivo_token=%s", (token,))
    row = cursor.fetchone()
    cursor.close()
    
    if not row or not row[0]:
        abort(404)
    
    file_on_disk = row[0]
    mime_type = row[1] if row[1] else 'application/octet-stream'

    return send_from_directory(UBI_ARCHIVO, file_on_disk, mimetype=mime_type)

# RUTA PARA DESCARGAR ARCHIVO CON TOKEN
@app.route('/file/download/<string:token>')
def download_file(token: str):
    """
    Ruta para descargar un archivo usando su token único
    Descarga el archivo con su nombre original
    """
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_nombre FROM archivos WHERE archivo_token=%s", (token,))
    row = cursor.fetchone()
    cursor.close()
    
    if not row or not row[0]:
        abort(404)
        
    file_on_disk = row[0]
    file_name = row[1] if row[1] else file_on_disk

    return send_from_directory(UBI_ARCHIVO, file_on_disk, as_attachment=True, download_name=file_name)

# RUTA AUXILIAR PARA OBTENER DATOS DE COMBOS (opcional para frontend)
@app.route('/api/combos')
def get_combos():
    """
    Ruta API para obtener los valores disponibles en las tablas de referencia
    Útil para llenar combos/selects en el frontend
    """
    cursor = db.database.cursor()
    
    # Obtener tipos de plano
    cursor.execute("SELECT id_tipo_plano, tipo_plano, cod_tipo_plano FROM tipo_plano ORDER BY tipo_plano")
    tipos = cursor.fetchall()
    
    # Obtener tamaños
    cursor.execute("SELECT id_tamanio, tamanio FROM tamanio ORDER BY tamanio")
    tamanios = cursor.fetchall()
    
    # Obtener revisiones
    cursor.execute("SELECT id_revision, revision FROM revision ORDER BY revision")
    revisiones = cursor.fetchall()
    
    # Obtener sub-revisiones
    cursor.execute("SELECT id_sub_revision, sub_revision FROM sub_revision ORDER BY sub_revision")
    sub_revisiones = cursor.fetchall()
    
    cursor.close()
    
    return {
        'tipos_plano': [{'id': t[0], 'tipo': t[1], 'codigo': t[2]} for t in tipos],
        'tamanios': [{'id': t[0], 'tamanio': t[1]} for t in tamanios],
        'revisiones': [{'id': r[0], 'revision': r[1]} for r in revisiones],
        'sub_revisiones': [{'id': s[0], 'sub_revision': s[1]} for s in sub_revisiones]
    }

# LANZAMOS APP
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=4000)