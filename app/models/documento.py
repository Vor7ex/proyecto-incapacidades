from app.models import db
from datetime import datetime


class Documento(db.Model):
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)
    incapacidad_id = db.Column(db.Integer, db.ForeignKey('incapacidades.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)  # Nombre original del archivo
    nombre_unico = db.Column(db.String(255), nullable=False)  # Nombre único generado (UUID + timestamp)
    ruta = db.Column(db.String(500), nullable=False)  # Ruta completa en servidor
    tipo_documento = db.Column(db.String(50), nullable=False)  # certificado, epicrisis, furips, etc.
    tamaño_bytes = db.Column(db.Integer, nullable=True)  # Tamaño del archivo en bytes
    checksum_md5 = db.Column(db.String(32), nullable=True)  # Hash MD5 del archivo (opcional)
    mime_type = db.Column(db.String(100), nullable=True)  # Tipo MIME del archivo
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Documento {self.nombre_archivo}>'
    
    @property
    def tamaño_mb(self):
        """Retorna el tamaño del archivo en MB"""
        if self.tamaño_bytes:
            return round(self.tamaño_bytes / (1024 * 1024), 2)
        return None
    
    @property
    def extension(self):
        """Retorna la extensión del archivo"""
        if self.nombre_archivo and '.' in self.nombre_archivo:
            return self.nombre_archivo.rsplit('.', 1)[1].lower()
        return None
