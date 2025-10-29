from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import logging
from app.models import db
from app.models.incapacidad import Incapacidad
from app.models.documento import Documento
from config import Config
from app.utils.validaciones import (
    validar_tipo_incapacidad, 
    validar_rango_fechas, 
    validar_archivo,
    validar_documentos_incapacidad,
    obtener_documentos_requeridos,
    procesar_archivo_completo
)
from app.utils.email_service import (
    notificar_nueva_incapacidad,
    notificar_validacion_completada,
    notificar_documentos_faltantes,
    notificar_aprobacion,
    notificar_rechazo,
    confirmar_almacenamiento_definitivo
)

incapacidades_bp = Blueprint('incapacidades', __name__, url_prefix='/incapacidades')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def limpiar_archivos_huerfanos(incapacidad_id):
    """
    Elimina archivos físicos de una incapacidad cuando falla la transacción.
    Se usa en rollback para evitar archivos huérfanos en el sistema.
    """
    try:
        documentos = Documento.query.filter_by(incapacidad_id=incapacidad_id).all()
        for doc in documentos:
            ruta_completa = os.path.join(Config.UPLOAD_FOLDER, doc.ruta_archivo)
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)
                print(f"🗑️ Archivo huérfano eliminado: {ruta_completa}")
    except Exception as e:
        print(f"⚠️ Error al limpiar archivos huérfanos: {e}")

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
        
        # Detectar si es petición AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                  request.accept_mimetypes.accept_json

        # Validar datos básicos
        if not all([tipo, fecha_inicio_str, fecha_fin_str]):
            error_msg = 'Todos los campos son obligatorios'
            if is_ajax:
                return jsonify({'success': False, 'errors': [error_msg]}), 400
            flash(error_msg, 'danger')
            return redirect(url_for('incapacidades.registrar'))

        # UC1: Validar tipo de incapacidad
        tipo_valido, error_tipo = validar_tipo_incapacidad(tipo)
        if not tipo_valido:
            if is_ajax:
                return jsonify({'success': False, 'errors': [error_tipo]}), 400
            flash(error_tipo, 'danger')
            return redirect(url_for('incapacidades.registrar'))

        # Convertir fechas
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            error_msg = 'Formato de fecha inválido'
            if is_ajax:
                return jsonify({'success': False, 'errors': [error_msg]}), 400
            flash(error_msg, 'danger')
            return redirect(url_for('incapacidades.registrar'))

        # Validar rango de fechas
        if fecha_fin < fecha_inicio:
            error_msg = 'La fecha de fin debe ser posterior a la fecha de inicio'
            if is_ajax:
                return jsonify({'success': False, 'errors': [error_msg]}), 400
            flash(error_msg, 'danger')
            return redirect(url_for('incapacidades.registrar'))

        dias = calcular_dias(fecha_inicio, fecha_fin)

        # ========================================
        # CAMBIO UC6: Documentos son OPCIONALES en registro inicial
        # El auxiliar los solicitará después mediante UC6 si faltan
        # ========================================
        # Ya no validamos documentos obligatorios aquí
        # El colaborador puede registrar sin documentos o con documentos parciales

        # ========================================
        # TRANSACCIÓN ATÓMICA: Incapacidad + Documentos
        # Si falla cualquier paso, se revierte todo
        # ========================================
        try:
            from app.models.enums import EstadoIncapacidadEnum
            
            # Crear incapacidad (sin commit aún)
            incapacidad = Incapacidad(
                usuario_id=current_user.id,
                tipo=tipo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                dias=dias,
                estado=EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value
            )
            
            # Asignar código de radicación único
            incapacidad.asignar_codigo_radicacion()
            
            # Agregar a sesión (sin commit)
            db.session.add(incapacidad)
            db.session.flush()  # Obtener ID sin hacer commit
            
            # ========================================
            # UC5: VALIDACIÓN DE REQUISITOS POR TIPO
            # Integración 2.1 - Validar antes de guardar
            # ========================================
            from app.services.validacion_requisitos_service import ValidadorRequisitos
            import logging
            
            logger = logging.getLogger(__name__)
            logger.info(f"✅ UC5: Iniciando validación de requisitos para incapacidad #{incapacidad.id}")
            
            try:
                validador = ValidadorRequisitos()
                resultado_uc5 = validador.validar(incapacidad)
                
                # Guardar resultado en BD para referencia futura
                incapacidad.validacion_uc5 = resultado_uc5
                
                logger.info(f"✅ UC5: Validación ejecutada - Completo: {resultado_uc5['completo']}")
                
                # UC1 + UC5: Si documentación NO está completa, mostrar advertencia pero PERMITIR guardar
                # (El auxiliar podrá usar UC6 para solicitar documentos faltantes)
                if not resultado_uc5['completo']:
                    documentos_faltantes = [doc['nombre'] for doc in resultado_uc5['faltantes']]
                    warning_msg = f"⚠️ Documentos faltantes según tipo de incapacidad: {', '.join(documentos_faltantes)}. Gestión Humana podrá solicitarlos posteriormente."
                    
                    if is_ajax:
                        warnings.append(warning_msg)
                    else:
                        flash(warning_msg, 'warning')
                    
                    logger.info(f"📋 UC5: Documentos faltantes identificados: {', '.join(documentos_faltantes)}")
                else:
                    success_msg = "✅ UC5: Documentación completa según tipo de incapacidad"
                    if is_ajax:
                        warnings.append(success_msg)
                    else:
                        flash(success_msg, 'success')
                    
                    logger.info("✅ UC5: Validación completa - todos los requisitos cumplidos")
                    
            except Exception as e:
                # Si falla UC5, registrar error pero NO bloquear el registro
                logger.error(f"❌ UC5: Error en validación de requisitos: {str(e)}")
                import traceback
                traceback.print_exc()
                
                error_msg = f"⚠️ UC5: Error en validación automática: {str(e)}. La incapacidad se registrará normalmente."
                if is_ajax:
                    warnings.append(error_msg)
                else:
                    flash(error_msg, 'warning')
                
                # Guardar error en validacion_uc5 para debugging
                incapacidad.validacion_uc5 = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'completo': False
                }
            
            # Procesar archivos (puede lanzar excepciones)
            archivos_guardados, errores_archivos = procesar_archivos(request.files, incapacidad.id)
            
            # UC6: Ya NO requerimos documentos en el registro inicial
            # El auxiliar los solicitará después si faltan
            # if archivos_guardados == 0:
            #     raise ValueError('No se cargaron documentos.')
            
            # Si hay errores en archivos, informar pero continuar
            warnings = []
            if errores_archivos:
                warnings = errores_archivos
                for error in errores_archivos:
                    flash(error, 'warning')
            
            # ✅ COMMIT: Todo exitoso
            db.session.commit()
            
            # ========================================
            # POST-COMMIT: Hooks e Integraciones
            # (NO revertir transacción si fallan)
            # ========================================
            
            # UC15: Confirmar almacenamiento definitivo
            try:
                almacenamiento_ok = confirmar_almacenamiento_definitivo(incapacidad)
                if not almacenamiento_ok:
                    print(f"⚠️ UC15: Advertencia en confirmación de almacenamiento para #{incapacidad.id}")
            except Exception as e:
                print(f"❌ UC15: Error al confirmar almacenamiento: {e}")
                import traceback
                traceback.print_exc()
                # No interrumpir flujo si falla UC15
            
            # UC2: Enviar notificaciones
            try:
                notificaciones_ok = notificar_nueva_incapacidad(incapacidad)
                if not notificaciones_ok:
                    print(f"⚠️ UC2: Advertencia al enviar notificaciones para #{incapacidad.id}")
                    warning_msg = 'Incapacidad registrada, pero no se pudieron enviar todas las notificaciones'
                    flash(warning_msg, 'warning')
                    warnings.append(warning_msg)
            except Exception as e:
                print(f"❌ UC2: Error al enviar notificaciones: {e}")
                import traceback
                traceback.print_exc()
                warning_msg = 'Incapacidad registrada, pero falló el envío de notificaciones'
                flash(warning_msg, 'warning')
                warnings.append(warning_msg)
            
            # Responder según tipo de petición
            if is_ajax:
                return jsonify({
                    'success': True,
                    'codigo_radicacion': incapacidad.codigo_radicacion,
                    'incapacidad_id': incapacidad.id,
                    'archivos_guardados': archivos_guardados,
                    'warnings': warnings
                }), 200
            
            # Mensaje de éxito con código de radicación
            success_msg = f'✅ Incapacidad registrada exitosamente. Código de radicación: {incapacidad.codigo_radicacion}'
            flash(success_msg, 'success')
            
            if archivos_guardados > 0:
                flash(f'{archivos_guardados} documento(s) cargado(s)', 'info')
            else:
                flash('⚠️ No se cargaron documentos. Gestión Humana podrá solicitarlos posteriormente.', 'warning')
            
            return redirect(url_for('incapacidades.mis_incapacidades'))
            
        except Exception as e:
            # ❌ ROLLBACK: Revertir todo si falla cualquier paso
            db.session.rollback()
            
            # Log del error
            print(f"❌ Error en transacción de registro: {e}")
            import traceback
            traceback.print_exc()
            
            # Limpiar archivos huérfanos si se guardaron
            # (los archivos físicos se guardan antes del commit)
            try:
                if 'incapacidad' in locals() and hasattr(incapacidad, 'id'):
                    limpiar_archivos_huerfanos(incapacidad.id)
            except:
                pass  # Si falla limpieza, no importa
            
            # Responder según tipo de petición
            error_msg = f'Error al registrar incapacidad: {str(e)}. Por favor, intente nuevamente.'
            
            if is_ajax:
                return jsonify({
                    'success': False,
                    'errors': [error_msg]
                }), 500
            
            # Mensaje de error al usuario
            flash(f'❌ {error_msg}', 'danger')
            return redirect(url_for('incapacidades.registrar'))

    return render_template('incapacidades/crear.html')

def procesar_archivos(files, incapacidad_id):
    """
    UC2 + Tarea 3: Cargar documentos con validación completa y metadatos.
    
    Procesa todos los archivos subidos:
    - Valida formato y tamaño
    - Genera nombres únicos (UUID + timestamp)
    - Calcula metadatos (tamaño, checksum, MIME type)
    - Guarda en BD con toda la información
    
    Returns:
        tuple: (archivos_guardados: int, errores: list)
    """
    archivos_guardados = 0
    errores_procesamiento = []
    
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
            
            # Verificar que hay archivo
            if not file or file.filename == '':
                continue
            
            # Procesar archivo completo (validar + guardar + metadatos)
            resultado = procesar_archivo_completo(
                file, 
                tipo_doc, 
                incapacidad_id,
                Config.UPLOAD_FOLDER
            )
            
            if resultado['exito']:
                # Crear documento en BD con metadatos completos
                metadatos = resultado['metadatos']
                
                documento = Documento(
                    incapacidad_id=incapacidad_id,
                    nombre_archivo=metadatos['nombre_archivo'],
                    nombre_unico=metadatos['nombre_unico'],
                    ruta=metadatos['ruta'],
                    tipo_documento=tipo_doc,
                    tamaño_bytes=metadatos['tamaño_bytes'],
                    checksum_md5=metadatos['checksum_md5'],
                    mime_type=metadatos['mime_type']
                )
                
                db.session.add(documento)
                archivos_guardados += 1
            else:
                # Acumular errores
                for error in resultado['errores']:
                    errores_procesamiento.append(f"{tipo_doc}: {error}")

    # Commit solo si todo fue exitoso
    if archivos_guardados > 0:
        db.session.commit()
    
    return archivos_guardados, errores_procesamiento

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
    from app.models.enums import EstadoIncapacidadEnum
    
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado. Solo Auxiliar RRHH puede acceder.', 'danger')
        return redirect(url_for('auth.index'))

    # Obtener incapacidades en diferentes estados (compatibilidad legacy + nuevos)
    pendientes = Incapacidad.query.filter(
        Incapacidad.estado.in_([
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
            'Pendiente'  # Legacy
        ])
    ).all()
    
    en_revision = Incapacidad.query.filter(
        Incapacidad.estado.in_([
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value,
            'En revision'  # Legacy
        ])
    ).all()
    
    aprobadas = Incapacidad.query.filter(
        Incapacidad.estado.in_([
            EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION.value,
            'Aprobada'  # Legacy
        ])
    ).all()
    
    rechazadas = Incapacidad.query.filter(
        Incapacidad.estado.in_([
            EstadoIncapacidadEnum.RECHAZADA.value,
            'Rechazada'  # Legacy
        ])
    ).all()

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
    from app.models.enums import EstadoIncapacidadEnum
    
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado. Solo Auxiliar RRHH puede validar documentación.', 'danger')
        return redirect(url_for('auth.index'))
    
    incapacidad = Incapacidad.query.get_or_404(id)
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        if accion == 'completar_revision':
            # Marcar como documentacion completa
            incapacidad.estado = EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value
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
        
        elif accion == 'solicitar_documentos_uc6':
            # UC6: Redirigir a formulario de solicitud de documentos
            return redirect(url_for('incapacidades.solicitar_documentos', incapacidad_id=id))
    
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
    from app.models.enums import EstadoIncapacidadEnum
    
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado. Solo Auxiliar RRHH puede aprobar/rechazar incapacidades.', 'danger')
        return redirect(url_for('auth.index'))
    
    incapacidad = Incapacidad.query.get_or_404(id)
    
    # Solo se puede aprobar/rechazar si esta en revision/documentacion completa
    estados_validos = [
        EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value,
        'En revision',  # Legacy
        EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
        'Pendiente'  # Legacy
    ]
    
    if incapacidad.estado not in estados_validos:
        flash('Esta incapacidad ya fue procesada', 'warning')
        return redirect(url_for('incapacidades.dashboard_auxiliar'))
    
    if request.method == 'POST':
        decision = request.form.get('decision')
        
        if decision == 'aprobar':
            incapacidad.estado = EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION.value
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
            
            incapacidad.estado = EstadoIncapacidadEnum.RECHAZADA.value
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
    from app.models.enums import EstadoIncapacidadEnum
    
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.index'))
    
    total = Incapacidad.query.count()
    
    pendientes = Incapacidad.query.filter(
        Incapacidad.estado.in_([
            EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
            'Pendiente'
        ])
    ).count()
    
    en_revision = Incapacidad.query.filter(
        Incapacidad.estado.in_([
            EstadoIncapacidadEnum.DOCUMENTACION_COMPLETA.value,
            'En revision'
        ])
    ).count()
    
    aprobadas = Incapacidad.query.filter(
        Incapacidad.estado.in_([
            EstadoIncapacidadEnum.APROBADA_PENDIENTE_TRANSCRIPCION.value,
            'Aprobada'
        ])
    ).count()
    
    rechazadas = Incapacidad.query.filter(
        Incapacidad.estado.in_([
            EstadoIncapacidadEnum.RECHAZADA.value,
            'Rechazada'
        ])
    ).count()
    
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
        resultado['recomendaciones'].append('✅ Todos los documentos obligatorios estan presentes')
    
    return resultado


# ============================================================================
# RUTAS UC6: SOLICITAR DOCUMENTOS FALTANTES
# ============================================================================

@incapacidades_bp.route('/<int:incapacidad_id>/solicitar-documentos', methods=['GET'])
@login_required
def solicitar_documentos(incapacidad_id):
    """
    RUTA 1 UC6: Mostrar formulario para solicitar documentos faltantes.
    Acceso: Solo AUXILIAR_GH
    
    Lógica:
    1. Si hay solicitudes PENDIENTES → Mostrar esas solicitudes con estado de documentos
    2. Si NO hay solicitudes PENDIENTES → Mostrar documentos requeridos para crear nuevas
    """
    from app.routes.auth import require_role
    from app.models.enums import EstadoIncapacidadEnum, TipoDocumentoEnum, EstadoSolicitudDocumentoEnum
    from app.models.solicitud_documento import SolicitudDocumento
    from app.utils.validaciones import obtener_documentos_requeridos
    
    # Verificar rol auxiliar
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado. Solo auxiliares pueden solicitar documentos.', 'danger')
        return redirect(url_for('incapacidades.dashboard_auxiliar'))
    
    # Obtener incapacidad
    incapacidad = Incapacidad.query.get_or_404(incapacidad_id)
    
    # Verificar estado válido - Aceptar tanto el nuevo estado como el antiguo
    estados_validos = [
        EstadoIncapacidadEnum.PENDIENTE_VALIDACION.value,
        'Pendiente'  # Estado legacy para retrocompatibilidad
    ]
    
    if incapacidad.estado not in estados_validos:
        flash(f'La incapacidad debe estar en estado PENDIENTE. Estado actual: {incapacidad.estado}', 'warning')
        return redirect(url_for('incapacidades.dashboard_auxiliar'))
    
    # MAPEO: Convertir tipos de documento para mostrar correctamente
    mapeo_inverso = {
        'CERTIFICADO_INCAPACIDAD': 'certificado',
        'EPICRISIS': 'epicrisis',
        'FURIPS': 'furips',
        'CERTIFICADO_NACIDO_VIVO': 'certificado_nacido_vivo',
        'REGISTRO_CIVIL': 'registro_civil',
        'DOCUMENTO_IDENTIDAD': 'documento_identidad_madre',
    }
    
    # Nombres legibles para mostrar en el template
    nombres_legibles = {
        'certificado': 'Certificado de Incapacidad',
        'epicrisis': 'Epicrisis o Documento Soporte',
        'furips': 'FURIPS',
        'certificado_nacido_vivo': 'Certificado de Nacido Vivo',
        'registro_civil': 'Registro Civil',
        'documento_identidad_madre': 'Documento de Identidad de la Madre',
    }
    
    # Obtener documentos ya cargados
    documentos_cargados = Documento.query.filter_by(incapacidad_id=incapacidad.id).all()
    tipos_cargados = {doc.tipo_documento for doc in documentos_cargados}
    
    # Obtener solicitudes de documentos PENDIENTES (no respondidas)
    solicitudes_pendientes = SolicitudDocumento.query.filter_by(
        incapacidad_id=incapacidad.id,
        estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value
    ).all()
    
    documentos_disponibles = []
    es_visualizacion = False
    
    if solicitudes_pendientes:
        # CASO 1: Hay solicitudes pendientes → Mostrar esas (visualización de solicitudes existentes)
        es_visualizacion = True
        
        for solicitud in solicitudes_pendientes:
            # El tipo_documento en solicitud está guardado como enum (CERTIFICADO_INCAPACIDAD)
            doc_tipo_enum = solicitud.tipo_documento
            doc_tipo_simple = mapeo_inverso.get(doc_tipo_enum, doc_tipo_enum)
            
            # Verificar si el documento está cargado
            documento_cargado = doc_tipo_simple in tipos_cargados
            
            documentos_disponibles.append({
                'tipo': doc_tipo_simple,
                'tipo_enum': doc_tipo_enum,
                'nombre_legible': nombres_legibles.get(doc_tipo_simple, doc_tipo_simple),
                'requerido': True,  # Todo lo que está en solicitud es requerido
                'cargado': documento_cargado,
                'falta': not documento_cargado,
                'solicitud_id': solicitud.id,
                'observaciones_auxiliar': solicitud.observaciones_auxiliar
            })
    else:
        # CASO 2: No hay solicitudes pendientes → Mostrar documentos requeridos para crear nuevas
        requisitos = obtener_documentos_requeridos(incapacidad.tipo, incapacidad.dias)
        
        # Documentos obligatorios
        for doc_tipo_enum in requisitos.get('obligatorios', []):
            doc_tipo_simple = mapeo_inverso.get(doc_tipo_enum, doc_tipo_enum)
            documento_cargado = doc_tipo_simple in tipos_cargados
            documentos_disponibles.append({
                'tipo': doc_tipo_simple,
                'tipo_enum': doc_tipo_enum,
                'nombre_legible': nombres_legibles.get(doc_tipo_simple, doc_tipo_simple),
                'requerido': True,
                'cargado': documento_cargado,
                'falta': not documento_cargado
            })
        
        # Documentos opcionales
        for doc_tipo_enum in requisitos.get('opcionales', []):
            doc_tipo_simple = mapeo_inverso.get(doc_tipo_enum, doc_tipo_enum)
            documento_cargado = doc_tipo_simple in tipos_cargados
            documentos_disponibles.append({
                'tipo': doc_tipo_simple,
                'tipo_enum': doc_tipo_enum,
                'nombre_legible': nombres_legibles.get(doc_tipo_simple, doc_tipo_simple),
                'requerido': False,
                'cargado': documento_cargado,
                'falta': not documento_cargado
            })
    
    return render_template(
        'solicitar_documentos.html',
        incapacidad=incapacidad,
        documentos_disponibles=documentos_disponibles,
        TipoDocumentoEnum=TipoDocumentoEnum,
        es_visualizacion=es_visualizacion
    )


@incapacidades_bp.route('/<int:incapacidad_id>/solicitar-documentos', methods=['POST'])
@login_required
def procesar_solicitud_documentos(incapacidad_id):
    """
    RUTA 2 UC6: Crear solicitud y notificar al colaborador.
    Acceso: Solo AUXILIAR_GH
    """
    from app.services.solicitud_documentos_service import SolicitudDocumentosService
    from app.models.enums import TipoDocumentoEnum
    
    # Verificar rol auxiliar
    if current_user.rol != 'auxiliar':
        flash('Acceso denegado. Solo auxiliares pueden solicitar documentos.', 'danger')
        return redirect(url_for('incapacidades.dashboard_auxiliar'))
    
    # Obtener incapacidad
    incapacidad = Incapacidad.query.get_or_404(incapacidad_id)
    
    # Obtener documentos seleccionados del formulario
    documentos_seleccionados = request.form.getlist('documentos[]')
    
    # Validar que al menos 1 documento seleccionado
    if not documentos_seleccionados:
        flash('Debe seleccionar al menos un documento para solicitar.', 'warning')
        return redirect(url_for('incapacidades.solicitar_documentos', incapacidad_id=incapacidad_id))
    
    # MAPEO: Convertir tipos de documento legibles a valores del enum
    mapeo_tipos = {
        'certificado': TipoDocumentoEnum.CERTIFICADO_INCAPACIDAD.value,
        'epicrisis': TipoDocumentoEnum.EPICRISIS.value,
        'furips': TipoDocumentoEnum.FURIPS.value,
        'certificado_nacido_vivo': TipoDocumentoEnum.CERTIFICADO_NACIDO_VIVO.value,
        'registro_civil': TipoDocumentoEnum.REGISTRO_CIVIL.value,
        'documento_identidad_madre': TipoDocumentoEnum.DOCUMENTO_IDENTIDAD.value,
    }
    
    # Convertir documentos seleccionados usando el mapeo
    documentos_mapeados = []
    for doc in documentos_seleccionados:
        doc_mapeado = mapeo_tipos.get(doc, doc)  # Usar valor mapeado o el original si no existe
        documentos_mapeados.append(doc_mapeado)
    
    # Construir observaciones_por_tipo (usando tipos mapeados como key)
    observaciones_por_tipo = {}
    for doc_original, doc_mapeado in zip(documentos_seleccionados, documentos_mapeados):
        observacion = request.form.get(f'observacion_{doc_original}', '')
        if observacion.strip():
            observaciones_por_tipo[doc_mapeado] = observacion.strip()
    
    # Llamar al servicio con documentos mapeados
    exito, mensaje, solicitudes = SolicitudDocumentosService.crear_solicitud_documentos(
        incapacidad_id=incapacidad.id,
        documentos_a_solicitar=documentos_mapeados,
        observaciones_por_tipo=observaciones_por_tipo,
        usuario_auxiliar=current_user
    )
    
    if not exito:
        flash(f'Error al crear solicitud: {mensaje}', 'danger')
        return redirect(url_for('incapacidades.solicitar_documentos', incapacidad_id=incapacidad_id))
    
    # Éxito
    flash(f'✅ {mensaje} El colaborador será notificado por correo.', 'success')
    return redirect(url_for('incapacidades.dashboard_auxiliar'))


@incapacidades_bp.route('/<int:incapacidad_id>/cargar-documentos-solicitados', methods=['GET'])
@login_required
def cargar_documentos_solicitados(incapacidad_id):
    """
    RUTA 3 UC6: Mostrar formulario para cargar documentos solicitados.
    Acceso: Solo COLABORADOR propietario
    """
    from app.models.solicitud_documento import SolicitudDocumento
    from app.models.enums import EstadoIncapacidadEnum, EstadoSolicitudDocumentoEnum
    from app.utils.calendario import dias_habiles_restantes, formatar_fecha_legible
    from datetime import datetime, date
    
    # Obtener incapacidad
    incapacidad = Incapacidad.query.get_or_404(incapacidad_id)
    
    # Verificar que es el propietario
    if current_user.rol != 'colaborador' or incapacidad.usuario_id != current_user.id:
        flash('Acceso denegado. Solo el colaborador propietario puede cargar documentos.', 'danger')
        return redirect(url_for('incapacidades.mis_incapacidades'))
    
    # Verificar estado válido
    if incapacidad.estado != EstadoIncapacidadEnum.DOCUMENTACION_INCOMPLETA.value:
        flash(f'No hay solicitudes de documentos pendientes para esta incapacidad.', 'info')
        return redirect(url_for('incapacidades.mis_incapacidades'))
    
    # Obtener solicitudes pendientes
    solicitudes = SolicitudDocumento.query.filter_by(
        incapacidad_id=incapacidad.id,
        estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value
    ).all()
    
    if not solicitudes:
        flash('No hay documentos pendientes de entrega.', 'info')
        return redirect(url_for('incapacidades.mis_incapacidades'))
    
    # Calcular días restantes y estado para cada solicitud
    fecha_hoy = date.today()
    tiene_vencidas = False
    
    for solicitud in solicitudes:
        solicitud.dias_restantes_calc = solicitud.dias_restantes()
        solicitud.esta_vencida_calc = solicitud.esta_vencida()
        solicitud.fecha_vencimiento_formateada = formatar_fecha_legible(solicitud.fecha_vencimiento)
        
        if solicitud.esta_vencida_calc:
            tiene_vencidas = True
            solicitud.clase_urgencia = 'danger'
        elif solicitud.dias_restantes_calc <= 1:
            solicitud.clase_urgencia = 'warning'
        else:
            solicitud.clase_urgencia = 'info'
    
    return render_template(
        'cargar_documentos_solicitados.html',
        incapacidad=incapacidad,
        solicitudes=solicitudes,
        tiene_vencidas=tiene_vencidas
    )


@incapacidades_bp.route('/<int:incapacidad_id>/cargar-documentos-solicitados', methods=['POST'])
@login_required
def procesar_cargar_documentos_solicitados(incapacidad_id):
    """
    RUTA 4 UC6: Recibir documentos y actualizar estado.
    Acceso: Solo COLABORADOR propietario
    Soporta AJAX (respuesta JSON)
    """
    from app.services.solicitud_documentos_service import SolicitudDocumentosService
    from app.models.solicitud_documento import SolicitudDocumento
    from app.models.enums import EstadoSolicitudDocumentoEnum
    
    # Obtener incapacidad
    incapacidad = Incapacidad.query.get_or_404(incapacidad_id)
    
    # Verificar que es el propietario
    if current_user.rol != 'colaborador' or incapacidad.usuario_id != current_user.id:
        return jsonify({'success': False, 'errors': ['Acceso denegado']}), 403
    
    # Obtener archivos del formulario
    archivos_subidos = []
    errores_validacion = []
    
    # Obtener solicitudes pendientes para mapear archivos
    solicitudes_pendientes = SolicitudDocumento.query.filter_by(
        incapacidad_id=incapacidad.id,
        estado=EstadoSolicitudDocumentoEnum.PENDIENTE.value
    ).all()
    
    # Procesar cada archivo por tipo de documento
    for solicitud in solicitudes_pendientes:
        archivo_key = f'documento_{solicitud.tipo_documento}'
        
        if archivo_key not in request.files:
            continue
        
        archivo = request.files[archivo_key]
        
        if archivo.filename == '':
            continue
        
        # Validar formato
        if not allowed_file(archivo.filename):
            errores_validacion.append(
                f'{solicitud.tipo_documento}: Formato no permitido. Use PDF, JPG, PNG o JPEG.'
            )
            continue
        
        # Validar tamaño (10MB = 10 * 1024 * 1024 bytes)
        archivo.seek(0, 2)  # Ir al final
        tamaño = archivo.tell()
        archivo.seek(0)  # Volver al inicio
        
        if tamaño > 10 * 1024 * 1024:
            errores_validacion.append(
                f'{solicitud.tipo_documento}: Archivo muy grande ({tamaño / 1024 / 1024:.2f} MB). Máximo 10MB.'
            )
            continue
        
        # Procesar archivo válido
        try:
            resultado = procesar_archivo_completo(
                file=archivo,
                tipo_documento=solicitud.tipo_documento,
                incapacidad_id=incapacidad.id,
                upload_folder=current_app.config['UPLOAD_FOLDER']
            )
            
            # Verificar si fue exitoso
            if not resultado['exito']:
                errores_validacion.extend(resultado['errores'])
                continue
            
            metadatos = resultado['metadatos']
            
            # IMPORTANTE: Convertir tipo_documento a tipo simple (no enum)
            # Los documentos en BD deben guardarse siempre como tipos simples
            mapeo_tipo_simple = {
                'CERTIFICADO_INCAPACIDAD': 'certificado',
                'EPICRISIS': 'epicrisis',
                'FURIPS': 'furips',
                'CERTIFICADO_NACIDO_VIVO': 'certificado_nacido_vivo',
                'REGISTRO_CIVIL': 'registro_civil',
                'DOCUMENTO_IDENTIDAD': 'documento_identidad_madre',
            }
            tipo_simple = mapeo_tipo_simple.get(solicitud.tipo_documento, solicitud.tipo_documento)
            
            # Crear objeto Documento
            documento = Documento(
                incapacidad_id=incapacidad.id,
                nombre_archivo=metadatos['nombre_archivo'],
                nombre_unico=metadatos['nombre_unico'],
                ruta=metadatos['ruta'],
                tipo_documento=tipo_simple,  # Guardar como tipo simple
                tamaño_bytes=metadatos['tamaño_bytes'],
                mime_type=metadatos['mime_type']
            )
            
            db.session.add(documento)
            archivos_subidos.append(documento)
            
        except Exception as e:
            errores_validacion.append(f'{solicitud.tipo_documento}: Error al procesar archivo - {str(e)}')
    
    # Si hay errores de validación, retornar sin procesar
    if errores_validacion:
        return jsonify({'success': False, 'errors': errores_validacion}), 400
    
    # Si no se subió ningún archivo
    if not archivos_subidos:
        return jsonify({'success': False, 'errors': ['Debe cargar al menos un documento']}), 400
    
    # Commit de documentos a BD
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'errors': [f'Error al guardar documentos: {str(e)}']}), 500
    
    # Llamar al servicio para validar respuesta
    completo, errores_servicio, pendientes = SolicitudDocumentosService.validar_respuesta_colaborador(
        incapacidad_id=incapacidad.id,
        documentos_entregados=archivos_subidos
    )
    
    if errores_servicio:
        return jsonify({'success': False, 'errors': errores_servicio}), 400
    
    # Si todos los documentos fueron entregados
    if completo:
        return jsonify({
            'success': True,
            'message': '✅ Todos los documentos fueron entregados exitosamente.',
            'codigo_radicacion': incapacidad.codigo_radicacion,
            'completo': True
        }), 200
    else:
        # Entrega parcial
        # Mapear tipos enum a nombres legibles
        nombres_legibles = {
            'CERTIFICADO_INCAPACIDAD': 'Certificado de Incapacidad',
            'EPICRISIS': 'Epicrisis o Documento Soporte',
            'FURIPS': 'FURIPS',
            'CERTIFICADO_NACIDO_VIVO': 'Certificado de Nacido Vivo',
            'REGISTRO_CIVIL': 'Registro Civil',
            'DOCUMENTO_IDENTIDAD': 'Documento de Identidad de la Madre',
        }
        documentos_pendientes_nombres = [
            nombres_legibles.get(p.tipo_documento, p.tipo_documento) 
            for p in pendientes
        ]
        return jsonify({
            'success': True,
            'message': f'✅ Documentos cargados. Aún faltan: {", ".join(documentos_pendientes_nombres)}',
            'codigo_radicacion': incapacidad.codigo_radicacion,
            'completo': False,
            'pendientes': documentos_pendientes_nombres
        }), 200


@incapacidades_bp.route('/<int:incapacidad_id>/historial-estados', methods=['GET'])
@login_required
def historial_estados(incapacidad_id):
    """
    RUTA 5 UC6: Mostrar historial completo de cambios de estado (auditoría).
    Acceso: Propietario, AUXILIAR_GH o ADMINISTRADOR
    """
    from app.models.historial_estado import HistorialEstado
    
    # Obtener incapacidad
    incapacidad = Incapacidad.query.get_or_404(incapacidad_id)
    
    # Verificar permisos
    puede_ver = (
        current_user.id == incapacidad.usuario_id or  # Propietario
        current_user.rol == 'auxiliar' or             # Auxiliar
        current_user.rol == 'admin'                   # Admin
    )
    
    if not puede_ver:
        flash('Acceso denegado. No tiene permisos para ver este historial.', 'danger')
        return redirect(url_for('incapacidades.mis_incapacidades'))
    
    # Obtener historial ordenado por fecha DESC
    historial = HistorialEstado.query.filter_by(
        incapacidad_id=incapacidad.id
    ).order_by(HistorialEstado.fecha_cambio.desc()).all()
    
    return render_template(
        'historial_estados.html',
        incapacidad=incapacidad,
        historial=historial
    )

# =============================================================================
# UC5: ENDPOINTS API PARA VALIDACIÓN DE DOCUMENTOS
# =============================================================================

@incapacidades_bp.route('/api/documentos-requeridos/<tipo>')
@login_required
def obtener_documentos_requeridos(tipo):
    """
    UC5: API endpoint para obtener documentos requeridos por tipo de incapacidad.
    Utiliza el ValidadorRequisitos para determinar qué documentos son necesarios.
    
    Parámetros:
        tipo: Tipo de incapacidad (str)
        dias: Días de incapacidad (query param, opcional)
    
    Retorna:
        JSON con documentos obligatorios y condicionales
    """
    try:
        from app.services.validacion_requisitos_service import ValidadorRequisitos
        
        # Obtener días si están proporcionados
        dias = request.args.get('dias', type=int, default=1)
        
        # Crear validador
        validador = ValidadorRequisitos()
        
        # Obtener requisitos usando el nuevo método
        requisitos = validador.obtener_requisitos_por_tipo_y_dias(tipo, dias)
        
        return jsonify({
            'tipo': tipo,
            'dias': dias,
            'obligatorios': requisitos['obligatorios'],
            'condicionales': requisitos['condicionales'],
            'total': requisitos['total']
        })
        
    except ImportError:
        # Fallback si no está disponible ValidadorRequisitos
        return jsonify({
            'error': 'Servicio de validación no disponible',
            'obligatorios': ['CERTIFICADO_INCAPACIDAD'],
            'condicionales': []
        }), 503
        
    except Exception as e:
        current_app.logger.error(f'Error obteniendo documentos requeridos: {e}')
        return jsonify({
            'error': 'Error interno del servidor',
            'obligatorios': ['CERTIFICADO_INCAPACIDAD'],
            'condicionales': []
        }), 500