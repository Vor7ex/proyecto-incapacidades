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