from app.models import db
from datetime import datetime

# Constantes de tipos de incapacidad según UC1
TIPOS_INCAPACIDAD = {
    'enfermedad_general': 'Enfermedad General',
    'accidente_laboral': 'Accidente Laboral',
    'accidente_transito': 'Accidente de Tránsito',
    'licencia_maternidad': 'Licencia de Maternidad',
    'licencia_paternidad': 'Licencia de Paternidad'
}

# Lista de valores válidos para validación
TIPOS_VALIDOS = list(TIPOS_INCAPACIDAD.values())


class Incapacidad(db.Model):
    __tablename__ = 'incapacidades'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Valores: TIPOS_VALIDOS
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
