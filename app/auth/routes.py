from flask import render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from app.auth import auth_bp
from app.models.user import User
import database as db
'''
Se elaboran las rutas de autenticacion de usuario para iniciar sesion, cerrar sesion y registrar nuevo usuario
'''
# Iniciar sesion
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
            user_data = User.get_by_username(username) # este metodo se trae de models/user.py (busqueda de usuario)
        except Exception as e:
            print(f'ERROR : {e}')
            return render_template('auth/login.html', error='Error interno')
        
        if user_data and check_password_hash(user_data['password_hash'], password): # se accede a la data del metodo a traver del nombre (password_hash)
            session.clear()
            login_user(user_data['user'], remember=bool(remember)) # login_user: funcion que sirve para marcar al usuario como logeado en la sesion actual
            next_page = request.args.get('next') or request.form.get('next') # esta llamda permite que si el usuario queria dirigirse a una seccion sin estar logeago al logearse lo redirja ahi

            parsed = urlparse(next_page or "") # nos ayuda con la verificacion, urlparse convierte la cadena en objeto con partes separadas de la URL

            if not next_page or parsed.netloc != "" or next_page.startswith('//'): # evita redireccion a dominios externos
                next_page = url_for('main.home')
            return redirect(next_page)
        else:
            return render_template('auth/login.html', 
                                 error='Usuario o contraseña incorrectos')
        
    return render_template('auth/login.html')

# Cerrar sesion
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
