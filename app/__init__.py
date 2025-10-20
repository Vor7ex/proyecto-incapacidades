from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db
from app.models.usuario import Usuario
from app.utils.email_service import mail
import os
import logging

logger = logging.getLogger(__name__)
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Crear carpeta de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)  # Inicializar Flask-Mail

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.incapacidades import incapacidades_bp
    from app.routes.documentos import documentos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(incapacidades_bp)
    app.register_blueprint(documentos_bp)

    # Crear tablas (sin usuarios automáticos)
    with app.app_context():
        db.create_all()
        # crear_usuarios_prueba()  # Desactivado - usar crear_usuarios.py

    # Inicializar scheduler de tareas periódicas (UC6)
    # Solo iniciar en producción o si está explícitamente habilitado
    if app.config.get('SCHEDULER_ENABLED', False):
        try:
            from app.tasks.scheduler_uc6 import iniciar_scheduler
            iniciar_scheduler(app)
            logger.info("✅ Scheduler de tareas periódicas iniciado")
        except Exception as e:
            logger.error(f"❌ Error al iniciar scheduler: {str(e)}", exc_info=True)

    return app


def crear_usuarios_prueba():
    """Crea usuarios de prueba si no existen"""
    from app.models.usuario import Usuario

    if Usuario.query.count() == 0:
        # Colaborador de prueba
        colaborador = Usuario(
            nombre='Juan Perez',
            email='colaborador@test.com',
            rol='colaborador'
        )
        colaborador.set_password('123456')

        # Auxiliar de prueba
        auxiliar = Usuario(
            nombre='Maria Garcia',
            email='auxiliar@test.com',
            rol='auxiliar'
        )
        auxiliar.set_password('123456')

        db.session.add(colaborador)
        db.session.add(auxiliar)
        db.session.commit()
        print('Usuarios de prueba creados')
