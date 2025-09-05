from flask import Flask, request, render_template, redirect, url_for
import os
from dotenv import load_dotenv
import database as db
load_dotenv()

app = Flask(
    __name__,
    static_folder = os.path.join(os.path.dirname(__file__),'static'),
    template_folder = os.path.join(os.path.dirname(__file__),'temaplates')
)

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

UPLOAD_FOLDER = comprobar_archivos
ALL_EXTENSIONS = {"pdf","png","jpg","jpeg"}

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
    try:
        cursor = db.database.cursor()
        for stm in[
            'ALTER TABLE planos ADD COLUMN archivo_nombre VARCHAR(255) NULL',
            'ALTER TABLE planos ADD COLUMN archivo_path VARCHAR(300) NULL',
            'ALTER TABLE planos ADD COLUMN archivo_mime VARCHAR(100) NULL',
        ]:
            try:  
                cursor.execute(stm)
                db.database.commit()
            except Exception:
                pass
        cursor.close()
    except Exception:
        pass

def validar_archivo(filename: str)->bool:
    valor = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALL_EXTENSIONS
    return valor

# ==================== RUTAS DE LA APP ============================

@app.route('/')
def home():
    fecha = request.args.get('fecha','').strip()
    descripcion = request.args.get('descripcion','').strip()
    numero_plano = request.args.get('numero_plano','').strip()
    tamano = request.args.get('tamano').strip()
    revision = request.args.get('revision','').strip()
    sub_revision = request.args.get('sub_revision','').strip()
    dibujante = request.args.get('dibujante','').strip()

    query = "SELECT * FROM planos WHERE 1=1"
    params = []

    if fecha:
        query += " AND fecha = %s"
        params.append(fecha)
    if descripcion:
        query += " AND descripcion = %s"
        params.append(descripcion)
    if numero_plano:
        query+= " AND numero_plano LIKE %s"
        params.append(f"%{numero_plano}%")
    if tamano:
        query += " AND tamano = %s"
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

    query += " ORDER BY id_plano DESC"

    cursor = db.database.cursor()
    cursor.execute(query, tuple(params))
    tuplas = cursor.fetchall()

    nameColumns = []
    for x in cursor.description:
        nameColumns.append(x[0])
    
    union = []
    for x in tuplas:
        union.append(dict(zip(nameColumns, x)))
    
    return render_template('index.html', data=union)

# RUTA PARA GUARDAR DATOS
@app.route('/user', methods=['POST'])
def addData():
    fecha = request.form.get('fecha','').strip()
    descripcion = request.form.get('descripcion','').strip()
    num_plano = request.form.get('num_plano','').strip()
    tipo_plano = request.form.get('tipo_plano','').strip()
    tamano = request.form.get('tamano','').strip()
    revision = request.form.get('revision','').strip()
    sub_revision = request.form.get('sub_revision','').strip()
    dibujante = request.form.get('dibujante','').strip()

    print(f"DATOS RECIBIDOS:")
    print(f"fecha: {fecha}")
    print(f"descripcion: {descripcion}")
    print(f"num_plano: {num_plano}")
    print(f"tipo_plano: {tipo_plano}")
    print(f"tamano: {tamano}")
    print(f"revision: {revision}")
    print(f"sub_revision: {sub_revision}")
    print(f"dibujante: {dibujante}")

    if not all([fecha, descripcion, num_plano, tipo_plano, tamano, revision, sub_revision, dibujante]):
        print("Faltan datos")
        return redirect(url_for('home'))
    
    archivo_nombre = None
    archivo_path = None
    archivo_mime = None

    if 'pdf' in request.files and request.files['pdf'] and request.files['pdf'].filename:
        file_storage = request.files['pdf']
    elif 'imagen' in request.files and request.files['imagen'] and request.files['imagen'].filename:
        file_storage = request.files['imagen']