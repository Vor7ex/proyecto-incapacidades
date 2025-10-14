"""
Tests para gestión mejorada de uploads: formato, tamaño, naming y metadatos (Tarea 3)
"""
import sys
import os
import hashlib
import tempfile

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.validaciones import (
    validar_archivo,
    generar_nombre_unico,
    calcular_checksum_md5,
    obtener_mime_type,
    procesar_archivo_completo
)


class FakeFile:
    """Mock de FileStorage para testing"""
    def __init__(self, filename, content=b"test content", size_mb=1):
        self.filename = filename
        self.content = content * int(size_mb * 1024 * 100)  # Aproximado
        self._position = 0
    
    def read(self, size=-1):
        if size == -1:
            result = self.content[self._position:]
            self._position = len(self.content)
            return result
        else:
            result = self.content[self._position:self._position + size]
            self._position += len(result)
            return result
    
    def seek(self, position, whence=0):
        if whence == 0:  # SEEK_SET
            self._position = position
        elif whence == 2:  # SEEK_END
            self._position = len(self.content)
    
    def tell(self):
        return self._position
    
    def save(self, path):
        """Simular guardado de archivo"""
        with open(path, 'wb') as f:
            f.write(self.content)


def test_validar_archivo_valido():
    """Test: Archivos válidos pasan la validación"""
    print("✅ Test: Validación de archivos válidos")
    
    archivos_validos = [
        FakeFile('documento.pdf', size_mb=5),
        FakeFile('imagen.png', size_mb=2),
        FakeFile('foto.jpg', size_mb=3),
        FakeFile('scan.jpeg', size_mb=1),
    ]
    
    for archivo in archivos_validos:
        errores = validar_archivo(archivo)
        assert len(errores) == 0, f"Archivo {archivo.filename} debería ser válido: {errores}"
        print(f"  ✓ {archivo.filename} - VÁLIDO")
    
    print()


def test_validar_archivo_extension_invalida():
    """Test: Extensiones no permitidas son rechazadas"""
    print("❌ Test: Extensiones inválidas")
    
    archivos_invalidos = [
        FakeFile('documento.docx'),
        FakeFile('imagen.gif'),
        FakeFile('archivo.exe'),
        FakeFile('script.sh'),
    ]
    
    for archivo in archivos_invalidos:
        errores = validar_archivo(archivo)
        assert len(errores) > 0, f"Archivo {archivo.filename} debería ser inválido"
        assert any('Extension' in err for err in errores), "Debería mencionar extensión inválida"
        print(f"  ✓ {archivo.filename} - RECHAZADO")
    
    print()


def test_validar_archivo_tamaño_excedido():
    """Test: Archivos mayores a 10MB son rechazados"""
    print("❌ Test: Tamaño excedido (>10MB)")
    
    archivo_grande = FakeFile('documento.pdf', size_mb=15)
    errores = validar_archivo(archivo_grande)
    
    assert len(errores) > 0, "Archivo >10MB debería ser rechazado"
    assert any('10MB' in err or 'maximo' in err.lower() for err in errores)
    print(f"  ✓ Archivo de 15MB - RECHAZADO")
    print()


def test_generar_nombre_unico():
    """Test: Nombres únicos se generan correctamente"""
    print("🔑 Test: Generación de nombres únicos")
    
    nombre1 = generar_nombre_unico('documento.pdf', 'certificado', 123)
    nombre2 = generar_nombre_unico('documento.pdf', 'certificado', 123)
    
    # Los nombres deben ser diferentes (UUID diferente)
    assert nombre1 != nombre2, "Nombres deberían ser únicos"
    
    # Verificar formato
    assert 'INC123' in nombre1, "Debe incluir ID de incapacidad"
    assert 'certificado' in nombre1, "Debe incluir tipo de documento"
    assert 'documento.pdf' in nombre1, "Debe incluir nombre original"
    
    # Verificar que tiene UUID (8 caracteres hex)
    partes = nombre1.split('_')
    assert len(partes) >= 4, "Debe tener al menos 4 partes separadas por _"
    
    print(f"  ✓ Nombre generado 1: {nombre1}")
    print(f"  ✓ Nombre generado 2: {nombre2}")
    print(f"  ✓ Son únicos: {nombre1 != nombre2}")
    print()


def test_calcular_checksum():
    """Test: Checksum MD5 se calcula correctamente"""
    print("🔐 Test: Cálculo de checksum MD5")
    
    content = b"Este es el contenido del archivo de prueba"
    
    # Crear FakeFile sin multiplicar contenido para este test
    archivo = FakeFile.__new__(FakeFile)
    archivo.filename = 'test.pdf'
    archivo.content = content
    archivo._position = 0
    
    checksum = calcular_checksum_md5(archivo)
    
    # Calcular checksum esperado
    md5_esperado = hashlib.md5(content).hexdigest()
    
    assert checksum == md5_esperado, f"Checksum incorrecto: {checksum} != {md5_esperado}"
    assert len(checksum) == 32, "MD5 debe tener 32 caracteres"
    
    print(f"  ✓ Checksum calculado: {checksum}")
    print(f"  ✓ Checksum esperado:  {md5_esperado}")
    print(f"  ✓ Coinciden: {checksum == md5_esperado}")
    print()


def test_obtener_mime_type():
    """Test: Tipo MIME se detecta correctamente"""
    print("📄 Test: Detección de tipo MIME")
    
    casos = [
        ('documento.pdf', 'application/pdf'),
        ('imagen.png', 'image/png'),
        ('foto.jpg', 'image/jpeg'),
        ('scan.jpeg', 'image/jpeg'),
        ('archivo.txt', 'application/octet-stream'),  # No soportado
    ]
    
    for filename, mime_esperado in casos:
        mime = obtener_mime_type(filename)
        assert mime == mime_esperado, f"MIME incorrecto para {filename}: {mime} != {mime_esperado}"
        print(f"  ✓ {filename:<20} → {mime}")
    
    print()


def test_procesar_archivo_completo_exitoso():
    """Test: Procesamiento completo de archivo exitoso"""
    print("✅ Test: Procesamiento completo exitoso")
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as temp_dir:
        archivo = FakeFile('certificado.pdf', size_mb=2)
        
        resultado = procesar_archivo_completo(
            archivo,
            'certificado',
            999,
            temp_dir
        )
        
        assert resultado['exito'], f"Procesamiento debería ser exitoso: {resultado['errores']}"
        assert len(resultado['errores']) == 0, "No debería haber errores"
        assert resultado['metadatos'] is not None, "Debe incluir metadatos"
        
        # Verificar metadatos
        metadatos = resultado['metadatos']
        assert metadatos['nombre_archivo'] == 'certificado.pdf'
        assert 'INC999' in metadatos['nombre_unico']
        assert metadatos['tamaño_bytes'] > 0
        assert len(metadatos['checksum_md5']) == 32
        assert metadatos['mime_type'] == 'application/pdf'
        
        # Verificar que el archivo se guardó
        assert os.path.exists(metadatos['ruta']), "Archivo debería existir"
        
        print(f"  ✓ Nombre original: {metadatos['nombre_archivo']}")
        print(f"  ✓ Nombre único:    {metadatos['nombre_unico']}")
        print(f"  ✓ Tamaño:          {metadatos['tamaño_bytes']} bytes")
        print(f"  ✓ Checksum:        {metadatos['checksum_md5']}")
        print(f"  ✓ MIME type:       {metadatos['mime_type']}")
        print(f"  ✓ Archivo guardado: {os.path.exists(metadatos['ruta'])}")
    
    print()


def test_procesar_archivo_completo_error_extension():
    """Test: Procesamiento rechaza extensiones inválidas"""
    print("❌ Test: Procesamiento rechaza extensión inválida")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        archivo = FakeFile('virus.exe', size_mb=1)
        
        resultado = procesar_archivo_completo(
            archivo,
            'certificado',
            999,
            temp_dir
        )
        
        assert not resultado['exito'], "Procesamiento debería fallar"
        assert len(resultado['errores']) > 0, "Debe incluir errores"
        assert resultado['metadatos'] is None, "No debe incluir metadatos"
        
        print(f"  ✓ Rechazado correctamente")
        print(f"  ✓ Errores: {resultado['errores']}")
    
    print()


def test_procesar_archivo_completo_error_tamaño():
    """Test: Procesamiento rechaza archivos muy grandes"""
    print("❌ Test: Procesamiento rechaza archivo >10MB")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        archivo = FakeFile('documento.pdf', size_mb=15)
        
        resultado = procesar_archivo_completo(
            archivo,
            'certificado',
            999,
            temp_dir
        )
        
        assert not resultado['exito'], "Procesamiento debería fallar"
        assert len(resultado['errores']) > 0, "Debe incluir errores"
        
        print(f"  ✓ Rechazado correctamente")
        print(f"  ✓ Errores: {resultado['errores']}")
    
    print()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("TESTS DE GESTIÓN DE UPLOADS: FORMATO, TAMAÑO, NAMING Y METADATOS")
    print("="*70 + "\n")
    
    try:
        test_validar_archivo_valido()
        test_validar_archivo_extension_invalida()
        test_validar_archivo_tamaño_excedido()
        test_generar_nombre_unico()
        test_calcular_checksum()
        test_obtener_mime_type()
        test_procesar_archivo_completo_exitoso()
        test_procesar_archivo_completo_error_extension()
        test_procesar_archivo_completo_error_tamaño()
        
        print("="*70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*70)
        
    except AssertionError as e:
        print("\n" + "="*70)
        print(f"❌ TEST FALLÓ: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ ERROR INESPERADO: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
