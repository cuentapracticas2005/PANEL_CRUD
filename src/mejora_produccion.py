from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, flash
import os
import database as db
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv
# CAMBIO: Añadido logging para mejor debugging
import logging
from datetime import datetime

load_dotenv()

# CAMBIO: Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

# CAMBIO: Añadida clave secreta para sesiones y mensajes flash
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configuración de subida de archivos
def get_upload_folder():
    """Obtiene la carpeta de uploads con validaciones"""
    upload_path = os.environ.get('UPLOAD_FOLDER')
    
    if not upload_path:
        # Fallback para desarrollo local
        upload_path = os.path.join(os.path.dirname(__file__), 'uploads')
        logger.warning("UPLOAD_FOLDER no definido, usando carpeta local")
    
    # Verificar que la carpeta existe y es accesible
    try:
        os.makedirs(upload_path, exist_ok=True)
        # Prueba de escritura
        test_file = os.path.join(upload_path, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.info(f"Carpeta de uploads configurada: {upload_path}")
    except PermissionError:
        logger.error(f"Sin permisos de escritura en: {upload_path}")
        raise
    except Exception as e:
        logger.error(f"Error al acceder a la carpeta: {e}")
        raise
    
    return upload_path

# CAMBIO: Mejorada función de verificación de permisos
def verificar_permisos(folder_path):
    """Verifica permisos de la carpeta"""
    try:
        # Verificar lectura
        os.listdir(folder_path)
        logger.info(f"Permisos de lectura OK en: {folder_path}")
        
        # Verificar escritura
        test_file = os.path.join(folder_path, f'permission_test_{uuid.uuid4().hex}.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.info(f"Permisos de escritura OK en: {folder_path}")
        
        return True
    except PermissionError as e:
        logger.error(f"Error de permisos en {folder_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error al verificar {folder_path}: {e}")
        return False

UPLOAD_FOLDER = get_upload_folder()
verificar_permisos(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif"}
# CAMBIO: Añadido tamaño máximo de archivo (16MB)
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB en bytes
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# CAMBIO: Mejorada inicialización de BD con manejo de errores más robusto
def inicializar_columnas_archivo():
    """Inicializa las columnas de archivo en la tabla planos"""
    try:
        cursor = db.database.cursor()
        
        # CAMBIO: Verificar si las columnas existen antes de intentar añadirlas
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'planos' 
            AND COLUMN_NAME IN ('archivo_nombre', 'archivo_path', 'archivo_mime')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        columns_to_add = [
            ("archivo_nombre", "VARCHAR(255)"),
            ("archivo_path", "VARCHAR(300)"),
            ("archivo_mime", "VARCHAR(100)")
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE planos ADD COLUMN {column_name} {column_type} NULL")
                    db.database.commit()
                    logger.info(f"Columna {column_name} añadida exitosamente")
                except Exception as e:
                    logger.warning(f"No se pudo añadir columna {column_name}: {e}")
                    db.database.rollback()
        
        cursor.close()
    except Exception as e:
        logger.error(f"Error al inicializar columnas de archivo: {e}")

# Inicializar columnas al arrancar la aplicación
inicializar_columnas_archivo()

def allowed_file(filename: str) -> bool:
    """Verifica si el archivo tiene una extensión permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def to_null_if_empty(value):
    """
    Convierte string vacío a None para que sea NULL en BD
    
    Args:
        value: Valor del formulario (puede ser None, string, etc.)
    
    Returns:
        None si está vacío (→ NULL en BD)
        String limpio si tiene contenido
    """
    if not value or (isinstance(value, str) and value.strip() == ''):
        return None
    return value.strip() if isinstance(value, str) else value

# CAMBIO: Añadida función para validar fecha
def validar_fecha(fecha_str):
    """Valida que la fecha esté en formato correcto"""
    if not fecha_str:
        return None
    try:
        # Intentar parsear la fecha (ajustar formato según tu necesidad)
        datetime.strptime(fecha_str, '%Y-%m-%d')
        return fecha_str
    except ValueError:
        logger.warning(f"Formato de fecha inválido: {fecha_str}")
        return None

# CAMBIO: Añadida función para manejar archivos de forma segura
def procesar_archivo(file_storage):
    """
    Procesa y guarda un archivo de forma segura
    
    Returns:
        tuple: (archivo_nombre, archivo_path, archivo_mime) o (None, None, None) si hay error
    """
    if not file_storage or not file_storage.filename:
        return None, None, None
    
    if not allowed_file(file_storage.filename):
        logger.warning(f"Tipo de archivo no permitido: {file_storage.filename}")
        return None, None, None
    
    try:
        original_name = secure_filename(file_storage.filename)
        extension = original_name.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_name)
        
        file_storage.save(save_path)
        
        # Determinar MIME type
        mime_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif'
        }
        archivo_mime = mime_types.get(extension, 'application/octet-stream')
        
        logger.info(f"Archivo guardado: {unique_name}")
        return original_name, unique_name, archivo_mime
        
    except Exception as e:
        logger.error(f"Error al procesar archivo: {e}")
        return None, None, None

# Rutas de la app
@app.route('/')
def home():
    # CAMBIO: Corregido para usar request.args (GET) en lugar de request.form (POST)
    fecha = to_null_if_empty(request.args.get('fecha'))
    descripcion = to_null_if_empty(request.args.get('descripcion'))
    numero_plano = to_null_if_empty(request.args.get('numero_plano'))
    tipo_plano = to_null_if_empty(request.args.get('tipo_plano'))
    tamano = to_null_if_empty(request.args.get('tamano'))
    revision = to_null_if_empty(request.args.get('revision'))
    sub_revision = to_null_if_empty(request.args.get('sub_revision'))
    dibujante = to_null_if_empty(request.args.get('dibujante'))
    
    try:
        # Construcción dinámica del WHERE con parámetros para evitar inyección SQL
        query = "SELECT * FROM planos WHERE 1=1"
        params = []
        
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
        
        # CAMBIO: Añadido ORDER BY para ordenar resultados
        query += " ORDER BY fecha DESC, id_plano DESC"
        
        cursor = db.database.cursor()
        cursor.execute(query, tuple(params))
        myresult = cursor.fetchall()
        
        # Convertir los datos a diccionario
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        
        return render_template('index.html', data=insertObject)
        
    except Exception as e:
        logger.error(f"Error al obtener planos: {e}")
        flash('Error al cargar los planos', 'error')
        return render_template('index.html', data=[])

# Ruta para guardar documentos en la BD
@app.route('/user', methods=['POST'])
def addUser():
    try:
        # Obtener datos del formulario
        fecha = validar_fecha(to_null_if_empty(request.form.get('fecha')))
        descripcion = to_null_if_empty(request.form.get('descripcion'))
        num_plano = to_null_if_empty(request.form.get('numero_plano'))
        tipo_plano = to_null_if_empty(request.form.get('tipo_plano'))
        tamano = to_null_if_empty(request.form.get('tamano'))
        revision = to_null_if_empty(request.form.get('revision'))
        sub_revision = to_null_if_empty(request.form.get('sub_revision'))
        dibujante = to_null_if_empty(request.form.get('dibujante'))
        
        # CAMBIO: Logging mejorado
        logger.info(f"Intentando añadir plano: {num_plano}")
        
        # Validación de campos requeridos
        if not all([fecha, descripcion, num_plano, dibujante]):
            flash('Por favor complete todos los campos requeridos', 'warning')
            logger.warning("Faltan campos requeridos")
            return redirect(url_for('home'))
        
        # CAMBIO: Verificar si el número de plano ya existe
        cursor = db.database.cursor()
        cursor.execute("SELECT COUNT(*) FROM planos WHERE num_plano = %s", (num_plano,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            flash(f'El número de plano {num_plano} ya existe', 'warning')
            return redirect(url_for('home'))
        cursor.close()
        
        # Procesamiento de archivo
        archivo_nombre, archivo_path, archivo_mime = procesar_archivo(request.files.get('pdf'))
        
        # Inserción en BD
        cursor = db.database.cursor()
        
        if archivo_nombre and archivo_path:
            sql = """INSERT INTO planos 
                     (fecha, descripcion, tipo_plano, num_plano, tamanio, revision, sub_revision, dibujante, 
                      archivo_nombre, archivo_path, archivo_mime) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (fecha, descripcion, tipo_plano, num_plano, tamano, revision, sub_revision, dibujante, 
                   archivo_nombre, archivo_path, archivo_mime)
        else:
            sql = """INSERT INTO planos 
                     (fecha, descripcion, tipo_plano, num_plano, tamanio, revision, sub_revision, dibujante) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (fecha, descripcion, tipo_plano, num_plano, tamano, revision, sub_revision, dibujante)
        
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        
        flash('Plano añadido exitosamente', 'success')
        logger.info(f"Plano {num_plano} insertado correctamente")
        
    except Exception as e:
        logger.error(f"Error al añadir plano: {e}")
        flash('Error al añadir el plano', 'error')
        if 'cursor' in locals():
            db.database.rollback()
    
    return redirect(url_for('home'))

# Ruta para actualizar documentos en la BD
@app.route('/edit/<string:id_plano>', methods=['POST'])
def edit(id_plano):
    try:
        # CAMBIO: Validación de ID
        if not id_plano or not id_plano.isdigit():
            flash('ID de plano inválido', 'error')
            return redirect(url_for('home'))
        
        fecha = validar_fecha(to_null_if_empty(request.form.get('fecha')))
        descripcion = to_null_if_empty(request.form.get('descripcion'))
        numero_plano = to_null_if_empty(request.form.get('numero_plano'))
        tipo_plano = to_null_if_empty(request.form.get('tipo_plano'))
        tamano = to_null_if_empty(request.form.get('tamano'))
        revision = to_null_if_empty(request.form.get('revision'))
        sub_revision = to_null_if_empty(request.form.get('sub_revision'))
        dibujante = to_null_if_empty(request.form.get('dibujante'))
        
        # Validación de campos requeridos
        if not all([fecha, descripcion, numero_plano, dibujante]):
            flash('Por favor complete todos los campos requeridos', 'warning')
            return redirect(url_for('home'))
        
        # CAMBIO: Verificar que el plano existe
        cursor = db.database.cursor()
        cursor.execute("SELECT archivo_path FROM planos WHERE id_plano = %s", (id_plano,))
        existing = cursor.fetchone()
        if not existing:
            cursor.close()
            flash('Plano no encontrado', 'error')
            return redirect(url_for('home'))
        old_file = existing[0]
        cursor.close()
        
        # Procesar nuevo archivo si se proporciona
        archivo_nombre = archivo_path = archivo_mime = None
        file_storage = request.files.get('pdf') or request.files.get('imagen')
        if file_storage and file_storage.filename:
            archivo_nombre, archivo_path, archivo_mime = procesar_archivo(file_storage)
            
            # CAMBIO: Eliminar archivo anterior si se sube uno nuevo
            if archivo_path and old_file:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, old_file))
                    logger.info(f"Archivo anterior eliminado: {old_file}")
                except FileNotFoundError:
                    pass
        
        cursor = db.database.cursor()
        if archivo_nombre and archivo_path:
            sql = """UPDATE planos SET fecha=%s, descripcion=%s, tipo_plano=%s, num_plano=%s, 
                     tamanio=%s, revision=%s, sub_revision=%s, dibujante=%s, 
                     archivo_nombre=%s, archivo_path=%s, archivo_mime=%s WHERE id_plano=%s"""
            data = (fecha, descripcion, tipo_plano, numero_plano, tamano, revision, sub_revision, 
                   dibujante, archivo_nombre, archivo_path, archivo_mime, id_plano)
        else:
            sql = """UPDATE planos SET fecha=%s, descripcion=%s, tipo_plano=%s, num_plano=%s, 
                     tamanio=%s, revision=%s, sub_revision=%s, dibujante=%s WHERE id_plano=%s"""
            data = (fecha, descripcion, tipo_plano, numero_plano, tamano, revision, sub_revision, 
                   dibujante, id_plano)
        
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        
        flash('Plano actualizado exitosamente', 'success')
        logger.info(f"Plano {id_plano} actualizado")
        
    except Exception as e:
        logger.error(f"Error al actualizar plano: {e}")
        flash('Error al actualizar el plano', 'error')
        if 'cursor' in locals():
            db.database.rollback()
    
    return redirect(url_for('home'))

# Ruta para eliminar documentos de la BD
@app.route('/delete/<string:id_plano>')
def delete(id_plano):
    try:
        # CAMBIO: Validación de ID
        if not id_plano or not id_plano.isdigit():
            flash('ID de plano inválido', 'error')
            return redirect(url_for('home'))
        
        cursor = db.database.cursor()
        
        # Obtener información del archivo antes de eliminar
        cursor.execute("SELECT archivo_path, num_plano FROM planos WHERE id_plano=%s", (id_plano,))
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            flash('Plano no encontrado', 'error')
            return redirect(url_for('home'))
        
        archivo_path = row[0]
        num_plano = row[1]
        
        # Eliminar registro de la BD
        cursor.execute("DELETE FROM planos WHERE id_plano=%s", (id_plano,))
        db.database.commit()
        
        # Eliminar archivo del disco si existe
        if archivo_path:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, archivo_path))
                logger.info(f"Archivo eliminado: {archivo_path}")
            except FileNotFoundError:
                logger.warning(f"Archivo no encontrado: {archivo_path}")
        
        cursor.close()
        flash(f'Plano {num_plano} eliminado exitosamente', 'success')
        logger.info(f"Plano {id_plano} eliminado")
        
    except Exception as e:
        logger.error(f"Error al eliminar plano: {e}")
        flash('Error al eliminar el plano', 'error')
        if 'cursor' in locals():
            db.database.rollback()
    
    return redirect(url_for('home'))

# Ruta para ver archivo en el navegador
@app.route('/file/view/<string:id_plano>')
def view_file(id_plano: str):
    try:
        # CAMBIO: Validación de ID
        if not id_plano or not id_plano.isdigit():
            abort(404)
        
        cursor = db.database.cursor()
        cursor.execute("SELECT archivo_path, archivo_mime FROM planos WHERE id_plano=%s", (id_plano,))
        row = cursor.fetchone()
        cursor.close()
        
        if not row or not row[0]:
            abort(404)
        
        file_on_disk = row[0]
        mime_type = row[1] if row[1] else 'application/octet-stream'
        
        # CAMBIO: Verificar que el archivo existe
        file_path = os.path.join(UPLOAD_FOLDER, file_on_disk)
        if not os.path.exists(file_path):
            logger.error(f"Archivo no encontrado: {file_path}")
            abort(404)
        
        return send_from_directory(UPLOAD_FOLDER, file_on_disk, mimetype=mime_type)
        
    except Exception as e:
        logger.error(f"Error al ver archivo: {e}")
        abort(500)

# Ruta para descargar archivo
@app.route('/file/download/<string:id_plano>')
def download_file(id_plano: str):
    try:
        # CAMBIO: Validación de ID
        if not id_plano or not id_plano.isdigit():
            abort(404)
        
        cursor = db.database.cursor()
        cursor.execute("SELECT archivo_path, archivo_nombre FROM planos WHERE id_plano=%s", (id_plano,))
        row = cursor.fetchone()
        cursor.close()
        
        if not row or not row[0]:
            abort(404)
        
        file_on_disk = row[0]
        original_name = row[1] if row[1] else file_on_disk
        
        # CAMBIO: Verificar que el archivo existe
        file_path = os.path.join(UPLOAD_FOLDER, file_on_disk)
        if not os.path.exists(file_path):
            logger.error(f"Archivo no encontrado: {file_path}")
            abort(404)
        
        return send_from_directory(UPLOAD_FOLDER, file_on_disk, as_attachment=True, download_name=original_name)
        
    except Exception as e:
        logger.error(f"Error al descargar archivo: {e}")
        abort(500)

# CAMBIO: Añadido manejador de errores
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.database.rollback()
    return render_template('500.html'), 500

# CAMBIO: Añadido manejador para archivos muy grandes
@app.errorhandler(413)
def too_large(error):
    flash('El archivo es demasiado grande. Máximo 16MB', 'error')
    return redirect(url_for('home'))

# Lanzamos la app
if __name__ == '__main__':
    # CAMBIO: Configuración mejorada para producción/desarrollo
    is_production = os.environ.get('FLASK_ENV') == 'production'
    app.run(
        host='0.0.0.0',
        debug=not is_production,  # Debug solo en desarrollo
        port=int(os.environ.get('PORT', 4000))
    )