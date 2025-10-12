import os

# Obtener la ruta base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-dev'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
	MAX_CONTENT_LENGTH = 10 * 1024 * 1024 # 10MB max
	ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
	
	# Configuración de sesiones
	SESSION_PERMANENT = False  # Las sesiones expiran al cerrar el navegador
	SESSION_TYPE = 'filesystem'  # Almacenar sesiones en filesystem
	
	# Configuración de correo electrónico (UC2: Notificaciones)
	MAIL_ENABLED = os.environ.get('MAIL_ENABLED', 'true').lower() in ['true', 'on', '1']
	MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@incapacidades.com'
	
	# Emails de notificación
	ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@empresa.com'
	GESTION_HUMANA_EMAIL = os.environ.get('GESTION_HUMANA_EMAIL') or 'gestionhumana@empresa.com'