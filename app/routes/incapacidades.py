from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app.models import db
from app.models.incapacidad import Incapacidad
from app.models.documento import Documento
from config import Config

incapacidades_bp = Blueprint('incapacidades', __name__, url_prefix='/incapacidades')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def calcular_dias(fecha_inicio, fecha_fin):
    return (fecha_fin - fecha_inicio).days + 1

@incapacidades_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():
    if current_user.rol != 'colaborador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        fecha_inicio_str = request.form.get('fecha_inicio')
        fecha_fin_str = request.form.get('fecha_fin')

        # Validar datos
        if not all([tipo, fecha_inicio_str, fecha_fin_str]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('incapacidades.registrar'))

        # Convertir fechas
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha inválido', 'danger')
            return redirect(url_for('incapacidades.registrar'))

        # Validar rango de fechas
        if fecha_fin < fecha_inicio:
            flash('La fecha de fin debe ser posterior a la fecha de inicio', 'danger')
            return redirect(url_for('incapacidades.registrar'))

        dias = calcular_dias(fecha_inicio, fecha_fin)

        # Crear incapacidad
        incapacidad = Incapacidad(
            usuario_id=current_user.id,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            dias=dias,
            estado='Pendiente'
        )

        db.session.add(incapacidad)
        db.session.commit()

        # Procesar archivos (UC2)
        archivos_guardados = procesar_archivos(request.files, incapacidad.id)

        if archivos_guardados == 0:
            flash('Incapacidad registrada, pero no se cargaron documentos', 'warning')
        else:
            flash(f'Incapacidad registrada exitosamente. {archivos_guardados} documento(s) cargado(s)', 'success')

        return redirect(url_for('incapacidades.mis_incapacidades'))

    return render_template('registro_incapacidad.html')

def procesar_archivos(files, incapacidad_id):
    """UC2: Cargar documentos"""
    archivos_guardados = 0

    # Procesar certificado
    if 'certificado' in files:
        file = files['certificado']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            nuevo_nombre = f"{incapacidad_id}_certificado_{timestamp}_{filename}"
            ruta = os.path.join(Config.UPLOAD_FOLDER, nuevo_nombre)
            file.save(ruta)

            documento = Documento(
                incapacidad_id=incapacidad_id,
                nombre_archivo=filename,
                ruta=ruta,
                tipo_documento='certificado'
            )
            db.session.add(documento)
            archivos_guardados += 1

    # Procesar epicrisis
    if 'epicrisis' in files:
        file = files['epicrisis']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            nuevo_nombre = f"{incapacidad_id}_epicrisis_{timestamp}_{filename}"
            ruta = os.path.join(Config.UPLOAD_FOLDER, nuevo_nombre)
            file.save(ruta)

            documento = Documento(
                incapacidad_id=incapacidad_id,
                nombre_archivo=filename,
                ruta=ruta,
                tipo_documento='epicrisis'
            )
            db.session.add(documento)
            archivos_guardados += 1

    db.session.commit()
    return archivos_guardados

@incapacidades_bp.route('/mis-incapacidades')
@login_required
def mis_incapacidades():
    """UC3: Consultar mis incapacidades"""
    if current_user.rol != 'colaborador':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.index'))

    incapacidades = Incapacidad.query.filter_by(
        usuario_id=current_user.id
    ).order_by(Incapacidad.fecha_registro.desc()).all()

    return render_template('mis_incapacidades.html', incapacidades=incapacidades)

@incapacidades_bp.route('/dashboard-auxiliar')
@login_required
def dashboard_auxiliar():
    """UC5: Ver incapacidades pendientes"""
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.index'))

    pendientes = Incapacidad.query.filter_by(estado='Pendiente').all()
    en_revision = Incapacidad.query.filter_by(estado='En revision').all()

    return render_template('dashboard_auxiliar.html', pendientes=pendientes, en_revision=en_revision)

@incapacidades_bp.route('/detalle/<int:id>')
@login_required
def detalle(id):
    """UC4: Ver detalle de incapacidad"""
    incapacidad = Incapacidad.query.get_or_404(id)

    # Verificar permisos
    if current_user.rol == 'colaborador' and incapacidad.usuario_id != current_user.id:
        flash('No tiene permisos para ver esta incapacidad', 'danger')
        return redirect(url_for('incapacidades.mis_incapacidades'))

    return render_template('detalle_incapacidad.html', incapacidad=incapacidad)