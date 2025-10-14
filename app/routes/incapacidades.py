from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app.models import db
from app.models.incapacidad import Incapacidad
from app.models.documento import Documento
from config import Config
from app.utils.validaciones import (
    validar_tipo_incapacidad, 
    validar_rango_fechas, 
    validar_archivo,
    validar_documentos_incapacidad,
    obtener_documentos_requeridos
)
from app.utils.email_service import (
    notificar_nueva_incapacidad,
    notificar_validacion_completada,
    notificar_documentos_faltantes,
    notificar_aprobacion,
    notificar_rechazo
)

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

        # Validar datos básicos
        if not all([tipo, fecha_inicio_str, fecha_fin_str]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('incapacidades.registrar'))

        # UC1: Validar tipo de incapacidad
        tipo_valido, error_tipo = validar_tipo_incapacidad(tipo)
        if not tipo_valido:
            flash(error_tipo, 'danger')
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

        # UC1: Validar documentos obligatorios según tipo de incapacidad
        documentos_validos, docs_faltantes, error_docs = validar_documentos_incapacidad(
            tipo, 
            request.files,
            dias
        )
        
        if not documentos_validos:
            flash(error_docs, 'danger')
            return redirect(url_for('incapacidades.registrar'))

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

        # UC2: Enviar notificaciones por email
        try:
            notificar_nueva_incapacidad(incapacidad)
        except Exception as e:
            print(f"❌ Error al enviar notificacion: {e}")
            import traceback
            traceback.print_exc()
            # No interrumpir el flujo si falla el email

        if archivos_guardados == 0:
            flash('Incapacidad registrada, pero no se cargaron documentos', 'warning')
        else:
            flash(f'Incapacidad registrada exitosamente. {archivos_guardados} documento(s) cargado(s)', 'success')

        return redirect(url_for('incapacidades.mis_incapacidades'))

    return render_template('registro_incapacidad.html')

def procesar_archivos(files, incapacidad_id):
    """UC2: Cargar documentos - Versión mejorada con todos los tipos"""
    archivos_guardados = 0
    
    # Lista de todos los tipos de documentos posibles
    tipos_documentos = [
        'certificado',
        'epicrisis',
        'furips',
        'certificado_nacido_vivo',
        'registro_civil',
        'documento_identidad_madre'
    ]

    for tipo_doc in tipos_documentos:
        if tipo_doc in files:
            file = files[tipo_doc]
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                nuevo_nombre = f"{incapacidad_id}_{tipo_doc}_{timestamp}_{filename}"
                ruta = os.path.join(Config.UPLOAD_FOLDER, nuevo_nombre)
                file.save(ruta)

                documento = Documento(
                    incapacidad_id=incapacidad_id,
                    nombre_archivo=filename,
                    ruta=ruta,
                    tipo_documento=tipo_doc
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
    """Dashboard de Auxiliar RRHH (CU-006 y CU-007)"""
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado. Solo Auxiliar RRHH puede acceder.', 'danger')
        return redirect(url_for('auth.index'))

    pendientes = Incapacidad.query.filter_by(estado='Pendiente').all()
    en_revision = Incapacidad.query.filter_by(estado='En revision').all()
    aprobadas = Incapacidad.query.filter_by(estado='Aprobada').all()
    rechazadas = Incapacidad.query.filter_by(estado='Rechazada').all()

    return render_template('dashboard_auxiliar.html', 
                         pendientes=pendientes, 
                         en_revision=en_revision,
                         aprobadas=aprobadas,
                         rechazadas=rechazadas)

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

@incapacidades_bp.route('/validar/<int:id>', methods=['GET', 'POST'])
@login_required
def validar(id):
    """CU-006: Validar documentación (Auxiliar RRHH)"""
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado. Solo Auxiliar RRHH puede validar documentación.', 'danger')
        return redirect(url_for('auth.index'))
    
    incapacidad = Incapacidad.query.get_or_404(id)
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        if accion == 'completar_revision':
            # Marcar como en revision (documentacion completa)
            incapacidad.estado = 'En revision'
            db.session.commit()
            
            # UC2: Notificar validacion completada
            try:
                notificar_validacion_completada(incapacidad)
            except Exception as e:
                print(f"❌ Error al enviar notificacion: {e}")
                import traceback
                traceback.print_exc()
            
            flash('Documentacion marcada como completa. Ahora puede aprobar o rechazar.', 'success')
            return redirect(url_for('incapacidades.aprobar_rechazar', id=id))
        
        elif accion == 'solicitar_documentos':
            # Mantener en pendiente (documentacion incompleta)
            observaciones = request.form.get('observaciones', '')
            
            # UC2: Notificar documentos faltantes
            try:
                notificar_documentos_faltantes(incapacidad, observaciones)
            except Exception as e:
                print(f"❌ Error al enviar notificacion: {e}")
                import traceback
                traceback.print_exc()
            
            flash(f'Solicitud registrada: {observaciones}. Notificacion enviada al colaborador.', 'warning')
            return redirect(url_for('incapacidades.dashboard_auxiliar'))
    
    # UC10: Validacion automatica de requisitos
    validacion = validar_requisitos_automatico(incapacidad)
    
    return render_template('validar_incapacidades.html', 
                         incapacidad=incapacidad,
                         validacion=validacion)

def validar_requisitos_automatico(incapacidad):
    """UC10: Validacion automatica basica"""
    resultado = {
        'certificado_presente': False,
        'epicrisis_presente': False,
        'epicrisis_requerida': False,
        'todos_documentos': False,
        'advertencias': [],
        'recomendaciones': []
    }
    
    # Verificar certificado
    certificado = Documento.query.filter_by(
        incapacidad_id=incapacidad.id,
        tipo_documento='certificado'
    ).first()
    resultado['certificado_presente'] = certificado is not None
    
    # Verificar epicrisis
    epicrisis = Documento.query.filter_by(
        incapacidad_id=incapacidad.id,
        tipo_documento='epicrisis'
    ).first()
    resultado['epicrisis_presente'] = epicrisis is not None
    
    # Determinar si epicrisis es requerida
    if incapacidad.dias > 2 or incapacidad.tipo == 'Accidente Laboral':
        resultado['epicrisis_requerida'] = True
        if not epicrisis:
            resultado['advertencias'].append('Falta Epicrisis (requerida para este tipo)')
    
    # Verificar si falta certificado
    if not certificado:
        resultado['advertencias'].append('Falta Certificado de Incapacidad (obligatorio)')
    else:
        resultado['recomendaciones'].append('Certificado presente')
    
    # Verificar epicrisis si esta presente
    if epicrisis:
        resultado['recomendaciones'].append('Epicrisis presente')
    
    # Todos los documentos OK
    if resultado['certificado_presente']:
        if resultado['epicrisis_requerida']:
            resultado['todos_documentos'] = resultado['epicrisis_presente']
        else:
            resultado['todos_documentos'] = True
    
    return resultado

@incapacidades_bp.route('/aprobar-rechazar/<int:id>', methods=['GET', 'POST'])
@login_required
def aprobar_rechazar(id):
    """CU-007: Aprobar o rechazar incapacidad (Auxiliar RRHH)"""
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado. Solo Auxiliar RRHH puede aprobar/rechazar incapacidades.', 'danger')
        return redirect(url_for('auth.index'))
    
    incapacidad = Incapacidad.query.get_or_404(id)
    
    # Solo se puede aprobar/rechazar si esta en revision
    if incapacidad.estado not in ['En revision', 'Pendiente']:
        flash('Esta incapacidad ya fue procesada', 'warning')
        return redirect(url_for('incapacidades.dashboard_auxiliar'))
    
    if request.method == 'POST':
        decision = request.form.get('decision')
        
        if decision == 'aprobar':
            incapacidad.estado = 'Aprobada'
            incapacidad.motivo_rechazo = None
            db.session.commit()
            
            # UC2: Notificar aprobacion
            try:
                notificar_aprobacion(incapacidad)
            except Exception as e:
                print(f"❌ Error al enviar notificacion: {e}")
                import traceback
                traceback.print_exc()
            
            flash(f'Incapacidad #{id} aprobada exitosamente', 'success')
            return redirect(url_for('incapacidades.dashboard_auxiliar'))
        
        elif decision == 'rechazar':
            motivo = request.form.get('motivo_rechazo')
            if not motivo or len(motivo.strip()) < 10:
                flash('Debe especificar un motivo de rechazo (minimo 10 caracteres)', 'danger')
                return render_template('aprobar_rechazar.html', incapacidad=incapacidad)
            
            incapacidad.estado = 'Rechazada'
            incapacidad.motivo_rechazo = motivo
            db.session.commit()
            
            # UC2: Notificar rechazo
            try:
                notificar_rechazo(incapacidad)
            except Exception as e:
                print(f"❌ Error al enviar notificacion: {e}")
                import traceback
                traceback.print_exc()
            
            flash(f'Incapacidad #{id} rechazada', 'info')
            return redirect(url_for('incapacidades.dashboard_auxiliar'))
    
    return render_template('aprobar_rechazar.html', incapacidad=incapacidad)

@incapacidades_bp.route('/estadisticas')
@login_required
def estadisticas():
    """Vista de estadísticas básicas (Auxiliar RRHH)"""
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.index'))
    
    total = Incapacidad.query.count()
    pendientes = Incapacidad.query.filter_by(estado='Pendiente').count()
    en_revision = Incapacidad.query.filter_by(estado='En revision').count()
    aprobadas = Incapacidad.query.filter_by(estado='Aprobada').count()
    rechazadas = Incapacidad.query.filter_by(estado='Rechazada').count()
    
    total_documentos = Documento.query.count()
    
    stats = {
        'total': total,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'aprobadas': aprobadas,
        'rechazadas': rechazadas,
        'total_documentos': total_documentos
    }
    
    return render_template('estadisticas.html', stats=stats)

def validar_requisitos_automatico(incapacidad):
    """UC10: Validacion automatica mejorada"""
    resultado = {
        'certificado_presente': False,
        'epicrisis_presente': False,
        'epicrisis_requerida': False,
        'todos_documentos': False,
        'advertencias': [],
        'recomendaciones': [],
        'nivel_cumplimiento': 0  # 0-100
    }
    
    # Verificar certificado
    certificado = Documento.query.filter_by(
        incapacidad_id=incapacidad.id,
        tipo_documento='certificado'
    ).first()
    resultado['certificado_presente'] = certificado is not None
    
    if not certificado:
        resultado['advertencias'].append('❌ Falta Certificado de Incapacidad (OBLIGATORIO)')
        resultado['nivel_cumplimiento'] = 0
    else:
        resultado['nivel_cumplimiento'] = 50
        resultado['recomendaciones'].append('✅ Certificado presente')
    
    # Verificar epicrisis
    epicrisis = Documento.query.filter_by(
        incapacidad_id=incapacidad.id,
        tipo_documento='epicrisis'
    ).first()
    resultado['epicrisis_presente'] = epicrisis is not None
    
    # Determinar si epicrisis es requerida
    if incapacidad.dias > 2:
        resultado['epicrisis_requerida'] = True
        if not epicrisis:
            resultado['advertencias'].append('❌ Falta Epicrisis (requerida para incapacidades >2 dias)')
        else:
            resultado['nivel_cumplimiento'] = 100
            resultado['recomendaciones'].append('✅ Epicrisis presente (requerida)')
    
    if incapacidad.tipo == 'Accidente Laboral':
        resultado['epicrisis_requerida'] = True
        if not epicrisis:
            resultado['advertencias'].append('❌ Falta Epicrisis (obligatoria para accidentes laborales)')
        else:
            resultado['nivel_cumplimiento'] = 100
            resultado['recomendaciones'].append('✅ Epicrisis presente (obligatoria)')
    
    # Si epicrisis no es requerida pero esta presente
    if not resultado['epicrisis_requerida'] and epicrisis:
        resultado['nivel_cumplimiento'] = 100
        resultado['recomendaciones'].append('✅ Documentacion completa')
    
    # Si no requiere epicrisis y tiene certificado
    if not resultado['epicrisis_requerida'] and certificado:
        resultado['nivel_cumplimiento'] = 100
        resultado['todos_documentos'] = True
    
    # Verificar si todos los documentos OK
    if resultado['certificado_presente']:
        if resultado['epicrisis_requerida']:
            resultado['todos_documentos'] = resultado['epicrisis_presente']
        else:
            resultado['todos_documentos'] = True
    
    # Recomendaciones adicionales
    if resultado['todos_documentos']:
        resultado['recomendaciones'].append('�� Todos los documentos obligatorios estan presentes')
    
    return resultado