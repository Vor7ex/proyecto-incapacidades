from app.models import db
from datetime import datetime


class Incapacidad(db.Model):
    __tablename__ = 'incapacidades'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'Enfermedad General' o 'Accidente Laboral'
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    dias = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(30), default='Pendiente')  # Pendiente, En revisión, Aprobada, Rechazada
    motivo_rechazo = db.Column(db.Text, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relación con documentos
    documentos = db.relationship(
        'Documento',
        backref='incapacidad',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Incapacidad {self.id} - {self.tipo}>'
