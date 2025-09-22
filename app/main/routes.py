from flask import render_template, request
from flask_login import login_required
from app.main import main_bp
import database as db

@main_bp.route('/')
@login_required
def home():
    # Parámetros de búsqueda
    fecha = request.args.get('fecha','').strip()
    descripcion = request.args.get('descripcion','').strip()
    identificador = request.args.get('identificador_plano','').strip()
    dibujante = request.args.get('dibujante','').strip()
    revision = request.args.get('revision','').strip()
    sub_revision = request.args.get('sub_revision','').strip()
    tamanio = request.args.get('tamano','').strip()

    # Paginación
    page = int(request.args.get('page', 1))
    max_registros = 10
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

    # Obtener total de registros
    cursor = db.database.cursor()
    count_query = "SELECT COUNT(*) FROM (" + base_query + ") AS total"
    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()[0]
    
    # Agregar paginación
    base_query += " ORDER BY r.id_registro DESC LIMIT %s OFFSET %s"
    params.extend([max_registros, offset])
    cursor.execute(base_query, tuple(params))
    tuplas = cursor.fetchall()
    
    nameColums = [x[0] for x in cursor.description]
    union = [dict(zip(nameColums, row)) for row in tuplas]
    cursor.close()
    
    # Validación de identificadores duplicados
    cursor = db.database.cursor()
    cursor.execute("SELECT id_registro, identificador_plano FROM registros")
    registros = cursor.fetchall()
    lista_identificadores = [{"id": r[0], "identificador": r[1]} for r in registros]
    cursor.close()

    total_pages = (total + max_registros - 1) // max_registros

    return render_template(
        'main/home.html',
        data=union,
        lista_identificadores=lista_identificadores,
        page=page,
        total_pages=total_pages
    )