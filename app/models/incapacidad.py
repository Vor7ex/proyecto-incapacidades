from datetime import datetime
import uuid
from typing import List, TYPE_CHECKING

from app.models import db
from app.models.enums import (
    EstadoIncapacidadEnum,
    EstadoSolicitudDocumentoEnum,
)

if TYPE_CHECKING:  # Import solo para tipos
    from app.models.solicitud_documento import SolicitudDocumento

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
    estado = db.Column(
        db.String(50),
        default=EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
        index=True,
    )
    motivo_rechazo = db.Column(db.Text, nullable=True)
    
    # UC5: Resultado de validación de requisitos (JSON)
    validacion_uc5 = db.Column(db.JSON, nullable=True)
    
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

    solicitudes = db.relationship(
        'SolicitudDocumento',
        backref='incapacidad',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='SolicitudDocumento.fecha_solicitud.desc()'
    )

    historial_estados = db.relationship(
        'HistorialEstado',
        backref='incapacidad',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='HistorialEstado.fecha_cambio.desc()'
    )

    def asignar_codigo_radicacion(self):
        """
        Asignar código de radicación único a la incapacidad.
        
        Debe llamarse antes de commit a la BD.
        """
        if not self.codigo_radicacion:
            self.codigo_radicacion = generar_codigo_radicacion_unico()
    
    def obtener_solicitudes_pendientes(self) -> List['SolicitudDocumento']:
        """Retorna las solicitudes de documentos que siguen pendientes."""
        return [
            solicitud
            for solicitud in self.solicitudes
            if solicitud.estado == EstadoSolicitudDocumentoEnum.PENDIENTE.value
        ]

    def todas_solicitudes_respondidas(self) -> bool:
        """True cuando todas las solicitudes de documentos fueron entregadas."""
        if not self.solicitudes:
            return True
        return all(
            solicitud.estado == EstadoSolicitudDocumentoEnum.ENTREGADO.value
            for solicitud in self.solicitudes
        )

    def cambiar_estado(self, nuevo_estado, usuario, observaciones='', documento=None) -> bool:
        """Actualiza el estado y registra el cambio en HistorialEstado."""
        from app.models.historial_estado import HistorialEstado

        estado_actual = str(self.estado)
        nuevo_estado_valor = str(nuevo_estado)

        if estado_actual == nuevo_estado_valor and not observaciones:
            return False

        registro = HistorialEstado.crear_desde_cambio(
            incapacidad=self,
            estado_nuevo=nuevo_estado_valor,
            usuario=usuario,
            observaciones=observaciones,
            documento=documento,
        )

        self.estado = nuevo_estado_valor
        self.historial_estados.append(registro)
        self.fecha_actualizacion = datetime.utcnow()
        return True

    def __repr__(self):
        if self.codigo_radicacion:
            return f'<Incapacidad {self.codigo_radicacion} - {self.tipo}>'
        return f'<Incapacidad {self.id} - {self.tipo}>'
