# Sistema de Gestion de Incapacidades - MVP

Sistema web para gestionar el ciclo completo de incapacidades medicas,
desde el registro hasta la aprobacion.

## Caracteristicas

- ✅ Registro digital de incapacidades
- ✅ Carga de documentos (certificado, epicrisis)
- ✅ Validacion automatica de requisitos
- ✅ Workflow de aprobacion
- ✅ Consulta de historial
- ✅ Dashboard para auxiliares
- ✅ Sistema de roles (colaborador/auxiliar)

## Tecnologias

- **Backend**: Python 3.8+ con Flask
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Base de Datos**: SQLite
- **Autenticacion**: Flask-Login

## Instalacion

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. Clonar o descargar el proyecto
2. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecutar aplicacion:
   ```bash
   python run.py
   ```
5. Abrir navegador en: http://localhost:5000

## Usuarios de Prueba

- **Colaborador**: colaborador@test.com / 123456
- **Auxiliar**: auxiliar@test.com / 123456

## Estructura del Proyecto

```
sistema-incapacidades/
├── app/
│   ├── models/          # Modelos de BD
│   ├── routes/          # Rutas/Controladores
│   ├── templates/       # Vistas HTML
│   └── static/          # CSS, JS, uploads
├── docs/                # Documentacion
├── tests/               # Pruebas
├── config.py            # Configuracion
├── run.py               # Punto de entrada
└── requirements.txt     # Dependencias
```

## Casos de Uso Implementados

1. **UC1**: Registrar incapacidad
2. **UC2**: Cargar documentos
3. **UC3**: Consultar mis incapacidades
4. **UC4**: Ver detalle de incapacidad
5. **UC5**: Ver incapacidades pendientes (auxiliar)
6. **UC6**: Validar documentacion
7. **UC7**: Aprobar o rechazar incapacidad
8. **UC8**: Descargar documentos
9. **UC9**: Almacenar documentos
10. **UC10**: Validacion automatica de requisitos

## Limitaciones del MVP

- No incluye notificaciones por correo
- No incluye integracion con portales EPS/ARL
- No incluye reportes avanzados
- No incluye conciliacion de pagos
- Autenticacion basica (sin OAuth)

## Trabajo Futuro

- Implementar sistema de notificaciones
- Agregar generacion de reportes PDF/Excel
- Integracion con APIs de EPS/ARL
- Dashboard con graficos y analiticas
- Modulo de conciliacion financiera
- Sistema de roles mas granular

## Autores

Juan Esteban Agudelo Escobar
Juan Alejandro Salgado Arcila

## Licencia

Proyecto academico - Universidad Tecnologica de Pereira