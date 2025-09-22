from flask import send_from_directory, abort
from flask_login import login_required
from app.archivos import archivos_bp
from app.archivos.utils import get_upload_folder
import database as db

@archivos_bp.route('/view/<string:token>')
@login_required
def view_file(token: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_mime FROM archivos WHERE archivo_token = %s", 
                  (token,))
    row = cursor.fetchone()
    cursor.close()
    
    if not row or not row[0]:
        abort(404)
    
    file_on_disk = row[0]
    mime_type = row[1] if row[1] else None
    UBI_ARCHIVO = get_upload_folder()
    
    return send_from_directory(UBI_ARCHIVO, file_on_disk, mimetype=mime_type)

@archivos_bp.route('/download/<string:token>')
@login_required
def download_file(token: str):
    cursor = db.database.cursor()
    cursor.execute("SELECT archivo_path, archivo_nombre FROM archivos WHERE archivo_token = %s", 
                  (token,))
    row = cursor.fetchone()
    cursor.close()
    
    if not row or not row[0]:
        abort(404)

    file_on_disk = row[0]
    file_name = row[1] if row[1] else file_on_disk
    UBI_ARCHIVO = get_upload_folder()
    
    return send_from_directory(UBI_ARCHIVO, file_on_disk, as_attachment=True, 
                             download_name=file_name)