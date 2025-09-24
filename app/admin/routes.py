from flask import render_template, redirect, url_for
from flask_login import login_required
from app.admin import admin_bp
import database as db

# Vista de usuarios
@admin_bp.route('/users')
@login_required
def admin_users():
    cursor = db.database.cursor()
    cursor.execute("""
            SELECT 
                u.id_user,
                u.username,
                u.nombre_completo,
                u.activo,
                r.rol
            FROM user u
            LEFT JOIN roles r ON u.id_rol = r.id_rol
        """
    )    
    tuplas = cursor.fetchall()
    nameColumns =[]
    for x in cursor.description:
        nameColumns.append(x[0])

    union = []
    for x in tuplas:
        filas = dict(zip(nameColumns, x))
        union.append(filas)
    cursor.close()

    return render_template('pages/admin_users.html', data=union)

# Eliminar usuarios
@admin_bp.route('/delete_user/<string:id_user>')
@login_required
def delete_user(id_user):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM user WHERE id_user = %s", (id_user,))
    cursor.close()

    return redirect(url_for('admin.admin_users')) # <nombre_del_blueprint>.<nombre_de_la_función>

#Editar usuario
@admin_bp.route('/editar_user/<string:id_user>', methods=['GET','POST'])
@login_required
def edit_user(id_user):
    return redirect(url_for('admin.admin_users'))