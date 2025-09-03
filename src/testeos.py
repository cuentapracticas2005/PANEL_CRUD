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
    upload_path = os.environ.get('UPLOAD_FOLDER')
    
    if not upload_path:
        # carpeta por defecto si no se define UPLOAD_FOLDER
        upload_path = os.path.join(os.path.dirname(__file__), 'uploads')
        print("⚠️  UPLOAD_FOLDER no definido, usando carpeta local")

    # verificar que la carpeta existe y es accesible
    try:
        os.makedirs(upload_path, exist_ok=True) # crea carpeta si no existe
        # Prueba de escritura para validar permisos
        test_file = os.path.join(upload_path, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file) # elimina archivo de prueba
        print(f"✅ Carpeta de uploads configurada: {upload_path}")
    except PermissionError:
        print(f"❌ Sin permisos de escritura en: {upload_path}")
        raise
    except Exception as e:
        print(f"❌ Error al acceder a la carpeta: {e}")
        raise
    
    return upload_path

# FUNCION PARA VERIFICAR PERMISOS
def verificarPermisos(folder_path):
    try:
        # verificar permisos de lectura
        os.listdir(folder_path)
        print(f"✅ Permisos de lectura OK en: {folder_path}")

        # Verificar permisos de escritura
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

# CONFIGURACION DE UPLOADS
UPLOAD_FOLDER = get_upload_folder()             # carpeta donde se almacenaran los archivos subidos
verificarPermisos(UPLOAD_FOLDER)                # verificar permisos de la carpeta
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)       # crear carpeta uploads si no existe

# funcion de seguridad para validacion de extension de archivos
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# =========== FUNCIONES AUXILIARES PARA MANEJO DE TABLAS RELACIONADAS ===========
def get_or_create_tipo_plano(cursor, tipo_plano, cod_tipo_plano):
    """Obtiene o crea un tipo de plano y retorna su ID"""
    # Buscar si ya existe
    cursor.execute("SELECT id_tipo_plano FROM tipo_plano WHERE cod_tipo_plano = %s", (cod_tipo_plano,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # Si no existe, crear nuevo
    cursor.execute("INSERT INTO tipo_plano (tipo_plano, cod_tipo_plano) VALUES (%s, %s)", 
                   (tipo_plano, cod_tipo_plano))
    return cursor.lastrowid

def get_or_create_num_plano(cursor, num_plano):
    """Obtiene o crea un número de plano y retorna su ID"""
    cursor.execute("SELECT id_num_plano FROM num_plano WHERE num_plano = %s", (num_plano,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    cursor.execute("INSERT INTO num_plano (num_plano) VALUES (%s)", (num_plano,))
    return cursor.lastrowid

def get_or_create_tamanio(cursor, tamanio):
    """Obtiene o crea un tamaño y retorna su ID"""
    cursor.execute("SELECT id_tamanio FROM tamanio WHERE tamanio = %s", (tamanio,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    cursor.execute("INSERT INTO tamanio (tamanio) VALUES (%s)", (tamanio,))
    return cursor.lastrowid

def get_or_create_revision(cursor, revision):
    """Obtiene o crea una revisión y retorna su ID"""
    cursor.execute("SELECT id_revision FROM revision WHERE revision = %s", (revision,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    cursor.execute("INSERT INTO revision (revision) VALUES (%s)", (revision,))
    return cursor.lastrowid

def get_or_create_sub_revision(cursor, sub_revision):
    """Obtiene o crea una sub_revisión y retorna su ID"""
    if not sub_revision:
        return None
    
    cursor.execute("SELECT id_sub_revision FROM sub_revision WHERE sub_revision = %s", (sub_revision,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    cursor.execute("INSERT INTO sub_revision (sub_revision) VALUES (%s)", (sub_revision,))
    return cursor.lastrowid

def get_or_create_archivo(cursor, archivo_nombre, archivo_path, archivo_mime):
    """Obtiene o crea un archivo y retorna su ID"""
    if not archivo_nombre:
        return None
    
    cursor.execute("INSERT INTO archivos (archivo_nombre, archivo_path, archivo_mime) VALUES (%s, %s, %s)", 
                   (archivo_nombre, archivo_path, archivo_mime))
    return cursor.lastrowid

# =========== RUTAS DE LA APP =================
@app.route('/')
def home():
    """ Ruta principal, pagina de inicio con filtros usando JOINs para obtener todos los datos"""
    fecha = request.args.get('fecha', '').strip()
    descripcion = request.args.get('descripcion', '').strip()
    numero_plano = request.args.get('numero_plano', '').strip()
    tamano = request.args.get('tamano', '').strip()
    revision = request.args.get('revision', '').strip()
    sub_revision = request.args.get('sub_revision', '').strip()
    dibujante = request.args.get('dibujante', '').strip()

    # Construcción de la consulta con JOINs para obtener todos los datos relacionados
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
            p.archivo_nombre,
            p.archivo_path,
            p.archivo_mime,
            -- Construir el código del plano en SQL
            CONCAT(
                tp.cod_tipo_plano, '-',
                np.num_plano, '-',
                t.tamanio,
                r.revision,
                IFNULL(sr.sub_revision, '')
            ) AS codigo_plano
        FROM planos p
        LEFT JOIN tipo_plano tp ON p.id_tipo_plano = tp.id_tipo_plano
        LEFT JOIN num_plano np ON p.id_num_plano = np.id_num_plano
        LEFT JOIN tamanio t ON p.id_tamanio = t.id_tamanio
        LEFT JOIN revision r ON p.id_revision = r.id_revision
        LEFT JOIN sub_revision sr ON p.id_sub_revision = sr.id_sub_revision
        WHERE 1=1
    """
    
    params = []
    if fecha:
        query += " AND p.fecha = %s"
        params.append(fecha)
    if descripcion:
        query += " AND p.descripcion LIKE %s"
        params.append(f"%{descripcion}%")
    if numero_plano:
        query += " AND np.num_plano LIKE %s"
        params.append(f"%{numero_plano}%")
    if tamano:
        query += " AND t.tamanio = %s"
        params.append(tamano)
    if revision:
        query += " AND r.revision LIKE %s"
        params.append(f"%{revision}%")
    if sub_revision:
        query += " AND sr.sub_revision LIKE %s"
        params.append(f"%{sub_revision}%")
    if dibujante:
        query += " AND p.dibujante LIKE %s"
        params.append(f"%{dibujante}%")

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

# ============== RUTA PARA GUARDAR DOCUMENTOS EN LA DB ==============
@app.route('/user', methods=['POST'])
def addUser():
    # Obtener datos del formulario
    fecha = request.form.get('fecha', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    num_plano = request.form.get('numero_plano', '').strip()
    tipo_plano = request.form.get('tipo_plano', '').strip()
    cod_tipo_plano = request.form.get('cod_tipo_plano', '').strip()  # Asumiendo que también envías el código
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
    print(f"  cod_tipo_plano: '{cod_tipo_plano}'")
    print(f"  tamano: '{tamano}'")
    print(f"  revision: '{revision}'")
    print(f"  sub_revision: '{sub_revision}'")
    print(f"  dibujante: '{dibujante}'")

    # Validación de campos requeridos
    if not all([fecha, descripcion, num_plano, dibujante]):
        print("DEBUG - Faltan campos requeridos")
        return redirect(url_for('home'))

    # Procesamiento del archivo
    archivo_nombre = None
    archivo_path = None
    archivo_mime = None
    file_storage = None

    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file_storage = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file_storage = request.files['imagen']

    if file_storage and file_storage.filename and allowed_file(file_storage.filename):
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

    # Inserción en DB con las nuevas tablas relacionadas
    if all([fecha, descripcion, num_plano, tamano, revision, dibujante]):
        cursor = db.database.cursor()
        
        try:
            # Obtener o crear IDs de las tablas relacionadas
            id_tipo_plano = get_or_create_tipo_plano(cursor, tipo_plano, cod_tipo_plano) if tipo_plano else None
            id_num_plano = get_or_create_num_plano(cursor, num_plano)
            id_tamanio = get_or_create_tamanio(cursor, tamano)
            id_revision = get_or_create_revision(cursor, revision)
            id_sub_revision = get_or_create_sub_revision(cursor, sub_revision) if sub_revision else None
            id_archivo = get_or_create_archivo(cursor, archivo_nombre, archivo_path, archivo_mime) if archivo_nombre else None
            
            # Generar el identificador del plano
            identificador_plano = f"{cod_tipo_plano}-{num_plano}-{tamano}{revision}{sub_revision or ''}"
            
            # Insertar en la tabla principal de planos
            sql = """INSERT INTO planos
                    (identificador_plano, descripcion, dibujante, fecha, 
                     id_tipo_plano, id_num_plano, id_tamanio, id_revision, id_sub_revision, 
                     id_archivo, archivo_nombre, archivo_path, archivo_mime)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            data = (identificador_plano, descripcion, dibujante, fecha,
                   id_tipo_plano, id_num_plano, id_tamanio, id_revision, id_sub_revision,
                   id_archivo, archivo_nombre, archivo_path, archivo_mime)
            
            cursor.execute(sql, data)
            db.database.commit()
            print("DEBUG - Datos insertados correctamente")
            
        except Exception as e:
            print(f"ERROR - Error al insertar datos: {e}")
            db.database.rollback()
        finally:
            cursor.close()
    
    return redirect(url_for('home'))

# ============= RUTA PARA ACTUALIZAR DOCUMENTOS EN LA DB ==============
@app.route('/edit/<string:id_plano>', methods=['POST'])
def edit(id_plano):
    fecha = request.form['fecha']
    descripcion = request.form['descripcion']
    tipo_plano = request.form.get('tipo_plano', '').strip()
    cod_tipo_plano = request.form.get('cod_tipo_plano', '').strip()
    numero_plano = request.form['numero_plano']
    tamano = request.form['tamano']
    revision = request.form['revision']
    sub_revision = request.form.get('sub_revision', '').strip()
    dibujante = request.form['dibujante']

    # Procesamiento del archivo
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
        
        try:
            # Obtener o crear IDs de las tablas relacionadas
            id_tipo_plano = get_or_create_tipo_plano(cursor, tipo_plano, cod_tipo_plano) if tipo_plano else None
            id_num_plano = get_or_create_num_plano(cursor, numero_plano)
            id_tamanio = get_or_create_tamanio(cursor, tamano)
            id_revision = get_or_create_revision(cursor, revision)
            id_sub_revision = get_or_create_sub_revision(cursor, sub_revision) if sub_revision else None
            id_archivo = get_or_create_archivo(cursor, archivo_nombre, archivo_path, archivo_mime) if archivo_nombre else None
            
            # Generar el identificador del plano actualizado
            identificador_plano = f"{cod_tipo_plano}-{numero_plano}-{tamano}{revision}{sub_revision or ''}"
            
            # Actualizar la tabla principal
            if archivo_nombre and archivo_path:
                sql = """UPDATE planos SET 
                        identificador_plano=%s, descripcion=%s, dibujante=%s, fecha=%s,
                        id_tipo_plano=%s, id_num_plano=%s, id_tamanio=%s, id_revision=%s, id_sub_revision=%s,
                        id_archivo=%s, archivo_nombre=%s, archivo_path=%s, archivo_mime=%s
                        WHERE id_plano=%s"""
                data = (identificador_plano, descripcion, dibujante, fecha,
                       id_tipo_plano, id_num_plano, id_tamanio, id_revision, id_sub_revision,
                       id_archivo, archivo_nombre, archivo_path, archivo_mime, id_plano)
            else:
                sql = """UPDATE planos SET 
                        identificador_plano=%s, descripcion=%s, dibujante=%s, fecha=%s,
                        id_tipo_plano=%s, id_num_plano=%s, id_tamanio=%s, id_revision=%s, id_sub_revision=%s
                        WHERE id_plano=%s"""
                data = (identificador_plano, descripcion, dibujante, fecha,
                       id_tipo_plano, id_num_plano, id_tamanio, id_revision, id_sub_revision, id_plano)

            cursor.execute(sql, data)
            db.database.commit()
            
        except Exception as e:
            print(f"ERROR - Error al actualizar datos: {e}")
            db.database.rollback()
        finally:
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
    return send_from_directory(UPLOAD_FOLDER, file_on_disk, as_attachment=True, download_name=original_name)

# Lanzamos la app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=4000)  # host=0.0.0.0 para acceso externo

"""
Explicación de los cambios y cómo funciona la conexión entre tablas:
1. Estructura de la conexión (Relaciones)
Tu base de datos ahora tiene una estructura normalizada donde la tabla planos es la tabla principal que referencia a las demás tablas mediante claves foráneas:
planos (tabla principal)
    ├── id_tipo_plano → tipo_plano
    ├── id_num_plano → num_plano  
    ├── id_tamanio → tamanio
    ├── id_revision → revision
    ├── id_sub_revision → sub_revision
    └── id_archivo → archivos
2. Funciones auxiliares agregadas
Agregué funciones get_or_create_* para cada tabla secundaria. Estas funciones:

Buscan si el valor ya existe en la tabla
Si existe, retornan su ID
Si no existe, lo crean y retornan el nuevo ID

Esto garantiza que no tengas duplicados en tus tablas de catálogo.
3. Consulta principal con JOINs
En la función home(), ahora uso JOINs para unir todas las tablas y obtener los datos completos:
sqlSELECT ... FROM planos p
LEFT JOIN tipo_plano tp ON p.id_tipo_plano = tp.id_tipo_plano
LEFT JOIN num_plano np ON p.id_num_plano = np.id_num_plano
...
Además, construyo el código del plano directamente en SQL usando CONCAT.
4. Proceso de inserción y actualización
Cuando insertas o actualizas un plano:

Primero obtienes/creas los IDs de las tablas secundarias
Generas el identificador_plano concatenando los valores
Insertas en la tabla principal con todas las referencias

5. Ventajas de esta estructura

Sin duplicados: Cada valor único (tipo, tamaño, revisión) se guarda una sola vez
Fácil mantenimiento: Si necesitas cambiar un código de tipo de plano, solo lo cambias en un lugar
Mejor rendimiento: Las búsquedas por índices numéricos son más rápidas
Código dinámico: El código del plano se genera automáticamente
Escalabilidad: Puedes agregar más atributos a cada tabla sin afectar las demás

6. Nota importante sobre las FK (Foreign Keys)
Vi que en tu SQL tienes algunas inconsistencias en los nombres de las constraints. Asegúrate de que las foreign keys coincidan con los nombres de columna correctos en la tabla planos.
¿Necesitas que también te ayude con la plantilla HTML para manejar estos campos adicionales en el formulario?
"""