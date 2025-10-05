# Manual de Usuario
## Sistema de Gestion de Incapacidades - MVP

### 1. Introduccion
Este sistema permite gestionar incapacidades medicas de forma digital,
desde el registro hasta la aprobacion.

### 2. Acceso al Sistema
- URL: http://localhost:5000
- Usuarios de prueba disponibles en pantalla de login

### 3. Para Colaboradores

#### 3.1 Registrar Incapacidad
1. Iniciar sesion
2. Click en "Registrar Incapacidad"
3. Completar formulario:
   - Seleccionar tipo
   - Ingresar fechas
   - Subir certificado (obligatorio)
   - Subir epicrisis (si aplica)
4. Click en "Registrar Incapacidad"

#### 3.2 Consultar Incapacidades
1. Click en "Mis Incapacidades"
2. Ver lista completa con estados
3. Click en "Ver Detalle" para mas informacion
4. Descargar documentos si es necesario

#### 3.3 Estados Posibles
- **Pendiente**: Esperando validacion
- **En revision**: Documentacion siendo revisada
- **Aprobada**: Incapacidad aprobada
- **Rechazada**: No cumple requisitos (ver motivo)

### 4. Para Auxiliares de Gestion Humana

#### 4.1 Dashboard
- Ver todas las incapacidades pendientes
- Ver incapacidades en revision
- Estadisticas generales

#### 4.2 Validar Documentacion
1. Click en "Validar" en incapacidad pendiente
2. Revisar validacion automatica
3. Descargar y revisar documentos
4. Completar checklist manual
5. Marcar como "Documentacion Completa"

#### 4.3 Aprobar o Rechazar
1. Acceder a incapacidad en revision
2. Seleccionar decision:
   - **Aprobar**: Si todo esta correcto
   - **Rechazar**: Especificar motivo detallado
3. Confirmar decision

### 5. Documentos Requeridos

#### Enfermedad General (≤2 dias)
- Certificado de incapacidad (obligatorio)

#### Enfermedad General (>2 dias)
- Certificado de incapacidad (obligatorio)
- Epicrisis (obligatorio)

#### Accidente Laboral
- Certificado de incapacidad (obligatorio)
- Epicrisis (obligatorio)

### 6. Formatos Aceptados
- PDF, JPG, JPEG, PNG
- Tamano maximo: 10MB por archivo

### 7. Soporte
Para problemas tecnicos, contactar al administrador del sistema.