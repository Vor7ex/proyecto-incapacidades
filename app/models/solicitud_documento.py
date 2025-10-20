import uuid
from datetime import datetime
from typing import Optional

from app.models import db
from app.models.enums import EstadoSolicitudDocumentoEnum, TipoDocumentoEnum

try:  # La utilidad de calendario se agregará en la tarea 2
    from app.utils.calendario import dias_habiles_restantes  # type: ignore
except Exception:  # pragma: no cover - fallback para evitar import circular
    dias_habiles_restantes = None


class SolicitudDocumento(db.Model):
    __tablename__ = "solicitudes_documento"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incapacidad_id = db.Column(
        db.Integer,
        db.ForeignKey("incapacidades.id"),
        nullable=False,
        index=True,
    )
    tipo_documento = db.Column(db.String(50), nullable=False)
    estado = db.Column(
        db.String(30),
        nullable=False,
        default=EstadoSolicitudDocumentoEnum.PENDIENTE.value,
        index=True,
    )
    fecha_solicitud = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True, index=True)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    observaciones_auxiliar = db.Column(db.Text, nullable=True)
    intentos_notificacion = db.Column(db.Integer, nullable=False, default=0)
    ultima_notificacion = db.Column(db.DateTime, nullable=True)
    extension_solicitada = db.Column(db.Boolean, nullable=False, default=False)
    motivo_extension = db.Column(db.Text, nullable=True)
    numero_reintentos = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return (
            f"<SolicitudDocumento incapacidad={self.incapacidad_id} "
            f"tipo={self.tipo_documento} estado={self.estado}>"
        )

    def dias_restantes(self, referencia: Optional[datetime] = None) -> int:
        """Retorna los días hábiles restantes hasta el vencimiento."""
        if not self.fecha_vencimiento:
            return 0

        referencia = referencia or datetime.utcnow()
        if dias_habiles_restantes:
            return dias_habiles_restantes(
                referencia.date(),
                self.fecha_vencimiento.date(),
            )

        delta = self.fecha_vencimiento.date() - referencia.date()
        return delta.days

    def esta_vencida(self, referencia: Optional[datetime] = None) -> bool:
        """True si la solicitud está vencida."""
        if not self.fecha_vencimiento:
            return False
        if self.estado == EstadoSolicitudDocumentoEnum.ENTREGADO.value:
            return False

        referencia = referencia or datetime.utcnow()
        return referencia.date() > self.fecha_vencimiento.date()

    def requiere_recordatorio_dia2(self, referencia: Optional[datetime] = None) -> bool:
        """Determina si debe enviarse el recordatorio del día 2."""
        if self.estado != EstadoSolicitudDocumentoEnum.PENDIENTE.value:
            return False
        if self.intentos_notificacion >= 1:
            return False

        return self.dias_restantes(referencia) <= 1

    def requiere_segunda_notificacion(self, referencia: Optional[datetime] = None) -> bool:
        """True si corresponde enviar la segunda notificación."""
        if self.estado != EstadoSolicitudDocumentoEnum.PENDIENTE.value:
            return False
        if self.intentos_notificacion < 1:
            return False
        if self.numero_reintentos >= 2:
            return False

        return self.dias_restantes(referencia) < 0

    def asignar_tipo_documento(self, tipo: TipoDocumentoEnum) -> None:
        """Conveniencia para guardar el tipo como cadena del enum."""
        self.tipo_documento = tipo.value
