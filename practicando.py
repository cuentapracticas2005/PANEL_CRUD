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

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 's5d4fd474fd5frf117481gjh74uk77i4lo5jm581j189ju4mk78ui')

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

@app.route('/')
@login_required
def home():
    fecha = request.args.get('fecha','').strip()
    descripcion = request.args.get('descripcion','').strip()
    identificador = request.args.get('identificador','').strip()
    dibujante = request.args.get('dibujante','').strip()
    revision = request.args.get('revision','').strip()
    sub_revision = request.args.get('sub_revision','').strip()
    tamanio = request.args.get('tamano', '').strip()

    page = int(request.args.get('page',1))
    per_page = 20
    offset = (page - 1) * per_page

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

    cursor = db.database.cursor()
    count_query = "SELECT COUNT(*) FROM (" + base_query + ") AS total"
    cursor.execute(count_query,tuple(params))
    total = cursor.fetchone()[0]

    base_query += " ORDER BY r.id_registro DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute([base_query, tuple(params)])
    tuplas = cursor.fetchall()
    nameColums = [x[0] for x in cursor.description]