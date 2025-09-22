from flask import Flask, request, render_template, redirect, url_for, abort, send_from_directory, session
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
import uuid
import database as db
import os
load_dotenv()

app = Flask(
    __name__,
    static_folder = os.path.join(os.path.dirname(__file__),'static'),
    template_folder = os.path.join(os.path.dirname(__file__),'templates')
)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'para-desarrollo')

# Inicializar LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Ruta a donde redirigir si no está autenticado
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'  # Para usar con flash messages

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
    cursor.execute("SELECT id_tipo_plano FROM tipo_plano WHERE cod_tipo_plano = %s", (cod_tipo_plano,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def obtener_siguiente_numero():
    cursor = db.database.cursor()
    cursor.execute("INSERT INTO num_plano (id_num_plano) VALUES (NULL)")
    db.database.commit()
    id_num_plano = cursor.lastrowid

    cursor.execute("SELECT id_num_plano FROM num_plano WHERE id_num_plano = %s", (id_num_plano,))
    x = cursor.fetchone()
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
    cursor.execute("SELECT id_sub_revision FROM sub_revision WHERE sub_revision = %s", (sub_revision,))
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

# ==================== RUTAS DE LA APP =============================

# RUTA DE AUTENTICACION DE USUARIO
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para el inicio de sesión"""
    # Si el usuario ya está autenticado, redirigir al home
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember', False)  # Checkbox "recordarme"
        # Validación básica
        if not username or not password:
            # Aquí podrías usar flash() para mostrar mensajes
            return render_template('login.html', error='Por favor, completa todos los campos')
        
        # Buscar usuario en la base de datos
        try:
            user_data = User.get_by_username(username)
        except Exception as e:
            print(f'ERROR : {e}')
            return render_template('login.html', error='Error interno')
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            session.clear()
            # Login exitoso
            login_user(user_data['user'], remember=bool(remember))

            # Redirigir a la página que el usuario intentaba acceder o al home
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('home')
            
            return redirect(next_page)
        else:
            # Login fallido
            return render_template('login.html', error='Usuario o contraseña incorrectos')
    
    return render_template('login.html')

# RUTA PARA CERRAR SESION
@app.route('/logout')
@login_required
def logout():
    """Ruta para cerrar sesión"""
    logout_user()
    return redirect(url_for('login'))

# RUTA PARA REGISTRAR USUARIOS
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Ruta para registrar nuevos usuarios (opcional)"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', 'user').strip()
        nombre_completo = request.form.get('nombre_completo', None).strip()
        # Validaciones
        if not all([username, password]):
            return render_template('registro.html', error='Todos los campos son obligatorios')
        
        # Generar hash de la contraseña
        password_hash = generate_password_hash(password)
        
        try:
            cursor = db.database.cursor()
            cursor.execute("""
                INSERT INTO user (username, password_hash, id_rol, nombre_completo)
                VALUES (%s, %s, %s, %s)
            """, (username, password_hash, int(rol), nombre_completo))
            db.database.commit()
            cursor.close()
            return redirect(url_for('login'))
        except Exception as e:
            # Manejar errores (usuario duplicado, etc.)
            print(f"ERROR: {e}")
            return render_template('registro.html', error='El usuario ya existe')
    
    return render_template('registro.html')

# RUTA HOME
@app.route('/')
@login_required
def home():
    fecha = request.args.get('fecha','').strip()
    descripcion = request.args.get('descripcion','').strip()
    identificador = request.args.get('identificador_plano','').strip()
    dibujante = request.args.get('dibujante','').strip()
    revision = request.args.get('revision','').strip()
    sub_revision = request.args.get('sub_revision','').strip()
    tamanio = request.args.get('tamano','').strip()

    # Paginación
    page = int(request.args.get('page', 1))  # Página actual
    max_registros = 100  # Número de registros por página
    offset = (page - 1) * max_registros

    # Construcción de la query
    base_query = """
        SELECT 
            r.id_registro,
            r.identificador_plano,
            r.descripcion,
            r.dibujante,
            r.fecha,
            tp.tipo_plano,
            tp.cod_tipo_plano,
            np.id_num_plano,
            t.tamanio,
            v.revision,
            sr.sub_revision,
            a.archivo_nombre,
            a.archivo_token
        FROM registros r
        LEFT JOIN tipo_plano tp ON r.id_tipo_plano = tp.id_tipo_plano
        LEFT JOIN num_plano np ON r.id_num_plano = np.id_num_plano
        LEFT JOIN tamanio t ON r.id_tamanio = t.id_tamanio
        LEFT JOIN revision v ON r.id_revision = v.id_revision
        LEFT JOIN sub_revision sr ON r.id_sub_revision = sr.id_sub_revision
        LEFT JOIN archivos a ON r.id_archivo = a.id_archivo
        WHERE 1=1
    """
    params = []

    if fecha:
        base_query += " AND r.fecha = %s"
        params.append(fecha)
    if descripcion:
        base_query += " AND r.descripcion LIKE %s"
        params.append(f"%{descripcion}%")
    if identificador:
        base_query += " AND r.identificador_plano LIKE %s"
        params.append(f"%{identificador}%")
    if dibujante:
        base_query += " AND r.dibujante LIKE %s"
        params.append(f"%{dibujante}%")
    if revision:
        base_query += " AND v.revision = %s"
        params.append(revision)
    if sub_revision:
        base_query += " AND sr.sub_revision = %s"
        params.append(sub_revision)
    if tamanio:
        base_query += " AND t.tamanio = %s"
        params.append(tamanio)

    # Obtener total de registros sin LIMIT
    cursor = db.database.cursor()
    count_query = "SELECT COUNT(*) FROM (" + base_query + ") AS total"
    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()[0]
    
    # Agregar paginación a la consulta
    base_query += " ORDER BY r.id_registro DESC LIMIT %s OFFSET %s"
    params.extend([max_registros, offset])
    cursor.execute(base_query, tuple(params))
    tuplas = cursor.fetchall()
    nameColums = []
    for x in cursor.description:
        nameColums.append(x[0])

    # Se ordena todo en una lista de diccionarios 
    union = []
    for x in tuplas:
        fila = dict(zip(nameColums, x))
        union.append(fila)
    cursor.close()
    
    # Para la validación de identificadores duplicados
    cursor = db.database.cursor()
    cursor.execute("SELECT id_registro, identificador_plano FROM registros")
    registros = cursor.fetchall()
    lista_identificadores = [{"id": r[0], "identificador": r[1]} for r in registros]
    cursor.close()

    total_pages = (total + max_registros - 1) // max_registros  # redondeo hacia arriba

    return render_template(
        'home.html',
        data=union,
        lista_identificadores=lista_identificadores,
        page=page,
        total_pages=total_pages
    )

# RUTA PARA ADMINISTRAR USUARIOS
@app.route('/admin')
@login_required
def admin_users():
    return render_template('pages/admin_users.html')

# RUTA PARA GUARDAR/REUTILIZAR REGISTROS
@app.route('/user', methods=['POST'])
@login_required
def addUser():
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    numero_plano_rep = request.form.get('numero_plano','').strip()
    identificador_plano_rep = request.form.get('identificador_plano','').strip()
    cod_tipo_plano = request.form.get('tipo_plano','').strip()
    tamanio = request.form.get('tamano','').strip()
    revision = request.form.get('revision','').strip()
    sub_revision = request.form.get('sub_revision','').strip()
    dibujante = request.form.get('dibujante','').strip()
    
    print(f"DATOS RECIBIDOS: ")
    print(f"fecha: {fecha}")
    print(f"numero_plano: {numero_plano_rep}")
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
    
    id_tamanio = obtener_tamanio(tamanio)
    id_revision = obtener_revision(revision)
    id_sub_revision = obtener_sub_revision(sub_revision) if sub_revision else None

    # ---------------------------------------- PARA DIFERENCIAR: num_plano ---------------------------------------------
    
    cursor = db.database.cursor()
    cursor.execute("SELECT id_num_plano FROM num_plano")
    x = cursor.fetchall()
    contenedor = False
    identificador_plano = None
    id_num_plano = None
    for y in x:
        if str(numero_plano_rep) == str(y[0]):
            contenedor = True
            break
        else:
            contenedor = False
    if contenedor:
        identificador_plano = generar_identificador_plano(cod_tipo_plano, numero_plano_rep, tamanio, revision, sub_revision)
        id_num_plano = numero_plano_rep
    else:
        id_num_plano_nuevo = obtener_siguiente_numero()
        identificador_plano = generar_identificador_plano(cod_tipo_plano, id_num_plano_nuevo, tamanio, revision, sub_revision)
        id_num_plano = id_num_plano_nuevo
    
    # -----------------------------------------------------------------------------------------------------------------

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
        
    # --------------------------------------- PARA DIFERENCIA identificador_plano ----------------------------------------------
    cursor = db.database.cursor()
    cursor.execute("SELECT identificador_plano FROM registros")
    x = cursor.fetchall()
    for y in x:
        if str(identificador_plano).strip() == str(identificador_plano_rep):
            print("ESTE IDENTIFICADOR DE PLANO YA EXISTE")
            break
        else:
            sql = """INSERT INTO registros
                    (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano,
                    id_num_plano, id_tamanio, id_revision, id_sub_revision, id_archivo)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (identificador_plano, descripcion, dibujante, fecha, id_tipo_plano,
                    id_num_plano, id_tamanio, id_revision, id_sub_revision, id_archivo)
            cursor.execute(sql, data)
            db.database.commit()
            cursor.close()
            print(f"Plano e identificador insertado en la base de datos correctamente: {identificador_plano}")
            return redirect(url_for('home'))
    
# RUTA PARA ACTUALIZAR REGISTROS
@app.route('/edit/<string:id_registro>', methods=['POST'])
@login_required
def edit(id_registro):
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
    return redirect(url_for('home'))
        
# RUTA PARA ELIMINAR REGISTROS
@app.route('/delete/<string:id_registro>')
@login_required
def delete(id_registro):
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

    return redirect(url_for('home'))

# RUTA PARA VER ARCHIVO
@app.route('/file/view/<string:token>')
@login_required
def view_file(token: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_mime FROM archivos WHERE archivo_token = %s", (token,))
    row = cursor.fetchone()
    cursor.close()
    if not row or not row[0]:
        abort(404)
    
    file_on_disk = row[0]
    mime_type = row[1] if row[1] else None

    if row is None:
        return None
    return send_from_directory(UBI_ARCHIVO, file_on_disk, mimetype=mime_type)

# RUTA PARA DESCARGR ARCHIVO
@app.route('/file/download/<string:token>')
@login_required
def download_file(token: str):
    cursor = db.database.cursor()
    cursor.execute("""SELECT archivo_path, archivo_nombre FROM archivos WHERE archivo_token = %s""", (token,))
    row = cursor.fetchone()
    cursor.close()
    if not row or not row[0]:
        abort(404)

    file_on_disk = row[0]
    file_name = row[1] if row[1] else file_on_disk

    if row is None:
        return None
    return send_from_directory(UBI_ARCHIVO, file_on_disk, as_attachment=True, download_name=file_name)

# CALLBACK PARA CARGAR EL USUARIO
@login_manager.user_loader
def load_user(user_id):
    """
    Esta función es llamada por Flask-Login en cada petición
    para cargar el usuario actual desde la sesión.
    """
    return User.get_by_id(int(user_id))

# LANZAR APP
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=4000)

# <!-- {{ form.hidden_tag() }} -->