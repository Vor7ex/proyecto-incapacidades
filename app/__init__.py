from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db
from app.models.usuario import Usuario

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

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

    # Crear tablas y usuarios de prueba
    with app.app_context():
        db.create_all()
        crear_usuarios_prueba()

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
