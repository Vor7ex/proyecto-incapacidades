from flask import Blueprint, send_file, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from app.models.documento import Documento
from app.models.incapacidad import Incapacidad
import os

documentos_bp = Blueprint('documentos', __name__, url_prefix='/documentos')

@documentos_bp.route('/descargar/<int:documento_id>')
@login_required
def descargar(documento_id):
    """UC8: Descargar documento individual"""
    documento = Documento.query.get_or_404(documento_id)
    incapacidad = Incapacidad.query.get(documento.incapacidad_id)
    
    # Verificar permisos
    if current_user.rol == 'colaborador' and incapacidad.usuario_id != current_user.id:
        flash('No tiene permisos para descargar este documento', 'danger')
        return redirect(url_for('incapacidades.mis_incapacidades'))
    
    # Verificar que el archivo existe
    if not os.path.exists(documento.ruta):
        flash('Archivo no encontrado en el servidor', 'danger')
        return redirect(url_for('incapacidades.detalle', id=incapacidad.id))
    
    try:
        return send_file(
            documento.ruta,
            as_attachment=True,
            download_name=documento.nombre_archivo
        )
    except Exception as e:
        flash(f'Error al descargar el archivo: {str(e)}', 'danger')
        return redirect(url_for('incapacidades.detalle', id=incapacidad.id))

@documentos_bp.route('/ver/<int:documento_id>')
@login_required
def ver(documento_id):
    """Ver documento en el navegador (para PDFs)"""
    documento = Documento.query.get_or_404(documento_id)
    incapacidad = Incapacidad.query.get(documento.incapacidad_id)
    
    # Verificar permisos
    if current_user.rol == 'colaborador' and incapacidad.usuario_id != current_user.id:
        flash('No tiene permisos para ver este documento', 'danger')
        return redirect(url_for('incapacidades.mis_incapacidades'))
    
    if not os.path.exists(documento.ruta):
        flash('Archivo no encontrado', 'danger')
        return redirect(url_for('incapacidades.detalle', id=incapacidad.id))
    
    try:
        return send_file(documento.ruta, mimetype='application/pdf')
    except:
        return send_file(documento.ruta, as_attachment=False)