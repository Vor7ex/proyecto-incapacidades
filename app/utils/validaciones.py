from datetime import date
import os

def validar_rango_fechas(fecha_inicio, fecha_fin):
    """Validar que el rango de fechas sea coherente"""
    errores = []
    
    if fecha_fin < fecha_inicio:
        errores.append('La fecha de fin debe ser posterior a la fecha de inicio')
    
    if fecha_inicio > date.today():
        errores.append('La fecha de inicio no puede ser futura')
    
    dias = (fecha_fin - fecha_inicio).days + 1
    if dias > 180:
        errores.append('El periodo de incapacidad no puede superar 180 dias')
    
    return errores

def validar_archivo(file):
    """Validar que el archivo cumpla requisitos"""
    errores = []
    
    if not file or file.filename == '':
        errores.append('No se ha seleccionado ningun archivo')
        return errores
    
    # Validar extension
    extensiones_permitidas = {'pdf', 'png', 'jpg', 'jpeg'}
    extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if extension not in extensiones_permitidas:
        errores.append(f'Extension .{extension} no permitida. Use: {", ".join(extensiones_permitidas)}')
    
    # Validar tamaño (obtener tamaño del archivo)
    file.seek(0, os.SEEK_END)
    tamaño = file.tell()
    file.seek(0)
    
    tamaño_mb = tamaño / (1024 * 1024)
    if tamaño_mb > 10:
        errores.append(f'El archivo pesa {tamaño_mb:.2f}MB. El maximo permitido es 10MB')
    
    return errores

def validar_integridad_sistema():
    """Validar integridad del sistema"""
    from app.models.incapacidad import Incapacidad
    from app.models.documento import Documento
    
    problemas = []
    
    # Verificar incapacidades sin documentos
    incapacidades_sin_docs = Incapacidad.query.filter(
        ~Incapacidad.documentos.any()
    ).all()
    
    if incapacidades_sin_docs:
        problemas.append(f'{len(incapacidades_sin_docs)} incapacidades sin documentos adjuntos')
    
    # Verificar documentos sin archivo fisico
    documentos = Documento.query.all()
    archivos_faltantes = []
    
    for doc in documentos:
        if not os.path.exists(doc.ruta):
            archivos_faltantes.append(doc.id)
    
    if archivos_faltantes:
        problemas.append(f'{len(archivos_faltantes)} documentos sin archivo fisico')
    
    return problemas