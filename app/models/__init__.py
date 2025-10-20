from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importaciones de modelos para que SQLAlchemy los registre
from app.models.usuario import Usuario  # noqa: E402,F401
from app.models.incapacidad import Incapacidad  # noqa: E402,F401
from app.models.documento import Documento  # noqa: E402,F401
from app.models.solicitud_documento import SolicitudDocumento  # noqa: E402,F401
from app.models.historial_estado import HistorialEstado  # noqa: E402,F401
from app.models.notificacion import Notificacion  # noqa: E402,F401