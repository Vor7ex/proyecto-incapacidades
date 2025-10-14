"""
Tests para funcionalidad de código de radicación de incapacidades
Cubre: generación, unicidad, formato, y transacciones atómicas
"""
import unittest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.incapacidad import (
    Incapacidad, 
    generar_codigo_radicacion, 
    verificar_codigo_unico,
    generar_codigo_radicacion_unico
)
from app.models.usuario import Usuario
import re

class TestCodigoRadicacion(unittest.TestCase):
    """Tests para código de radicación de incapacidades"""
    
    def setUp(self):
        """Configurar entorno de pruebas"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Crear usuario de prueba
        self.usuario = Usuario(
            nombre='Test User',
            email='test@example.com',
            rol='colaborador'
        )
        self.usuario.set_password('password123')
        db.session.add(self.usuario)
        db.session.commit()
    
    def tearDown(self):
        """Limpiar después de cada test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    # ========================================
    # TEST 1: Formato del código
    # ========================================
    def test_formato_codigo_radicacion(self):
        """Test: El código debe tener formato INC-YYYYMMDD-XXXX"""
        codigo = generar_codigo_radicacion()
        
        # Verificar formato con regex
        patron = r'^INC-\d{8}-[A-F0-9]{4}$'
        self.assertRegex(
            codigo, 
            patron, 
            f"El código {codigo} no cumple formato INC-YYYYMMDD-XXXX"
        )
        
        # Verificar partes
        partes = codigo.split('-')
        self.assertEqual(len(partes), 3, "Código debe tener 3 partes separadas por -")
        self.assertEqual(partes[0], "INC", "Prefijo debe ser INC")
        self.assertEqual(len(partes[1]), 8, "Fecha debe tener 8 dígitos")
        self.assertEqual(len(partes[2]), 4, "UUID corto debe tener 4 caracteres")
        
        # Verificar que la fecha es válida
        fecha_str = partes[1]
        try:
            fecha = datetime.strptime(fecha_str, '%Y%m%d')
            self.assertIsNotNone(fecha)
        except ValueError:
            self.fail(f"Fecha {fecha_str} no es válida")
    
    # ========================================
    # TEST 2: Unicidad del código
    # ========================================
    def test_unicidad_codigo_radicacion(self):
        """Test: Códigos generados múltiples veces deben ser únicos"""
        codigos = set()
        
        # Generar 100 códigos
        for _ in range(100):
            codigo = generar_codigo_radicacion()
            codigos.add(codigo)
        
        # Todos deben ser únicos (aunque UUID corto puede colisionar, es muy raro)
        self.assertEqual(
            len(codigos), 
            100, 
            f"Se generaron {len(codigos)} códigos únicos de 100 intentos"
        )
    
    # ========================================
    # TEST 3: Verificación de código único en BD
    # ========================================
    def test_verificar_codigo_unico_bd(self):
        """Test: verificar_codigo_unico debe detectar códigos duplicados"""
        # Código nuevo (no existe en BD)
        codigo_nuevo = "INC-20251013-TEST"
        self.assertTrue(
            verificar_codigo_unico(codigo_nuevo),
            "Código nuevo debe ser único"
        )
        
        # Crear incapacidad con código
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=3)).date(),
            dias=3,
            estado='Pendiente',
            codigo_radicacion=codigo_nuevo
        )
        db.session.add(incapacidad)
        db.session.commit()
        
        # Ahora el código existe, no debe ser único
        self.assertFalse(
            verificar_codigo_unico(codigo_nuevo),
            "Código existente NO debe ser único"
        )
    
    # ========================================
    # TEST 4: Generación de código único con reintentos
    # ========================================
    def test_generar_codigo_radicacion_unico(self):
        """Test: generar_codigo_radicacion_unico debe crear códigos sin duplicados"""
        codigos = []
        
        # Generar 10 códigos únicos
        for _ in range(10):
            codigo = generar_codigo_radicacion_unico()
            codigos.append(codigo)
            
            # Crear incapacidad para simular uso del código
            inc = Incapacidad(
                usuario_id=self.usuario.id,
                tipo='Enfermedad General',
                fecha_inicio=datetime.now().date(),
                fecha_fin=(datetime.now() + timedelta(days=1)).date(),
                dias=1,
                estado='Pendiente',
                codigo_radicacion=codigo
            )
            db.session.add(inc)
            db.session.commit()
        
        # Verificar que todos son únicos
        self.assertEqual(
            len(codigos), 
            len(set(codigos)),
            "Todos los códigos deben ser únicos"
        )
    
    # ========================================
    # TEST 5: Asignación automática de código
    # ========================================
    def test_asignar_codigo_radicacion_metodo(self):
        """Test: asignar_codigo_radicacion() debe asignar código si no existe"""
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Accidente Laboral',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=5)).date(),
            dias=5,
            estado='Pendiente'
        )
        
        # No tiene código aún
        self.assertIsNone(incapacidad.codigo_radicacion)
        
        # Asignar código
        incapacidad.asignar_codigo_radicacion()
        
        # Ahora debe tener código
        self.assertIsNotNone(incapacidad.codigo_radicacion)
        
        # Verificar formato
        patron = r'^INC-\d{8}-[A-F0-9]{4}$'
        self.assertRegex(incapacidad.codigo_radicacion, patron)
    
    # ========================================
    # TEST 6: No sobrescribir código existente
    # ========================================
    def test_no_sobrescribir_codigo_existente(self):
        """Test: asignar_codigo_radicacion() no debe cambiar código existente"""
        codigo_original = "INC-20251013-ORIG"
        
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=2)).date(),
            dias=2,
            estado='Pendiente',
            codigo_radicacion=codigo_original
        )
        
        # Intentar reasignar código
        incapacidad.asignar_codigo_radicacion()
        
        # Debe conservar el código original
        self.assertEqual(
            incapacidad.codigo_radicacion, 
            codigo_original,
            "No debe sobrescribir código existente"
        )
    
    # ========================================
    # TEST 7: Índice único en base de datos
    # ========================================
    def test_indice_unico_bd(self):
        """Test: BD debe rechazar códigos duplicados (constraint UNIQUE)"""
        from sqlalchemy.exc import IntegrityError
        
        codigo = "INC-20251013-DUP1"
        
        # Primera incapacidad con código
        inc1 = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=1)).date(),
            dias=1,
            estado='Pendiente',
            codigo_radicacion=codigo
        )
        db.session.add(inc1)
        db.session.commit()
        
        # Segunda incapacidad con MISMO código (debe fallar)
        inc2 = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Accidente Laboral',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=2)).date(),
            dias=2,
            estado='Pendiente',
            codigo_radicacion=codigo  # DUPLICADO
        )
        db.session.add(inc2)
        
        # Debe lanzar IntegrityError por violación de UNIQUE
        with self.assertRaises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()
    
    # ========================================
    # TEST 8: __repr__ con código de radicación
    # ========================================
    def test_repr_con_codigo(self):
        """Test: __repr__ debe mostrar código de radicación si existe"""
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Licencia Maternidad',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=90)).date(),
            dias=90,
            estado='Pendiente'
        )
        incapacidad.asignar_codigo_radicacion()
        
        repr_str = repr(incapacidad)
        
        # Debe contener el código
        self.assertIn('INC-', repr_str)
        self.assertIn(incapacidad.codigo_radicacion, repr_str)
        self.assertIn(incapacidad.tipo, repr_str)
    
    # ========================================
    # TEST 9: Transacción atómica (simulación)
    # ========================================
    def test_transaccion_atomica_rollback(self):
        """Test: Rollback debe revertir asignación de código"""
        incapacidad = Incapacidad(
            usuario_id=self.usuario.id,
            tipo='Enfermedad General',
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=3)).date(),
            dias=3,
            estado='Pendiente'
        )
        incapacidad.asignar_codigo_radicacion()
        codigo = incapacidad.codigo_radicacion
        
        db.session.add(incapacidad)
        
        # Simular error antes de commit
        db.session.rollback()
        
        # El código NO debe estar en BD
        incapacidades = Incapacidad.query.filter_by(codigo_radicacion=codigo).all()
        self.assertEqual(
            len(incapacidades), 
            0,
            "Rollback debe revertir inserción"
        )
        
        # El código debe estar disponible para reutilización
        self.assertTrue(
            verificar_codigo_unico(codigo),
            "Código debe estar disponible después de rollback"
        )

if __name__ == '__main__':
    unittest.main()
