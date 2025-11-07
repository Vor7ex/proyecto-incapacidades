import uuid
from datetime import datetime
from typing import Optional

from app.models import db
from app.models.enums import EstadoNotificacionEnum, TipoNotificacionEnum


class Notificacion(db.Model):
    __tablename__ = "notificaciones"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tipo = db.Column(db.String(50), nullable=False)
    destinatario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )
    asunto = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_lectura = db.Column(db.DateTime, nullable=True)
    estado = db.Column(
        db.String(20),
        nullable=False,
        default=EstadoNotificacionEnum.PENDIENTE.value,
        index=True,
    )
    solicitud_documento_id = db.Column(
        db.String(36),
        db.ForeignKey("solicitudes_documento.id"),
        nullable=True,
        index=True,
    )
    numero_reintento = db.Column(db.Integer, nullable=False, default=1)

    destinatario = db.relationship("Usuario", backref="notificaciones", lazy="joined")
    solicitud_documento = db.relationship("SolicitudDocumento", lazy="joined")

    def __repr__(self) -> str:
        return f"<Notificacion tipo={self.tipo} destinatario={self.destinatario_id}>"

    def marcar_enviada(self) -> None:
        self.estado = EstadoNotificacionEnum.ENVIADA.value
        self.fecha_envio = datetime.utcnow()

    def marcar_entregada(self) -> None:
        self.estado = EstadoNotificacionEnum.ENTREGADA.value

    def marcar_leida(self) -> None:
        """Marca la notificación como leída y registra la fecha de lectura."""
        self.estado = EstadoNotificacionEnum.LEIDA.value
        self.fecha_lectura = datetime.utcnow()

    def registrar_error(self, descripcion: Optional[str] = None) -> None:
        self.estado = EstadoNotificacionEnum.ERROR.value
        if descripcion:
            self.contenido = f"{self.contenido}\n\nError: {descripcion}"

    def set_tipo(self, tipo: TipoNotificacionEnum) -> None:
        self.tipo = tipo.value
