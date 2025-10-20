"""
Scheduler de tareas periódicas para UC6 - Solicitud de Documentos Faltantes.

Este módulo implementa tareas programadas que se ejecutan automáticamente
para procesar recordatorios de documentación pendiente.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# Scheduler global
scheduler = None


def procesar_recordatorios_documentos():
    """
    Tarea diaria automática que procesa recordatorios de documentos pendientes.
    
    Esta función se ejecuta todos los días a las 08:00 AM para:
    - Identificar solicitudes vencidas o próximas a vencer
    - Enviar recordatorios con tono de urgencia apropiado
    - Actualizar campos de última notificación
    - Marcar solicitudes que requieren citación
    
    Returns:
        bool: True si la ejecución fue exitosa, False en caso de error
    """
    try:
        logger.info("🔄 Iniciando tarea programada: procesar_recordatorios_documentos()")
        
        # Import aquí para evitar circular imports
        from app.services.solicitud_documentos_service import SolicitudDocumentosService
        
        # Ejecutar el procesamiento de recordatorios
        resultado = SolicitudDocumentosService.procesar_recordatorios()
        
        if resultado['exito']:
            logger.info(
                f"✅ Tarea de recordatorios ejecutada correctamente - "
                f"Procesados: {resultado.get('total_procesados', 0)}, "
                f"Recordatorios enviados: {resultado.get('recordatorios_enviados', 0)}"
            )
            return True
        else:
            logger.warning(
                f"⚠️ Tarea de recordatorios completada con advertencias - "
                f"{resultado.get('mensaje', 'Sin detalles')}"
            )
            return True  # No fallar aunque haya advertencias
            
    except Exception as e:
        # En caso de error, loguear pero no fallar completamente
        # El scheduler debe continuar ejecutándose
        logger.error(f"❌ Error en tarea programada de recordatorios: {str(e)}", exc_info=True)
        return False


def registrar_tareas_periodicas(scheduler_instance):
    """
    Registra todas las tareas periódicas de UC6 en el scheduler.
    
    Esta función se ejecuta una vez al startup de la aplicación y configura:
    - Tarea diaria de recordatorios a las 08:00 AM
    - Cualquier otra tarea periódica necesaria para UC6
    
    Args:
        scheduler_instance: Instancia de APScheduler (BackgroundScheduler)
    
    Returns:
        bool: True si las tareas fueron registradas exitosamente
    """
    try:
        logger.info("📋 Registrando tareas periódicas de UC6...")
        
        # Tarea diaria: Procesar recordatorios de documentos a las 08:00 AM
        scheduler_instance.add_job(
            func=procesar_recordatorios_documentos,
            trigger=CronTrigger(hour=8, minute=0),
            id='procesar_recordatorios_uc6',
            name='Procesar recordatorios de documentos UC6',
            replace_existing=True,
            misfire_grace_time=3600  # Permitir 1 hora de gracia si la app estaba apagada
        )
        
        logger.info("✅ Tarea 'procesar_recordatorios_uc6' registrada para ejecutarse diariamente a las 08:00 AM")
        
        # Aquí se podrían agregar más tareas periódicas en el futuro:
        # - Limpieza de documentos antiguos
        # - Reportes automáticos
        # - Auditorías programadas
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al registrar tareas periódicas: {str(e)}", exc_info=True)
        return False


def iniciar_scheduler(app=None):
    """
    Inicializa y arranca el scheduler de tareas periódicas.
    
    Esta función debe ser llamada durante el startup de la aplicación Flask.
    Crea el scheduler, registra las tareas y lo inicia en modo background.
    
    Args:
        app: Instancia de la aplicación Flask (opcional, para logging context)
    
    Returns:
        BackgroundScheduler: Instancia del scheduler iniciado
    """
    global scheduler
    
    try:
        if scheduler is not None:
            logger.warning("⚠️ Scheduler ya está inicializado, omitiendo...")
            return scheduler
        
        logger.info("🚀 Inicializando scheduler de tareas periódicas...")
        
        # Crear scheduler en modo background
        scheduler = BackgroundScheduler(
            timezone='America/Bogota',  # Timezone de Colombia
            daemon=True  # Daemon thread para que termine con la app
        )
        
        # Registrar todas las tareas periódicas
        if registrar_tareas_periodicas(scheduler):
            # Iniciar el scheduler
            scheduler.start()
            logger.info("✅ Scheduler iniciado correctamente")
            
            # Loguear las tareas registradas
            jobs = scheduler.get_jobs()
            logger.info(f"📊 Tareas programadas activas: {len(jobs)}")
            for job in jobs:
                logger.info(f"   - {job.id}: {job.name} (próxima ejecución: {job.next_run_time})")
        else:
            logger.error("❌ No se pudieron registrar las tareas periódicas")
            scheduler = None
        
        return scheduler
        
    except Exception as e:
        logger.error(f"❌ Error al inicializar scheduler: {str(e)}", exc_info=True)
        scheduler = None
        return None


def detener_scheduler():
    """
    Detiene el scheduler de tareas periódicas.
    
    Esta función debe ser llamada durante el shutdown de la aplicación
    para asegurar que todas las tareas se completen apropiadamente.
    """
    global scheduler
    
    if scheduler is not None:
        try:
            logger.info("🛑 Deteniendo scheduler de tareas periódicas...")
            scheduler.shutdown(wait=True)
            scheduler = None
            logger.info("✅ Scheduler detenido correctamente")
        except Exception as e:
            logger.error(f"❌ Error al detener scheduler: {str(e)}", exc_info=True)


def obtener_scheduler():
    """
    Obtiene la instancia global del scheduler.
    
    Returns:
        BackgroundScheduler: Instancia del scheduler o None si no está inicializado
    """
    return scheduler


def ejecutar_tarea_manual(nombre_tarea):
    """
    Ejecuta una tarea programada manualmente (útil para testing y debugging).
    
    Args:
        nombre_tarea (str): Nombre de la tarea a ejecutar ('procesar_recordatorios')
    
    Returns:
        bool: True si la tarea se ejecutó correctamente
    """
    try:
        logger.info(f"🔧 Ejecución manual de tarea: {nombre_tarea}")
        
        if nombre_tarea == 'procesar_recordatorios':
            return procesar_recordatorios_documentos()
        else:
            logger.error(f"❌ Tarea desconocida: {nombre_tarea}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en ejecución manual de tarea: {str(e)}", exc_info=True)
        return False
