from flask import render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import auth_bp
from app.models.user import User
import database as db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para el inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember', False)
        
        if not username or not password:
            return render_template('auth/login.html', 
                                 error='Por favor, completa todos los campos')
        
        try:
            user_data = User.get_by_username(username)
        except Exception as e:
            print(f'ERROR : {e}')
            return render_template('auth/login.html', error='Error interno')
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            session.clear()
            login_user(user_data['user'], remember=bool(remember))
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.home')
            
            return redirect(next_page)
        else:
            return render_template('auth/login.html', 
                                 error='Usuario o contraseña incorrectos')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Ruta para cerrar sesión"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Ruta para registrar nuevos usuarios"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', 'user').strip()
        nombre_completo = request.form.get('nombre_completo', None)
        
        if nombre_completo:
            nombre_completo = nombre_completo.strip()
        
        if not all([username, password]):
            return render_template('auth/registro.html', 
                                 error='Todos los campos son obligatorios')
        
        password_hash = generate_password_hash(password)
        
        try:
            cursor = db.database.cursor()
            cursor.execute("""
                INSERT INTO user (username, password_hash, id_rol, nombre_completo)
                VALUES (%s, %s, %s, %s)
            """, (username, password_hash, int(rol), nombre_completo))
            db.database.commit()
            cursor.close()
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"ERROR: {e}")
            return render_template('auth/registro.html', 
                                 error='El usuario ya existe')
    
    return render_template('auth/registro.html')