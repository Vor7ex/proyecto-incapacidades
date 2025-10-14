from datetime import date
import os

# Mapeo de documentos obligatorios según tipo de incapacidad (UC1 - Sección 5.1.2)
DOCUMENTOS_REQUERIDOS_POR_TIPO = {
    'Enfermedad General': {
        'obligatorios': ['certificado'],
        'opcionales': ['epicrisis'],  # Obligatorio si > 2 días
        'reglas_especiales': {
            'epicrisis': lambda dias: dias > 2
        }
    },
    'Accidente Laboral': {
        'obligatorios': ['certificado', 'epicrisis'],
        'opcionales': [],
        'reglas_especiales': {}
    },
    'Accidente de Tránsito': {
        'obligatorios': ['certificado', 'epicrisis', 'furips'],
        'opcionales': [],
        'reglas_especiales': {}
    },
    'Licencia de Maternidad': {
        'obligatorios': ['certificado', 'epicrisis', 'certificado_nacido_vivo', 'registro_civil'],
        'opcionales': ['documento_identidad_madre'],
        'reglas_especiales': {}
    },
    'Licencia de Paternidad': {
        'obligatorios': ['epicrisis', 'certificado_nacido_vivo', 'registro_civil', 'documento_identidad_madre'],
        'opcionales': ['certificado'],
        'reglas_especiales': {}
    }
}

def obtener_documentos_requeridos(tipo_incapacidad, dias=0):
    """
    Obtener la lista de documentos requeridos para un tipo de incapacidad.
    
    Args:
        tipo_incapacidad (str): Tipo de incapacidad
        dias (int): Número de días de la incapacidad
        
    Returns:
        dict: {
            'obligatorios': list,
            'opcionales': list,
            'todos': list (obligatorios + condicionales aplicables)
        }
    """
    if tipo_incapacidad not in DOCUMENTOS_REQUERIDOS_POR_TIPO:
        return {'obligatorios': ['certificado'], 'opcionales': [], 'todos': ['certificado']}
    
    config = DOCUMENTOS_REQUERIDOS_POR_TIPO[tipo_incapacidad]
    obligatorios = config['obligatorios'].copy()
    opcionales = config['opcionales'].copy()
    
    # Aplicar reglas especiales
    for doc, regla in config.get('reglas_especiales', {}).items():
        if callable(regla) and regla(dias):
            # Si la regla se cumple, el documento opcional se vuelve obligatorio
            if doc in opcionales:
                opcionales.remove(doc)
                obligatorios.append(doc)
    
    return {
        'obligatorios': obligatorios,
        'opcionales': opcionales,
        'todos': obligatorios  # Para validación, solo verificamos obligatorios
    }

def validar_documentos_incapacidad(tipo_incapacidad, documentos_subidos, dias=0):
    """
    Validar que se hayan subido todos los documentos obligatorios según el tipo.
    
    Args:
        tipo_incapacidad (str): Tipo de incapacidad
        documentos_subidos (dict): Dict con archivos subidos {nombre_campo: FileStorage o bool}
        dias (int): Número de días de incapacidad
        
    Returns:
        tuple: (es_valido: bool, documentos_faltantes: list, mensaje_error: str o None)
    """
    requeridos = obtener_documentos_requeridos(tipo_incapacidad, dias)
    documentos_obligatorios = requeridos['todos']
    
    documentos_faltantes = []
    
    # Verificar cada documento obligatorio
    for doc in documentos_obligatorios:
        # Verificar si el documento fue subido
        archivo = documentos_subidos.get(doc)
        
        # El archivo está presente si:
        # - Es un objeto FileStorage con filename no vacío
        # - O es True (para casos donde ya verificamos antes)
        if not archivo:
            documentos_faltantes.append(doc)
        elif hasattr(archivo, 'filename') and (not archivo.filename or archivo.filename == ''):
            documentos_faltantes.append(doc)
    
    if documentos_faltantes:
        # Traducir nombres técnicos a nombres legibles
        nombres_legibles = {
            'certificado': 'Certificado de Incapacidad',
            'epicrisis': 'Epicrisis o Documento Soporte',
            'furips': 'FURIPS (Formulario Único de Reclamación)',
            'certificado_nacido_vivo': 'Certificado de Nacido Vivo',
            'registro_civil': 'Registro Civil',
            'documento_identidad_madre': 'Documento de Identidad de la Madre'
        }
        
        faltantes_legibles = [nombres_legibles.get(d, d) for d in documentos_faltantes]
        mensaje = f"Faltan documentos obligatorios: {', '.join(faltantes_legibles)}"
        
        return False, documentos_faltantes, mensaje
    
    return True, [], None

def validar_tipo_incapacidad(tipo):
    """
    Validar que el tipo de incapacidad sea uno de los permitidos según UC1.
    
    Args:
        tipo (str): Tipo de incapacidad a validar
        
    Returns:
        tuple: (es_valido: bool, mensaje_error: str o None)
    """
    from app.models.incapacidad import TIPOS_VALIDOS
    
    if not tipo or tipo.strip() == '':
        return False, 'El tipo de incapacidad es obligatorio'
    
    tipo_limpio = tipo.strip()
    
    if tipo_limpio not in TIPOS_VALIDOS:
        tipos_permitidos = ', '.join(TIPOS_VALIDOS)
        return False, f'Tipo de incapacidad no válido. Tipos permitidos: {tipos_permitidos}'
    
    return True, None

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