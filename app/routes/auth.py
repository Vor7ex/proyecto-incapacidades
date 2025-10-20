from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.models import db
from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)


def require_role(*roles):
    """
    Decorador para proteger rutas por rol.
    
    Uso:
        @require_role('auxiliar')
        @require_role('colaborador', 'admin')
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.rol not in roles:
                flash(f'Acceso denegado. Se requiere rol: {", ".join(roles)}', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)

            # Redirigir según rol
            if usuario.rol == 'colaborador':
                return redirect(url_for('incapacidades.mis_incapacidades'))
            elif usuario.rol == 'auxiliar':
                return redirect(url_for('incapacidades.dashboard_auxiliar'))
            else:
                flash('Rol de usuario no reconocido', 'danger')
                logout_user()
                return redirect(url_for('auth.login'))
        else:
            flash('Email o contraseña incorrectos', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
