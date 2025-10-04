from app.models import db
from datetime import datetime


class Documento(db.Model):
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)
    incapacidad_id = db.Column(db.Integer, db.ForeignKey('incapacidades.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta = db.Column(db.String(500), nullable=False)
    tipo_documento = db.Column(db.String(50), nullable=False)  # 'certificado' o 'epicrisis'
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Documento {self.nombre_archivo}>'
