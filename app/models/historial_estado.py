import uuid
from datetime import datetime
from typing import Optional

from app.models import db


class HistorialEstado(db.Model):
    __tablename__ = "historial_estados"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incapacidad_id = db.Column(
        db.Integer,
        db.ForeignKey("incapacidades.id"),
        nullable=False,
        index=True,
    )
    estado_anterior = db.Column(db.String(50), nullable=True)  # Puede ser NULL en el primer registro
    estado_nuevo = db.Column(db.String(50), nullable=False)
    fecha_cambio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    documento_soporte_id = db.Column(
        db.Integer,
        db.ForeignKey("documentos.id"),
        nullable=True,
    )

    usuario = db.relationship("Usuario", lazy="joined")
    documento_soporte = db.relationship("Documento", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<HistorialEstado incapacidad={self.incapacidad_id} "
            f"{self.estado_anterior}->{self.estado_nuevo}>"
        )

    @classmethod
    def crear_desde_cambio(
        cls,
        incapacidad,
        estado_nuevo: str,
        usuario,
        observaciones: str = "",
        documento=None,
    ) -> "HistorialEstado":
        """Fábrica para registrar cambios de estado en la incapacidad."""
        if usuario is None:
            raise ValueError("Se requiere un usuario para registrar el cambio de estado")

        return cls(
            incapacidad_id=incapacidad.id,
            estado_anterior=str(incapacidad.estado),
            estado_nuevo=str(estado_nuevo),
            usuario_id=usuario.id,
            observaciones=observaciones or None,
            documento_soporte_id=getattr(documento, "id", None),
        )
