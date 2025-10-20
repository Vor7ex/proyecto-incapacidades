from datetime import date
import os
import uuid
import hashlib

# Mapeo de documentos obligatorios según tipo de incapacidad (UC1 - Sección 5.1.2)
# ACTUALIZADO: Usar valores del enum TipoDocumentoEnum para compatibilidad con UC6
DOCUMENTOS_REQUERIDOS_POR_TIPO = {
    'Enfermedad General': {
        'obligatorios': ['CERTIFICADO_INCAPACIDAD'],
        'opcionales': ['EPICRISIS'],  # Obligatorio si > 2 días
        'reglas_especiales': {
            'EPICRISIS': lambda dias: dias > 2
        }
    },
    'Accidente Laboral': {
        'obligatorios': ['CERTIFICADO_INCAPACIDAD', 'EPICRISIS'],
        'opcionales': [],
        'reglas_especiales': {}
    },
    'Accidente de Tránsito': {
        'obligatorios': ['CERTIFICADO_INCAPACIDAD', 'EPICRISIS', 'FURIPS'],
        'opcionales': [],
        'reglas_especiales': {}
    },
    'Licencia de Maternidad': {
        'obligatorios': ['CERTIFICADO_INCAPACIDAD', 'EPICRISIS', 'CERTIFICADO_NACIDO_VIVO', 'REGISTRO_CIVIL'],
        'opcionales': ['DOCUMENTO_IDENTIDAD'],
        'reglas_especiales': {}
    },
    'Licencia de Paternidad': {
        'obligatorios': ['EPICRISIS', 'CERTIFICADO_NACIDO_VIVO', 'REGISTRO_CIVIL', 'DOCUMENTO_IDENTIDAD'],
        'opcionales': ['CERTIFICADO_INCAPACIDAD'],
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
        # Traducir nombres técnicos a nombres legibles (usando enums)
        nombres_legibles = {
            'CERTIFICADO_INCAPACIDAD': 'Certificado de Incapacidad',
            'EPICRISIS': 'Epicrisis o Documento Soporte',
            'FURIPS': 'FURIPS (Formulario Único de Reclamación)',
            'CERTIFICADO_NACIDO_VIVO': 'Certificado de Nacido Vivo',
            'REGISTRO_CIVIL': 'Registro Civil',
            'DOCUMENTO_IDENTIDAD': 'Documento de Identidad',
            # Mantener retrocompatibilidad con nombres antiguos
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

def generar_nombre_unico(nombre_original, tipo_documento, incapacidad_id):
    """
    Generar nombre único para archivo usando UUID + timestamp.
    
    Args:
        nombre_original (str): Nombre original del archivo
        tipo_documento (str): Tipo de documento (certificado, epicrisis, etc.)
        incapacidad_id (int): ID de la incapacidad
    
    Returns:
        str: Nombre único en formato: INC{id}_{tipo}_{timestamp}_{uuid}_{nombre_seguro}
    
    Ejemplo: INC123_certificado_20251013123045_a1b2c3d4_cert.pdf
    """
    from datetime import datetime
    from werkzeug.utils import secure_filename
    
    # Timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # UUID corto (primeros 8 caracteres)
    uuid_short = str(uuid.uuid4())[:8]
    
    # Nombre seguro
    nombre_seguro = secure_filename(nombre_original)
    
    # Formato: INC{id}_{tipo}_{timestamp}_{uuid}_{nombre_original}
    nombre_unico = f"INC{incapacidad_id}_{tipo_documento}_{timestamp}_{uuid_short}_{nombre_seguro}"
    
    return nombre_unico

def calcular_checksum_md5(file):
    """
    Calcular checksum MD5 del archivo.
    
    Args:
        file: Objeto FileStorage de Flask
    
    Returns:
        str: Hash MD5 en hexadecimal
    """
    md5_hash = hashlib.md5()
    
    # Leer archivo en chunks para no cargar todo en memoria
    file.seek(0)
    for chunk in iter(lambda: file.read(4096), b""):
        md5_hash.update(chunk)
    
    file.seek(0)  # Reset para posterior lectura
    return md5_hash.hexdigest()

def obtener_mime_type(filename):
    """
    Obtener el tipo MIME basado en la extensión del archivo.
    
    Args:
        filename (str): Nombre del archivo
    
    Returns:
        str: Tipo MIME
    """
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    mime_types = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg'
    }
    
    return mime_types.get(extension, 'application/octet-stream')

def procesar_archivo_completo(file, tipo_documento, incapacidad_id, upload_folder):
    """
    Procesar archivo completo: validar, generar nombre único, calcular metadatos y guardar.
    
    Args:
        file: Objeto FileStorage de Flask
        tipo_documento (str): Tipo de documento
        incapacidad_id (int): ID de la incapacidad
        upload_folder (str): Carpeta de destino
    
    Returns:
        dict: {
            'exito': bool,
            'errores': list,
            'metadatos': dict o None
        }
    
    Metadatos incluyen:
        - nombre_archivo: Nombre original
        - nombre_unico: Nombre generado único
        - ruta: Ruta completa del archivo
        - tamaño_bytes: Tamaño en bytes
        - checksum_md5: Hash MD5
        - mime_type: Tipo MIME
    """
    # 1. Validar archivo
    errores = validar_archivo(file)
    if errores:
        return {
            'exito': False,
            'errores': errores,
            'metadatos': None
        }
    
    try:
        # 2. Generar nombre único
        nombre_unico = generar_nombre_unico(file.filename, tipo_documento, incapacidad_id)
        
        # 3. Calcular tamaño
        file.seek(0, os.SEEK_END)
        tamaño_bytes = file.tell()
        file.seek(0)
        
        # 4. Calcular checksum (opcional, puede ser costoso)
        checksum_md5 = calcular_checksum_md5(file)
        
        # 5. Obtener MIME type
        mime_type = obtener_mime_type(file.filename)
        
        # 6. Construir ruta completa
        ruta_completa = os.path.join(upload_folder, nombre_unico)
        
        # 7. Guardar archivo
        file.save(ruta_completa)
        
        # 8. Verificar que se guardó correctamente
        if not os.path.exists(ruta_completa):
            return {
                'exito': False,
                'errores': ['Error al guardar el archivo en el servidor'],
                'metadatos': None
            }
        
        # 9. Retornar metadatos
        metadatos = {
            'nombre_archivo': file.filename,
            'nombre_unico': nombre_unico,
            'ruta': ruta_completa,
            'tamaño_bytes': tamaño_bytes,
            'checksum_md5': checksum_md5,
            'mime_type': mime_type
        }
        
        return {
            'exito': True,
            'errores': [],
            'metadatos': metadatos
        }
        
    except Exception as e:
        return {
            'exito': False,
            'errores': [f'Error al procesar archivo: {str(e)}'],
            'metadatos': None
        }

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