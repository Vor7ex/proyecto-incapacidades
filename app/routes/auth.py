from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models import db
from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

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
