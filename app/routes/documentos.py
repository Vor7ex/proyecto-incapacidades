from flask import Blueprint, send_file, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models.documento import Documento
from app.models.incapacidad import Incapacidad
import os

# Definir el blueprint para la gestión de documentos
documentos_bp = Blueprint('documentos', __name__, url_prefix='/documentos')

@documentos_bp.route('/descargar/<int:documento_id>')
@login_required
def descargar(documento_id):
    """UC8: Descargar documentos"""
    documento = Documento.query.get_or_404(documento_id)
    incapacidad = Incapacidad.query.get(documento.incapacidad_id)

    # Verificar permisos
    if current_user.rol == 'colaborador' and incapacidad.usuario_id != current_user.id:
        flash('No tiene permisos para descargar este documento', 'danger')
        return redirect(url_for('auth.index'))

    # Verificar que el archivo exista
    if not os.path.exists(documento.ruta):
        flash('Archivo no encontrado', 'danger')
        return redirect(request.referrer or url_for('auth.index'))

    # Enviar archivo para descarga
    return send_file(documento.ruta, as_attachment=True, download_name=documento.nombre_archivo)