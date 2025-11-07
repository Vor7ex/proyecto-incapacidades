"""
Rutas para gestión de notificaciones internas del sistema.
"""

from datetime import datetime
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import desc

from app.models import db
from app.models.notificacion import Notificacion
from app.models.enums import EstadoNotificacionEnum

notificaciones_bp = Blueprint("notificaciones", __name__, url_prefix="/notificaciones")


@notificaciones_bp.route("/")
@login_required
def listar():
    """Vista principal de notificaciones del usuario."""
    return render_template("notificaciones.html")


@notificaciones_bp.route("/api/mis-notificaciones")
@login_required
def obtener_mis_notificaciones():
    """
    API para obtener las notificaciones del usuario actual.
    
    Query params:
    - limite: Número máximo de notificaciones a retornar (default: 10)
    - solo_no_leidas: Si es 'true', solo retorna las no leídas (default: false)
    - pagina: Número de página para paginación (default: 1)
    
    Returns:
        JSON con lista de notificaciones y metadata de paginación
    """
    # Parsear parámetros
    limite = request.args.get("limite", 10, type=int)
    solo_no_leidas = request.args.get("solo_no_leidas", "false").lower() == "true"
    pagina = request.args.get("pagina", 1, type=int)
    
    # Query base
    query = Notificacion.query.filter_by(destinatario_id=current_user.id)
    
    # Filtro de no leídas
    if solo_no_leidas:
        query = query.filter(
            Notificacion.estado != EstadoNotificacionEnum.LEIDA.value
        )
    
    # Ordenar por fecha de envío descendente
    query = query.order_by(desc(Notificacion.fecha_envio))
    
    # Contar total
    total = query.count()
    
    # Paginación
    offset = (pagina - 1) * limite
    notificaciones = query.offset(offset).limit(limite).all()
    
    # Serializar
    resultado = []
    for notif in notificaciones:
        resultado.append({
            "id": notif.id,
            "tipo": notif.tipo,
            "asunto": notif.asunto,
            "contenido": notif.contenido,
            "fecha_envio": notif.fecha_envio.isoformat(),
            "fecha_lectura": notif.fecha_lectura.isoformat() if notif.fecha_lectura else None,
            "estado": notif.estado,
            "es_leida": notif.estado == EstadoNotificacionEnum.LEIDA.value,
            "tiempo_relativo": _formatear_tiempo_relativo(notif.fecha_envio),
        })
    
    return jsonify({
        "notificaciones": resultado,
        "total": total,
        "pagina": pagina,
        "total_paginas": (total + limite - 1) // limite,
        "no_leidas": Notificacion.query.filter_by(
            destinatario_id=current_user.id
        ).filter(
            Notificacion.estado != EstadoNotificacionEnum.LEIDA.value
        ).count()
    })


@notificaciones_bp.route("/api/contador-no-leidas")
@login_required
def contador_no_leidas():
    """
    API rápida para obtener solo el contador de notificaciones no leídas.
    Usado por el badge en el navbar.
    """
    count = Notificacion.query.filter_by(
        destinatario_id=current_user.id
    ).filter(
        Notificacion.estado != EstadoNotificacionEnum.LEIDA.value
    ).count()
    
    return jsonify({"no_leidas": count})


@notificaciones_bp.route("/api/marcar-leida/<string:notificacion_id>", methods=["POST"])
@login_required
def marcar_leida(notificacion_id):
    """
    Marca una notificación como leída.
    
    Args:
        notificacion_id: UUID de la notificación
        
    Returns:
        JSON con resultado de la operación
    """
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    
    # Verificar que la notificación pertenece al usuario actual
    if notificacion.destinatario_id != current_user.id:
        return jsonify({"error": "No autorizado"}), 403
    
    # Marcar como leída si no lo está
    if notificacion.estado != EstadoNotificacionEnum.LEIDA.value:
        notificacion.marcar_leida()
        db.session.commit()
    
    return jsonify({
        "success": True,
        "notificacion_id": notificacion_id,
        "fecha_lectura": notificacion.fecha_lectura.isoformat()
    })


@notificaciones_bp.route("/api/marcar-no-leida/<string:notificacion_id>", methods=["POST"])
@login_required
def marcar_no_leida(notificacion_id):
    """
    Marca una notificación como NO leída (revertir lectura).
    
    Args:
        notificacion_id: UUID de la notificación
        
    Returns:
        JSON con resultado de la operación
    """
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    
    # Verificar que la notificación pertenece al usuario actual
    if notificacion.destinatario_id != current_user.id:
        return jsonify({"error": "No autorizado"}), 403
    
    # Marcar como no leída (volver a ENTREGADA)
    if notificacion.estado == EstadoNotificacionEnum.LEIDA.value:
        notificacion.estado = EstadoNotificacionEnum.ENTREGADA.value
        notificacion.fecha_lectura = None
        db.session.commit()
    
    return jsonify({
        "success": True,
        "notificacion_id": notificacion_id
    })


@notificaciones_bp.route("/api/marcar-todas-leidas", methods=["POST"])
@login_required
def marcar_todas_leidas():
    """
    Marca todas las notificaciones del usuario como leídas.
    
    Returns:
        JSON con número de notificaciones actualizadas
    """
    notificaciones = Notificacion.query.filter_by(
        destinatario_id=current_user.id
    ).filter(
        Notificacion.estado != EstadoNotificacionEnum.LEIDA.value
    ).all()
    
    count = 0
    for notif in notificaciones:
        notif.marcar_leida()
        count += 1
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "marcadas": count
    })


def _formatear_tiempo_relativo(fecha):
    """
    Formatea una fecha como tiempo relativo (ej: 'hace 5 minutos').
    
    Args:
        fecha: datetime a formatear
        
    Returns:
        str: Texto descriptivo del tiempo transcurrido
    """
    ahora = datetime.utcnow()
    diferencia = ahora - fecha
    
    segundos = diferencia.total_seconds()
    
    if segundos < 60:
        return "Hace un momento"
    elif segundos < 3600:
        minutos = int(segundos / 60)
        return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
    elif segundos < 86400:
        horas = int(segundos / 3600)
        return f"Hace {horas} hora{'s' if horas > 1 else ''}"
    elif segundos < 604800:
        dias = int(segundos / 86400)
        return f"Hace {dias} día{'s' if dias > 1 else ''}"
    else:
        return fecha.strftime("%d/%m/%Y %H:%M")
