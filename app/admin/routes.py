from flask import render_template, redirect, url_for, request
from flask_login import login_required
from app.admin import admin_bp
from werkzeug.security import generate_password_hash
import database as db

# Vista de usuarios
@admin_bp.route('/users')
@login_required
def admin_users():
    username = request.args.get('username', '').strip()    
    cursor = db.database.cursor(dictionary=True)

    params = []
    query = """
            SELECT 
                u.id_user,
                u.username,
                u.nombre_completo,
                u.activo,
                r.rol
            FROM user u
            LEFT JOIN roles r ON u.id_rol = r.id_rol
            WHERE r.rol != 'admin'
        """
    if username:
        query += " AND u.username LIKE %s"
        params.append(f"%{username}%")

    cursor.execute(query,tuple(params))
    union = cursor.fetchall()
    cursor.close()

    return render_template('pages/admin_users.html', data=union)

# Eliminar usuarios
@admin_bp.route('/delete_user/<string:id_user>')
@login_required
def delete_user(id_user):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM user WHERE id_user = %s", (id_user,))
    db.database.commit()
    cursor.close()

    return redirect(url_for('admin.admin_users')) # <nombre_del_blueprint>.<nombre_de_la_función>

#Editar usuario
@admin_bp.route('/editar_user/<string:id_user>', methods=['GET','POST'])
@login_required
def edit_user(id_user):
    cursor = db.database.cursor()

    if request.method == 'POST':
        nombre = request.form.get('nombre_completo','').strip()
        usuario = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', '').strip()

        cursor.execute("SELECT username FROM user WHERE username=%s AND id_user!=%s", (usuario, id_user))
        existe = cursor.fetchone()
        if existe:
            cursor.close()
            return "El username ya está en uso", 400

        update_query = "UPDATE user SET nombre_completo=%s, username=%s, id_rol=%s"
        params = [nombre, usuario, rol]

        if password:
            password_hash = generate_password_hash(password)
            update_query += ", password_hash=%s"
            params.append(password_hash)

        update_query += " WHERE id_user=%s"
        params.append(id_user)

        try:
            cursor.execute(update_query, tuple(params))
            db.database.commit()
        except Exception as e:
            db.database.rollback()
            print(f"Error: {e}")
            raise
        finally:
            cursor.close()

        return redirect(url_for('admin.admin_users'))

    # Si es GET, traer datos del usuario y mostrarlos
    cursor.execute("SELECT nombre_completo, username, id_rol FROM user WHERE id_user=%s", (id_user,))
    usuario = cursor.fetchone()
    cursor.close()

    return render_template('editar_user.html', usuario=usuario)

# Estado de usuario
@admin_bp.route('/estado_user/<string:id_user>', methods=['POST'])
@login_required
def estado_user(id_user):
    estado = request.form.get('estado','').strip()

    if estado not in ['0', '1']:
        return "ESTADO INVALIDO", 400

    cursor = db.database.cursor()
    cursor.execute("UPDATE user SET activo=%s WHERE id_user=%s",(int(estado), id_user))
    db.database.commit()
    cursor.close()
    return redirect(url_for('admin.admin_users'))

    