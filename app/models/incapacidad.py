from app.models import db
from datetime import datetime
import uuid

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


def generar_codigo_radicacion():
    """
    Generar código único de radicación para incapacidad.
    
    Formato: INC-YYYYMMDD-XXXX
    - INC: Prefijo fijo
    - YYYYMMDD: Fecha actual
    - XXXX: 4 dígitos del UUID (hexadecimal)
    
    Ejemplos:
        INC-20251013-A3F2
        INC-20251014-B7C1
    
    Returns:
        str: Código de radicación único
    """
    # Fecha actual en formato YYYYMMDD
    fecha = datetime.now().strftime('%Y%m%d')
    
    # 4 caracteres únicos del UUID (hexadecimal en mayúsculas)
    codigo_unico = str(uuid.uuid4()).replace('-', '')[:4].upper()
    
    # Formato final: INC-YYYYMMDD-XXXX
    codigo_radicacion = f"INC-{fecha}-{codigo_unico}"
    
    return codigo_radicacion


def verificar_codigo_unico(codigo):
    """
    Verificar que un código de radicación sea único en la BD.
    
    Args:
        codigo (str): Código a verificar
    
    Returns:
        bool: True si es único, False si ya existe
    """
    from app.models.incapacidad import Incapacidad
    existe = Incapacidad.query.filter_by(codigo_radicacion=codigo).first()
    return existe is None


def generar_codigo_radicacion_unico(max_intentos=10):
    """
    Generar código de radicación garantizando unicidad en BD.
    
    Args:
        max_intentos (int): Número máximo de intentos antes de fallar
    
    Returns:
        str: Código único
    
    Raises:
        RuntimeError: Si no se puede generar código único después de max_intentos
    """
    for intento in range(max_intentos):
        codigo = generar_codigo_radicacion()
        if verificar_codigo_unico(codigo):
            return codigo
    
    # Si llegamos aquí, hubo colisión en todos los intentos (muy improbable)
    raise RuntimeError(f"No se pudo generar código único después de {max_intentos} intentos")


class Incapacidad(db.Model):
    __tablename__ = 'incapacidades'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    codigo_radicacion = db.Column(db.String(50), unique=True, nullable=True, index=True)  # INC-YYYYMMDD-XXXX
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

    def asignar_codigo_radicacion(self):
        """
        Asignar código de radicación único a la incapacidad.
        
        Debe llamarse antes de commit a la BD.
        """
        if not self.codigo_radicacion:
            self.codigo_radicacion = generar_codigo_radicacion_unico()
    
    def __repr__(self):
        if self.codigo_radicacion:
            return f'<Incapacidad {self.codigo_radicacion} - {self.tipo}>'
        return f'<Incapacidad {self.id} - {self.tipo}>'
