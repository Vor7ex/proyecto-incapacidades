import os

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-dev'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOAD_FOLDER = 'app/static/uploads'
	MAX_CONTENT_LENGTH = 10 * 1024 * 1024 # 10MB max
	ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}