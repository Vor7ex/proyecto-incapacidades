"""Migración inicial para los modelos de UC6 (solicitudes y trazabilidad)."""
import os
import sys

from sqlalchemy import inspect, text

# Añadir el directorio raíz al path para resolver imports de la app
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app, db  # noqa: E402
from app.models.solicitud_documento import SolicitudDocumento  # noqa: E402
from app.models.historial_estado import HistorialEstado  # noqa: E402
from app.models.notificacion import Notificacion  # noqa: E402


TABLAS_NUEVAS = {
    SolicitudDocumento.__tablename__: SolicitudDocumento.__table__,
    HistorialEstado.__tablename__: HistorialEstado.__table__,
    Notificacion.__tablename__: Notificacion.__table__,
}


def crear_tablas(inspector):
    creadas = []
    for nombre_tabla, tabla in TABLAS_NUEVAS.items():
        if inspector.has_table(nombre_tabla):
            print(f"✅ La tabla '{nombre_tabla}' ya existe")
            continue

        print(f"➕ Creando tabla '{nombre_tabla}'...")
        tabla.create(bind=db.engine)
        creadas.append(nombre_tabla)

    if creadas:
        print(f"\n🎉 Tablas creadas: {', '.join(creadas)}\n")
    else:
        print("\nℹ️  No se crearon tablas nuevas en esta ejecución\n")


def asegurar_columnas_notificaciones(inspector):
    if not inspector.has_table(Notificacion.__tablename__):
        return

    columnas = {col['name'] for col in inspector.get_columns(Notificacion.__tablename__)}
    alteraciones = []

    if 'solicitud_documento_id' not in columnas:
        alteraciones.append("ADD COLUMN solicitud_documento_id VARCHAR(36)")

    if 'numero_reintento' not in columnas:
        alteraciones.append("ADD COLUMN numero_reintento INTEGER DEFAULT 1")

    if not alteraciones:
        print("✅ La tabla 'notificaciones' ya tiene todas las columnas nuevas")
        return

    print("➕ Actualizando columnas de 'notificaciones'...")
    with db.engine.begin() as conn:
        for alter in alteraciones:
            conn.execute(text(f"ALTER TABLE {Notificacion.__tablename__} {alter}"))

    print("🎉 Columnas agregadas en 'notificaciones': " + ", ".join(alteraciones))


def run_migration():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)

        print("\n================ UC6 - Migración de Modelos ================")
        crear_tablas(inspector)
        asegurar_columnas_notificaciones(inspector)
        print("==========================================================\n")


if __name__ == "__main__":
    run_migration()
