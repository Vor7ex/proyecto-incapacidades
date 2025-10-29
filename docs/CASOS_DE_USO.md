## Módulo de Registro

### UC1 - Registrar incapacidad con documentos

| **Campo**                  | **Descripción**                                                                                                                                                                                                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Nombre del Caso de Uso** | Registrar incapacidad con documentos                                                                                                                                                                                                                                                             |
| **Identificación**         | UC1                                                                                                                                                                                                                                                                                              |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                                                                                                       |
| **Fecha Modificación**     | -                                                                                                                                                                                                                                                                                                |
| **Referencia**             | CAR-01, ON-01, ON-03                                                                                                                                                                                                                                                                             |
| **Tipo implementación**    | Release 1.0                                                                                                                                                                                                                                                                                      |
| **Actores**                | Colaborador                                                                                                                                                                                                                                                                                      |
| **Propósito**              | Permitir al colaborador registrar una incapacidad médica o licencia en el sistema, adjuntando la documentación requerida según el tipo.                                                                                                                                                          |
| **Resumen**                | El colaborador accede al sistema, selecciona el tipo de incapacidad, completa el formulario con los datos requeridos y carga los documentos digitales correspondientes. El sistema valida y almacena la información, notificando automáticamente al líder inmediato y al área de Gestión Humana. |
| **Precondición**           | - El colaborador debe estar autenticado en el sistema<br>- El colaborador debe tener rol activo en la organización<br>- Debe contar con los documentos digitalizados                                                                                                                             |

---

### Flujo Normal de los Eventos

| **#** | **Acción de los Actores**                                                                                                                        | **Respuesta del Sistema**                                                                       |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| 1     | El colaborador accede al módulo de registro de incapacidades                                                                                     | Muestra el formulario de registro                                                               |
| 2     | Selecciona el tipo de incapacidad (Enfermedad general, Accidente laboral, Accidente de tránsito, Licencia de maternidad, Licencia de paternidad) | Ajusta los campos del formulario según el tipo seleccionado y muestra los documentos requeridos |
| 3     | Completa los datos: fecha de inicio, fecha de fin, número de días, diagnóstico (si aplica)                                                       | Valida el formato de los datos ingresados                                                       |
| 4     | Carga el certificado de incapacidad original (PDF o imagen)                                                                                      | Valida el formato y tamaño del archivo. Muestra vista previa                                    |
| 5     | Carga documentos adicionales según tipo (Epicrisis, FURIPS, certificados, etc.)                                                                  | Valida cada documento y marca como completado                                                   |
| 6     | Confirma el envío del formulario                                                                                                                 | Verifica que todos los documentos obligatorios estén cargados                                   |
| 7     |                                                                                                                                                  | Almacena la incapacidad con estado "Pendiente de validación"                                    |
| 8     |                                                                                                                                                  | Genera código de radicación único                                                               |
| 9     |                                                                                                                                                  | Ejecuta UC2 - Notifica automáticamente al líder y Gestión Humana                                |
| 10    |                                                                                                                                                  | Ejecuta UC15 - Almacena documentos en repositorio digital                                       |
| 11    |                                                                                                                                                  | Muestra mensaje de confirmación con código de radicación                                        |
| 12    | Recibe notificación de registro exitoso                                                                                                          | Envía correo electrónico de confirmación al colaborador                                         |

---

### Postcondición

* La incapacidad queda registrada en el sistema con estado "Pendiente de validación"
* Los documentos están almacenados digitalmente
* Se ha notificado al líder inmediato y Gestión Humana
* Se genera código de radicación único

---

### Flujos Alternos de los Eventos (Excepciones)

| **#**  | **Descripción**                                                                                                                                                                                    |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Documentos incompletos:** Si el colaborador intenta enviar sin todos los documentos obligatorios, el sistema muestra mensaje de error indicando los documentos faltantes y no permite continuar. |
| **E2** | **Formato de archivo inválido:** Si el documento no está en formato PDF o imagen válida, el sistema rechaza el archivo y solicita formato correcto.                                                |
| **E3** | **Archivo demasiado grande:** Si el archivo supera 10MB, el sistema muestra mensaje de error y solicita comprimir el archivo.                                                                      |
| **E4** | **Fechas inválidas:** Si la fecha de inicio es posterior a la fecha de fin, o si las fechas son futuras sin justificación, el sistema muestra error y solicita corrección.                         |
| **E5** | **Sesión expirada:** Si la sesión expira durante el registro, el sistema guarda borrador automáticamente y solicita reautenticación.                                                               |
| **E6** | **Error de conexión:** Si hay pérdida de conexión, el sistema guarda borrador local y permite retomar cuando se restablezca.                                                                       |

---

### Frecuencia, Importancia y Urgencia

| **Campo**               | **Descripción**              |
| ----------------------- | ---------------------------- |
| **Frecuencia esperada** | 50-100 incapacidades por mes |
| **Importancia**         | Alta                         |
| **Urgencia**            | Alta                         |

---

### UC2 - Notificar a líder y Gestión Humana

| **Campo**                  | **Descripción**                                                                                                                                                                                                 |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Notificar a líder y Gestión Humana                                                                                                                                                                              |
| **Identificación**         | UC2                                                                                                                                                                                                             |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                      |
| **Referencia**             | CAR-03, ON-01                                                                                                                                                                                                   |
| **Tipo implementación**    | Release 1.0                                                                                                                                                                                                     |
| **Actores**                | Sistema (automático)                                                                                                                                                                                            |
| **Propósito**              | Notificar de manera automática e inmediata al líder inmediato y al área de Gestión Humana sobre el registro de una nueva incapacidad.                                                                           |
| **Resumen**                | Cuando se registra una incapacidad en el sistema, este envía automáticamente notificaciones por correo electrónico y notificación interna al líder del colaborador y al auxiliar de Gestión Humana responsable. |
| **Precondición**           | - Una incapacidad debe haber sido registrada exitosamente (UC1)<br>- El colaborador debe tener líder asignado en el sistema<br>- Deben existir usuarios de Gestión Humana activos                               |

---

### Flujo Normal de los Eventos

| **#** | **Acción de los Actores**                     | **Respuesta del Sistema**                                                                                             |
| ----- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 1     | Se completa el registro de incapacidad (UC1)  | Identifica al líder inmediato del colaborador                                                                         |
| 2     |                                               | Identifica a los auxiliares de Gestión Humana activos                                                                 |
| 3     |                                               | Genera contenido de notificación con: nombre del colaborador, tipo de incapacidad, fechas, días, código de radicación |
| 4     |                                               | Envía correo electrónico al líder inmediato                                                                           |
| 5     |                                               | Envía correo electrónico a Gestión Humana                                                                             |
| 6     |                                               | Crea notificación interna en el sistema para el líder                                                                 |
| 7     |                                               | Crea notificación interna para Gestión Humana                                                                         |
| 8     |                                               | Registra log de notificaciones enviadas                                                                               |
| 9     | Líder y Gestión Humana reciben notificaciones | Marca notificaciones como entregadas                                                                                  |

---

### Postcondición

* El líder inmediato ha sido notificado
* Gestión Humana ha sido notificada
* Quedan registros de notificaciones enviadas

---

### Flujos Alternos de los Eventos (Excepciones)

| **#**  | **Descripción**                                                                                                                                                                    |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Líder no asignado:** Si el colaborador no tiene líder asignado, el sistema notifica solo a Gestión Humana y registra alerta.                                                     |
| **E2** | **Correo electrónico inválido:** Si el correo del líder o Gestión Humana es inválido, el sistema envía solo notificación interna y registra error.                                 |
| **E3** | **Error en servidor de correo:** Si el servidor SMTP falla, el sistema reintenta 3 veces con intervalos de 5 minutos. Si persiste, registra error y mantiene notificación interna. |
| **E4** | **Sin usuarios de Gestión Humana:** Si no hay usuarios activos de Gestión Humana, el sistema notifica al administrador del sistema.                                                |

---

### Frecuencia, Importancia y Urgencia

| **Campo**               | **Descripción**                    |
| ----------------------- | ---------------------------------- |
| **Frecuencia esperada** | 50-100 veces por mes (igual a UC1) |
| **Importancia**         | Alta                               |
| **Urgencia**            | Alta                               |

---

### UC3 - Consultar mis incapacidades

| **Campo**                  | **Descripción**                                                                                                                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Consultar mis incapacidades                                                                                                                                                         |
| **Identificación**         | UC3                                                                                                                                                                                 |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                          |
| **Referencia**             | ON-01                                                                                                                                                                               |
| **Tipo implementación**    | Release 1.0                                                                                                                                                                         |
| **Actores**                | Colaborador                                                                                                                                                                         |
| **Propósito**              | Permitir al colaborador consultar el historial y estado de sus incapacidades registradas en el sistema.                                                                             |
| **Resumen**                | El colaborador accede al módulo de consulta donde puede ver todas sus incapacidades, filtrar por fecha o estado, y consultar el detalle de cada una incluyendo documentos adjuntos. |
| **Precondición**           | - El colaborador debe estar autenticado en el sistema<br>- Debe tener al menos una incapacidad registrada                                                                           |

---

### Flujo Normal de los Eventos

| **#** | **Acción de los Actores**                               | **Respuesta del Sistema**                                                                   |
| ----- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 1     | Accede al módulo "Mis Incapacidades"                    | Muestra listado de incapacidades del colaborador ordenadas por fecha (más reciente primero) |
| 2     | Visualiza tabla con: código, tipo, fechas, días, estado | Presenta información en formato tabla paginada                                              |
| 3     | (Opcional) Aplica filtros por: fecha, tipo, estado      | Actualiza el listado según filtros aplicados                                                |
| 4     | Selecciona una incapacidad para ver detalle             | Muestra vista detallada con toda la información y línea de tiempo de estados                |
| 5     | (Opcional) Descarga documentos adjuntos                 | Permite descargar cada documento individual o todos en ZIP                                  |
| 6     | (Opcional) Solicita información adicional sobre rechazo | Muestra detalles del rechazo si el estado es "Rechazada"                                    |

---

### Postcondición

* El colaborador ha consultado su información
* No se modifica ningún dato en el sistema

---

### Flujos Alternos de los Eventos (Excepciones)

| **#**  | **Descripción**                                                                                                                                                |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Sin incapacidades registradas:** Si el colaborador no tiene incapacidades, el sistema muestra mensaje informativo y botón para registrar nueva.              |
| **E2** | **Error al descargar documento:** Si hay error en la descarga, el sistema muestra mensaje de error y sugiere reintentar o contactar soporte.                   |
| **E3** | **Filtros sin resultados:** Si los filtros aplicados no retornan resultados, el sistema muestra mensaje "No se encontraron incapacidades con estos criterios". |

---

### Frecuencia, Importancia y Urgencia

| **Campo**               | **Descripción**           |
| ----------------------- | ------------------------- |
| **Frecuencia esperada** | 200-300 consultas por mes |
| **Importancia**         | Media                     |
| **Urgencia**            | Media                     |

## Módulo de Validación

---

### UC4 - Recibir y validar documentación

| **Campo**                  | **Descripción**                                                                                                                                                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Nombre del Caso de Uso** | Recibir y validar documentación                                                                                                                                                                                                                  |
| **Identificación**         | UC4                                                                                                                                                                                                                                              |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                                                       |
| **Referencia**             | CAR-02, ON-01, ON-05                                                                                                                                                                                                                             |
| **Tipo implementación**    | Release 1.0                                                                                                                                                                                                                                      |
| **Actores**                | Auxiliar de Gestión Humana                                                                                                                                                                                                                       |
| **Propósito**              | Permitir al auxiliar de Gestión Humana recibir y validar que las incapacidades registradas cumplan con todos los requisitos documentales según el tipo.                                                                                          |
| **Resumen**                | El auxiliar accede a las incapacidades pendientes de validación, revisa los documentos adjuntos, verifica que cumplan los requisitos automáticos y manuales, y determina si la documentación está completa o si requiere documentos adicionales. |
| **Precondición**           | - El auxiliar debe estar autenticado con rol de Gestión Humana<br>- Debe existir al menos una incapacidad con estado "Pendiente de validación"                                                                                                   |

---

### Flujo Normal de los Eventos

| **#** | **Acción de los Actores**                                               | **Respuesta del Sistema**                                                                                   |
| ----- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| 1     | Accede al módulo de validación de incapacidades                         | Muestra listado de incapacidades pendientes de validación ordenadas por fecha de registro                   |
| 2     | Selecciona una incapacidad para validar                                 | Muestra detalle completo: datos del colaborador, tipo, fechas, documentos adjuntos, checklist de requisitos |
| 3     |                                                                         | Ejecuta UC5 - Verifica automáticamente requisitos por tipo                                                  |
| 4     | Visualiza checklist automático de documentos                            | Muestra resultados de validación automática (documentos presentes/faltantes)                                |
| 5     | Revisa cada documento adjunto (calidad, legibilidad, coherencia)        | Permite visualizar cada documento en pantalla                                                               |
| 6     | Verifica información manual: coherencia entre fechas, diagnóstico, días | Marca items del checklist como verificados                                                                  |
| 7     | Marca la validación como completa y aprobada                            | Actualiza estado a "Documentación Completa" y ejecuta UC7                                                   |
| 8     |                                                                         | Registra fecha y usuario que validó                                                                         |
| 9     |                                                                         | Notifica al colaborador que su incapacidad está en proceso                                                  |

---

### Postcondición

* La incapacidad cambia de estado a "Documentación Completa"
* Queda registro de validación con fecha y usuario
* El colaborador recibe notificación
* La incapacidad queda lista para transcripción

---

### Flujos Alternos de los Eventos (Excepciones)

| **#**  | **Descripción**                                                                                                                                                                                                         |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Documentación incompleta:** Si faltan documentos o la validación automática detecta faltantes, el auxiliar ejecuta UC6 - Solicitar documentos faltantes. El sistema no permite aprobar hasta completar documentación. |
| **E2** | **Documentos ilegibles:** Si un documento no se puede leer, el auxiliar marca como "ilegible" y ejecuta UC6 especificando el problema.                                                                                  |
| **E3** | **Información incoherente:** Si hay incoherencia entre fechas, días o diagnóstico, el auxiliar marca observaciones y ejecuta UC6 para aclaración.                                                                       |
| **E4** | **Documento incorrecto:** Si se adjuntó documento que no corresponde, el auxiliar registra observación y ejecuta UC6.                                                                                                   |
| **E5** | **Certificado no original:** Si el certificado de incapacidad no es original, el auxiliar rechaza y ejecuta UC6 solicitando original.                                                                                   |

---

### Frecuencia, Importancia y Urgencia

| **Campo**               | **Descripción**             |
| ----------------------- | --------------------------- |
| **Frecuencia esperada** | 50-100 validaciones por mes |
| **Importancia**         | Alta                        |
| **Urgencia**            | Alta                        |

---

### UC5 - Verificar requisitos por tipo

| **Campo**                  | **Descripción**                                                                                                                                                                                                                                     |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Verificar requisitos por tipo                                                                                                                                                                                                                       |
| **Identificación**         | UC5                                                                                                                                                                                                                                                 |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                                                          |
| **Referencia**             | CAR-02, ON-05                                                                                                                                                                                                                                       |
| **Tipo implementación**    | Release 1.0                                                                                                                                                                                                                                         |
| **Actores**                | Sistema (automático)                                                                                                                                                                                                                                |
| **Propósito**              | Validar automáticamente que se hayan adjuntado todos los documentos requeridos según el tipo de incapacidad.                                                                                                                                        |
| **Resumen**                | El sistema verifica automáticamente la presencia de documentos obligatorios según reglas predefinidas para cada tipo de incapacidad (enfermedad general, accidente laboral, accidente de tránsito, licencia de maternidad, licencia de paternidad). |
| **Precondición**           | - Existe una incapacidad registrada con tipo definido.<br>- Se han cargado documentos al sistema.                                                                                                                                                   |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores** | **Respuesta del Sistema**                                                                                                                                     |
| ----- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Se invoca desde UC1 o UC4 | Identifica el tipo de incapacidad                                                                                                                             |
| 2     |                           | Carga reglas de validación para ese tipo específico                                                                                                           |
| 3     |                           | Verifica presencia de certificado de incapacidad (obligatorio para todos)                                                                                     |
| 4     |                           | Si tipo = Enfermedad general y días > 2: verifica presencia de Epicrisis                                                                                      |
| 5     |                           | Si tipo = Accidente de tránsito: verifica Epicrisis y FURIPS                                                                                                  |
| 6     |                           | Si tipo = Accidente laboral: verifica Epicrisis                                                                                                               |
| 7     |                           | Si tipo = Licencia de maternidad: verifica Epicrisis, certificado de nacido vivo, registro civil, documento de identidad                                      |
| 8     |                           | Si tipo = Licencia de paternidad: verifica Epicrisis con semanas de gestación, certificado de nacido vivo, registro civil, documento de identidad de la madre |
| 9     |                           | Genera checklist con resultado: documentos presentes (✓) y faltantes (✗)                                                                                      |
| 10    |                           | Retorna resultado al proceso que lo invocó                                                                                                                    |

---

| **Postcondición** |                                                                                                                         |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------- |
|                   | - Se ha generado checklist de validación automática.<br>- Se identifica si la documentación está completa o incompleta. |

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Tipo de incapacidad no definido:** Si el tipo no está especificado, el sistema marca error y solicita definir tipo antes de validar.         |
| **E2** | **Reglas no configuradas:** Si no existen reglas para un tipo específico, el sistema notifica al administrador y solo valida certificado base. |

---

| **Campo**               | **Descripción**      |
| ----------------------- | -------------------- |
| **Frecuencia esperada** | 50-100 veces por mes |
| **Importancia**         | Alta                 |
| **Urgencia**            | Alta                 |

---

### UC6 - Solicitar documentos faltantes

| **Campo**                  | **Descripción**                                                                                                                                                                                                      |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Solicitar documentos faltantes                                                                                                                                                                                       |
| **Identificación**         | UC6                                                                                                                                                                                                                  |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                           |
| **Referencia**             | ON-01, ON-05                                                                                                                                                                                                         |
| **Tipo implementación**    | Release 1.0                                                                                                                                                                                                          |
| **Actores**                | Auxiliar de Gestión Humana, Colaborador                                                                                                                                                                              |
| **Propósito**              | Notificar al colaborador sobre documentos faltantes o con problemas y establecer plazo de 3 días hábiles para su entrega.                                                                                            |
| **Resumen**                | Cuando la validación detecta documentos faltantes o con problemas, el auxiliar registra las observaciones específicas y el sistema notifica al colaborador otorgando 3 días hábiles para completar la documentación. |
| **Precondición**           | - Existe una incapacidad en validación con documentación incompleta.<br>- El auxiliar ha identificado documentos específicos faltantes o con problemas.                                                              |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                                       | **Respuesta del Sistema**                                                                             |
| ----- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| 1     | El auxiliar identifica documentos faltantes durante UC4                                         | Muestra formulario para registrar solicitud                                                           |
| 2     | Selecciona documentos faltantes del checklist                                                   | Marca documentos seleccionados                                                                        |
| 3     | Agrega observaciones específicas para cada documento (ej: "Epicrisis ilegible", "Falta FURIPS") | Registra observaciones                                                                                |
| 4     | Confirma solicitud de documentos                                                                | Cambia estado de incapacidad a "Documentación incompleta"                                             |
| 5     |                                                                                                 | Calcula fecha límite (3 días hábiles desde hoy)                                                       |
| 6     |                                                                                                 | Envía notificación por correo y sistema al colaborador detallando documentos faltantes y fecha límite |
| 7     |                                                                                                 | Programa recordatorio automático para día 2 si no hay respuesta                                       |
| 8     |                                                                                                 | Registra log de solicitud con fecha, usuario y observaciones                                          |
| 9     | Colaborador recibe notificación y carga documentos solicitados                                  | Valida formato y almacena nuevos documentos                                                           |
| 10    |                                                                                                 | Cambia estado a "Pendiente de validación" nuevamente                                                  |
| 11    |                                                                                                 | Notifica al auxiliar que se completó documentación                                                    |

---

| **Postcondición** |                                                                                                                                                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|                   | - El colaborador ha sido notificado de documentos faltantes.<br>- Se establece plazo de 3 días hábiles.<br>- Estado cambia a "Documentación incompleta".<br>- Al completar documentación, regresa a "Pendiente de validación". |

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **E1** | **Colaborador no responde en 3 días:** Al cumplirse el plazo sin respuesta, el sistema envía segunda notificación advirtiendo que será citado con coordinación si no responde. |
| **E2** | **Documentos enviados siguen incompletos:** Si el colaborador envía documentos pero aún faltan algunos, el auxiliar puede reiniciar UC6 con nuevo plazo de 3 días.             |
| **E3** | **Segunda notificación sin respuesta:** Si tras 3 días adicionales no hay respuesta, el sistema marca incapacidad como "Requiere citación" y notifica a coordinación.          |
| **E4** | **Colaborador solicita extensión de plazo:** El auxiliar puede extender manualmente el plazo por razones justificadas, registrando motivo.                                     |

---

| **Campo**               | **Descripción**                            |
| ----------------------- | ------------------------------------------ |
| **Frecuencia esperada** | 15-25 veces por mes (30% de incapacidades) |
| **Importancia**         | Alta                                       |
| **Urgencia**            | Alta                                       |

---

### UC7 - Aprobar/Rechazar incapacidad

| **Campo**                  | **Descripción**                                                                                                                                                                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Aprobar/Rechazar incapacidad                                                                                                                                                                                                              |
| **Identificación**         | UC7                                                                                                                                                                                                                                       |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                                                |
| **Referencia**             | ON-01, ON-05                                                                                                                                                                                                                              |
| **Tipo implementación**    | Release 1.0                                                                                                                                                                                                                               |
| **Actores**                | Auxiliar de Gestión Humana                                                                                                                                                                                                                |
| **Propósito**              | Permitir al auxiliar aprobar una incapacidad validada correctamente o rechazarla definitivamente si no cumple requisitos fundamentales.                                                                                                   |
| **Resumen**                | Después de la validación documental, el auxiliar determina si la incapacidad cumple todos los requisitos para ser procesada. Si es aprobada, avanza a transcripción; si es rechazada, se registra el motivo y se notifica al colaborador. |
| **Precondición**           | - La incapacidad ha sido validada (UC4 completado).<br>- Toda la documentación ha sido revisada.                                                                                                                                          |

---

### **Flujo Normal de los Eventos - Aprobar**

| **#** | **Acción de los Actores**                                 | **Respuesta del Sistema**                                                      |
| ----- | --------------------------------------------------------- | ------------------------------------------------------------------------------ |
| 1     | El auxiliar completa validación satisfactoriamente en UC4 | Muestra opción de aprobar incapacidad                                          |
| 2     | Selecciona "Aprobar incapacidad"                          | Solicita confirmación                                                          |
| 3     | Confirma aprobación                                       | Ejecuta UC8 - Actualiza estado a "Aprobada - Pendiente transcripción"          |
| 4     |                                                           | Registra fecha de aprobación y usuario                                         |
| 5     |                                                           | Notifica al colaborador sobre aprobación                                       |
| 6     |                                                           | Coloca incapacidad en cola para transcripción                                  |
| 7     |                                                           | Genera alerta si el plazo de transcripción está próximo a vencer según entidad |

---

### **Flujo Alterno - Rechazar**

| **#** | **Acción de los Actores**                                        | **Respuesta del Sistema**                                              |
| ----- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 1     | El auxiliar identifica que la incapacidad no puede ser procesada | Muestra opción de rechazar incapacidad                                 |
| 2     | Selecciona "Rechazar incapacidad"                                | Muestra formulario de rechazo                                          |
| 3     | Selecciona motivo de rechazo de lista predefinida                | Registra motivo seleccionado                                           |
| 4     | Agrega observaciones adicionales                                 | Registra observaciones                                                 |
| 5     | Confirma rechazo                                                 | Ejecuta UC8 - Actualiza estado a "Rechazada"                           |
| 6     |                                                                  | Registra fecha de rechazo, motivo y usuario                            |
| 7     |                                                                  | Envía notificación detallada al colaborador con motivo y observaciones |
| 8     |                                                                  | Marca incapacidad como finalizada (no procesable)                      |

---

| **Postcondición** |                                                                                                                                                                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|                   | - **Si aprobada:** Estado cambia a "Aprobada - Pendiente transcripción", lista para procesar.<br>- **Si rechazada:** Estado cambia a "Rechazada", queda registro de motivo, no se procesa.<br>- En ambos casos: colaborador es notificado. |

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                          |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **E1** | **Rechazo por certificado falso:** Si se detecta falsificación, el auxiliar marca motivo específico y el sistema notifica adicionalmente a coordinación y área jurídica. |
| **E2** | **Rechazo por extemporaneidad:** Si la incapacidad se presenta fuera del plazo establecido por la EPS, se rechaza registrando este motivo específico.                    |
| **E3** | **Aprobación con observaciones:** El auxiliar puede aprobar pero registrar observaciones especiales que deben considerarse en transcripción.                             |

---

| **Campo**               | **Descripción**                                         |
| ----------------------- | ------------------------------------------------------- |
| **Frecuencia esperada** | 50-100 veces por mes (aprobaciones: 90%, rechazos: 10%) |
| **Importancia**         | Alta                                                    |
| **Urgencia**            | Alta                                                    |

## Módulo de Seguimiento

### UC8 - Actualizar estado de incapacidad

| **Campo**                  | **Descripción**                                                                                                                                                                                                          |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Nombre del Caso de Uso** | Actualizar estado de incapacidad                                                                                                                                                                                         |
| **Identificación**         | UC8                                                                                                                                                                                                                      |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                               |
| **Referencia**             | CAR-04, ON-02                                                                                                                                                                                                            |
| **Tipo implementación**    | Release 2.0                                                                                                                                                                                                              |
| **Actores**                | Auxiliar de Gestión Humana, Sistema                                                                                                                                                                                      |
| **Propósito**              | Mantener actualizado el estado de cada incapacidad a lo largo de su ciclo de vida, permitiendo trazabilidad completa del proceso.                                                                                        |
| **Resumen**                | El auxiliar actualiza manualmente el estado de las incapacidades conforme avanza el proceso, o el sistema lo hace automáticamente en ciertos eventos. Se registra historial completo con fechas y usuarios responsables. |
| **Precondición**           | - Existe una incapacidad registrada en el sistema.<br>- El estado a actualizar debe ser válido según el flujo del proceso.                                                                                               |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                                          | **Respuesta del Sistema**                                                                |
| ----- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1     | El auxiliar accede al detalle de una incapacidad                                                   | Muestra estado actual e historial de estados                                             |
| 2     | Selecciona "Actualizar estado"                                                                     | Muestra lista de estados válidos según estado actual                                     |
| 3     | Selecciona nuevo estado de la lista (Transcrita, Cobrada, Rechazada por entidad, Pagada)           | Valida transición de estado                                                              |
| 4     | (Opcional) Agrega observaciones sobre el cambio                                                    | Registra observaciones                                                                   |
| 5     | (Si aplica) Adjunta documento soporte (ej: comprobante de radicación, notificación de rechazo EPS) | Almacena documento asociado al cambio de estado                                          |
| 6     | Confirma actualización                                                                             | Actualiza estado de la incapacidad                                                       |
| 7     |                                                                                                    | Registra en historial: fecha/hora, estado anterior, estado nuevo, usuario, observaciones |
| 8     |                                                                                                    | Si estado = "Rechazada por entidad": solicita causal de rechazo                          |
| 9     |                                                                                                    | Si estado = "Pagada": solicita fecha y valor del pago                                    |
| 10    |                                                                                                    | Genera notificación interna si el estado requiere acción de otra área                    |

---

| **Postcondición** |                                                                                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|                   | - El estado de la incapacidad ha sido actualizado.<br>- Queda registro en historial con trazabilidad completa.<br>- Se generan notificaciones si corresponde. |

---

### **Estados válidos del sistema**

* Pendiente de validación
* Documentación incompleta
* Documentación completa
* Aprobada - Pendiente transcripción
* Transcrita (radicada en EPS/ARL)
* Cobrada (aprobada por entidad, pendiente pago)
* Rechazada por entidad
* Pagada
* Rechazada (por validación interna)

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                                     |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Transición inválida:** Si el auxiliar intenta cambiar a un estado no válido desde el estado actual (ej: de "Pendiente validación" a "Pagada"), el sistema muestra error y explica flujo correcto. |
| **E2** | **Rechazada por entidad sin causal:** Si se marca como rechazada por EPS/ARL sin especificar causal, el sistema no permite guardar y solicita la información obligatoria.                           |
| **E3** | **Pagada sin valor:** Si se marca como pagada sin especificar valor y fecha, el sistema solicita estos datos obligatorios.                                                                          |
| **E4** | **Actualización automática:** Algunos cambios de estado se realizan automáticamente (ej: al aprobar en UC7, auto-cambia a "Aprobada").                                                              |

---

| **Campo**               | **Descripción**                 |
| ----------------------- | ------------------------------- |
| **Frecuencia esperada** | 200-400 actualizaciones por mes |
| **Importancia**         | Alta                            |
| **Urgencia**            | Alta                            |

---

### UC9 - Consultar estado de radicación

| **Campo**                  | **Descripción**                                                                                                                                                            |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Consultar estado de radicación                                                                                                                                             |
| **Identificación**         | UC9                                                                                                                                                                        |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                 |
| **Referencia**             | CAR-04, ON-02                                                                                                                                                              |
| **Tipo implementación**    | Release 2.0                                                                                                                                                                |
| **Actores**                | Auxiliar de Gestión Humana                                                                                                                                                 |
| **Propósito**              | Permitir al auxiliar consultar el estado actual de radicación de las incapacidades ante EPS/ARL para realizar seguimiento y gestión de cobro.                            |
| **Resumen**                | El auxiliar consulta las incapacidades que han sido transcritas y radicadas ante las entidades para verificar su estado (en verificación, aprobada, rechazada) y realizar las acciones correspondientes. |
| **Precondición**           | - El auxiliar debe estar autenticado<br>- Deben existir incapacidades en estado "Transcrita" o posterior                                                                  |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                      | **Respuesta del Sistema**                                                                           |
| ----- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| 1     | Accede al módulo de seguimiento de radicaciones                                | Muestra dashboard con resumen por estado: Transcritas, Cobradas, Rechazadas, Pagadas              |
| 2     | Visualiza indicadores: total pendientes, tiempo promedio, alertas de vencimiento | Calcula y muestra métricas actualizadas                                                             |
| 3     | Aplica filtros: por entidad, por fecha, por estado, por colaborador            | Actualiza listado según filtros                                                                    |
| 4     | Selecciona una entidad específica (ej: Sura EPS)                               | Muestra todas las incapacidades de esa entidad con sus estados                                     |
| 5     | Identifica incapacidades próximas a vencer plazo de transcripción              | Sistema resalta en color las que están cerca del límite (ej: Sura 150 días)                        |
| 6     | Selecciona una incapacidad específica                                          | Muestra detalle completo con línea de tiempo de estados                                             |
| 7     | Verifica documentación de radicación adjunta                                   | Permite visualizar comprobantes de radicación                                                       |
| 8     | Registra gestión realizada (llamada, correo, visita)                           | Guarda log de gestiones con fecha y descripción                                                     |

---

### **Postcondición**

* El auxiliar tiene visibilidad del estado de todas las radicaciones
* Se registran las gestiones de seguimiento realizadas
* Se identifican casos que requieren acción

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                  |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Sin incapacidades transcritas:** Si no hay incapacidades en estado "Transcrita" o posterior, el sistema muestra mensaje informativo.                                            |
| **E2** | **Alerta de vencimiento crítico:** Si una incapacidad está por vencer el plazo de transcripción (últimos 10 días), el sistema muestra alerta roja prominente.                    |
| **E3** | **Incapacidades vencidas:** Si el plazo ya venció, el sistema marca en estado especial y sugiere contactar coordinación para acción jurídica.                                    |

---

| **Campo**               | **Descripción**            |
| ----------------------- | -------------------------- |
| **Frecuencia esperada** | 100-200 consultas por mes |
| **Importancia**         | Alta                       |
| **Urgencia**            | Alta                       |

---

### UC10 - Generar reporte de seguimiento

| **Campo**                  | **Descripción**                                                                                                                                                               |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Generar reporte de seguimiento                                                                                                                                                |
| **Identificación**         | UC10                                                                                                                                                                          |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                    |
| **Referencia**             | CAR-04, ON-02, ON-04                                                                                                                                                          |
| **Tipo implementación**    | Release 2.0                                                                                                                                                                   |
| **Actores**                | Auxiliar de Gestión Humana                                                                                                                                                    |
| **Propósito**              | Generar reportes consolidados del estado de las incapacidades para análisis, seguimiento y toma de decisiones.                                                               |
| **Resumen**                | El auxiliar selecciona criterios de reporte (período, entidad, estado, etc.) y el sistema genera un documento consolidado con la información solicitada en formato exportable. |
| **Precondición**           | - El auxiliar debe estar autenticado<br>- Deben existir incapacidades registradas en el período consultado                                                                   |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                                              | **Respuesta del Sistema**                                                                       |
| ----- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| 1     | Accede al módulo de reportes                                                                           | Muestra interfaz de generación de reportes con opciones                                         |
| 2     | Selecciona tipo de reporte: Por estado, Por entidad, Por período, Por colaborador, General             | Muestra filtros específicos según tipo seleccionado                                             |
| 3     | Define rango de fechas (desde - hasta)                                                                 | Valida que la fecha inicial sea menor que la final                                              |
| 4     | (Opcional) Aplica filtros adicionales: entidad específica, área, tipo de incapacidad                  | Registra filtros seleccionados                                                                  |
| 5     | Selecciona formato de salida: PDF, Excel, CSV                                                          | Registra formato deseado                                                                        |
| 6     | Solicita generar reporte                                                                               | Procesa consulta con filtros aplicados                                                          |
| 7     |                                                                                                        | Extrae datos de incapacidades que cumplen criterios                                             |
| 8     |                                                                                                        | Calcula estadísticas: total incapacidades, por estado, días promedio, valor total estimado      |
| 9     |                                                                                                        | Genera gráficos resumen (distribución por estado, por entidad, tendencias)                      |
| 10    |                                                                                                        | Formatea documento según formato solicitado                                                     |
| 11    |                                                                                                        | Muestra vista previa del reporte                                                                |
| 12    | Revisa reporte y confirma descarga                                                                     | Genera archivo y permite descarga                                                               |
| 13    | Descarga reporte                                                                                       | Registra log de reporte generado (usuario, fecha, filtros)                                      |

---

### **Postcondición**

* Se genera reporte con información consolidada
* El reporte está disponible para descarga
* Queda registro de reporte generado

---

### **Tipos de reportes disponibles**

* **Reporte por estado:** Todas las incapacidades agrupadas por estado actual
* **Reporte por entidad:** Distribución por EPS/ARL con estadísticas
* **Reporte de pagos pendientes:** Incapacidades cobradas pero sin pago
* **Reporte de ausentismo:** Días totales de incapacidad por área/período
* **Reporte general:** Vista completa de todas las incapacidades

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Sin datos en el período:** Si no hay incapacidades en el rango de fechas seleccionado, el sistema muestra mensaje "No hay datos para generar reporte" y sugiere ampliar criterios.             |
| **E2** | **Rango de fechas muy amplio:** Si el rango supera 2 años, el sistema advierte que puede tardar y solicita confirmación.                                                                         |
| **E3** | **Error al generar archivo:** Si hay error técnico, el sistema muestra mensaje de error y permite reintentar o cambiar formato.                                                                  |
| **E4** | **Reporte muy grande:** Si el resultado supera 10,000 registros, el sistema sugiere aplicar más filtros o dividir en reportes más pequeños.                                                      |

---

| **Campo**               | **Descripción**        |
| ----------------------- | ---------------------- |
| **Frecuencia esperada** | 20-30 reportes por mes |
| **Importancia**         | Alta                   |
| **Urgencia**            | Media                  |

---

### UC11 - Ver incapacidades del equipo

| **Campo**                  | **Descripción**                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Nombre del Caso de Uso** | Ver incapacidades del equipo                                                                                                                                       |
| **Identificación**         | UC11                                                                                                                                                               |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                         |
| **Referencia**             | CAR-03, ON-01                                                                                                                                                      |
| **Tipo implementación**    | Release 2.0                                                                                                                                                        |
| **Actores**                | Líder Inmediato                                                                                                                                                    |
| **Propósito**              | Permitir a los líderes consultar las incapacidades de su equipo para gestionar reemplazos y planificar recursos.                                                   |
| **Resumen**                | El líder accede a una vista consolidada de las incapacidades de todos los colaboradores bajo su cargo, pudiendo ver estado actual, fechas y planificar coberturas. |
| **Precondición**           | - El líder debe estar autenticado con rol de líder<br>- Debe tener colaboradores asignados a su cargo                                                           |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                        | **Respuesta del Sistema**                                                                   |
| ----- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 1     | Accede al módulo "Incapacidades de mi equipo"                                   | Identifica colaboradores bajo su cargo                                                      |
| 2     |                                                                                 | Muestra dashboard con incapacidades activas e históricas del equipo                         |
| 3     | Visualiza vista de calendario con incapacidades activas                         | Muestra calendario con períodos de incapacidad marcados                                    |
| 4     | Visualiza lista de incapacidades: colaborador, tipo, fechas, días, estado       | Presenta tabla ordenada por fecha de inicio                                                 |
| 5     | (Opcional) Filtra por: colaborador específico, tipo de incapacidad, período     | Actualiza vista según filtros                                                               |
| 6     | Selecciona una incapacidad para ver detalle                                     | Muestra información detallada (respetando privacidad médica - sin diagnósticos)            |
| 7     | Identifica necesidad de reemplazo                                               | Visualiza información básica para planificación                                             |
| 8     | (Opcional) Agrega nota sobre gestión de reemplazo                               | Sistema registra nota asociada a esa incapacidad                                            |
| 9     | (Opcional) Exporta calendario de ausencias                                      | Genera archivo con cronograma de incapacidades                                              |

---

### **Postcondición**

* El líder tiene visibilidad de ausencias de su equipo
* Puede planificar reemplazos informadamente
* Se respeta privacidad médica (no se muestran diagnósticos)

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                                 |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Sin colaboradores asignados:** Si el líder no tiene colaboradores a cargo, el sistema muestra mensaje "No tiene colaboradores asignados actualmente".                                  |
| **E2** | **Sin incapacidades en el período:** Si ningún colaborador del equipo tiene incapacidades, el sistema muestra mensaje "Su equipo no tiene incapacidades registradas".                   |
| **E3** | **Intento de acceso a información médica:** Si el líder intenta acceder a diagnósticos o información médica restringida, el sistema muestra "Información confidencial - No disponible". |

---

| **Campo**               | **Descripción**              |
| ----------------------- | ---------------------------- |
| **Frecuencia esperada** | 100-150 consultas por mes   |
| **Importancia**         | Media                        |
| **Urgencia**            | Media                        |

---

## Módulo de Conciliación

### UC12 - Registrar pago de EPS/ARL

| **Campo**                  | **Descripción**                                                                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Nombre del Caso de Uso** | Registrar pago de EPS/ARL                                                                                                                                                                                          |
| **Identificación**         | UC12                                                                                                                                                                                                               |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                         |
| **Referencia**             | CAR-05, ON-04                                                                                                                                                                                                      |
| **Tipo implementación**    | Release 3.0                                                                                                                                                                                                        |
| **Actores**                | Auxiliar de Gestión Humana                                                                                                                                                                                         |
| **Propósito**              | Registrar los pagos recibidos de las entidades EPS/ARL por concepto de incapacidades, asociándolos con las incapacidades correspondientes.                                                                          |
| **Resumen**                | Cuando Contabilidad informa sobre un pago recibido de una EPS/ARL, el auxiliar registra el pago en el sistema, identifica las incapacidades que cubre y actualiza sus estados correspondientes.                     |
| **Precondición**           | - El auxiliar debe estar autenticado<br>- Contabilidad debe haber informado sobre un pago recibido<br>- Deben existir incapacidades en estado "Cobrada" de la entidad pagadora                                       |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                                        | **Respuesta del Sistema**                                                                               |
| ----- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| 1     | Recibe notificación de Contabilidad sobre pago recibido                                          | -                                                                                                       |
| 2     | Accede al módulo de registro de pagos                                                            | Muestra formulario de registro de pago                                                                  |
| 3     | Selecciona entidad pagadora (EPS o ARL específica)                                               | Filtra incapacidades cobradas de esa entidad                                                            |
| 4     | Ingresa fecha de pago recibido                                                                   | Valida formato de fecha                                                                                 |
| 5     | Ingresa valor total del pago                                                                     | Valida formato numérico                                                                                 |
| 6     | Ingresa número de referencia o comprobante                                                       | Registra referencia                                                                                     |
| 7     | (Opcional) Adjunta comprobante de pago (PDF)                                                     | Almacena documento                                                                                      |
| 8     |                                                                                                  | Muestra listado de incapacidades en estado "Cobrada" de esa entidad con sus valores                    |
| 9     | Selecciona las incapacidades que cubre este pago (puede ser una o varias)                        | Marca incapacidades seleccionadas y suma valores                                                        |
| 10    |                                                                                                  | Verifica si la suma coincide con el valor total del pago                                                |
| 11    | Confirma registro del pago                                                                       | Valida información completa                                                                             |
| 12    |                                                                                                  | Ejecuta UC8 - Actualiza estado de incapacidades seleccionadas a "Pagada"                               |
| 13    |                                                                                                  | Registra en cada incapacidad: fecha de pago, valor pagado, referencia                                  |
| 14    |                                                                                                  | Genera registro de pago con detalle de incapacidades cubiertas                                          |
| 15    |                                                                                                  | Notifica a Contabilidad que el pago fue identificado y asignado                                         |

---

### **Postcondición**

* El pago queda registrado en el sistema
* Las incapacidades asociadas cambian a estado "Pagada"
* Contabilidad es notificada para conciliación
* Queda trazabilidad completa del pago

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                                                                                           |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Valor del pago no coincide:** Si la suma de incapacidades seleccionadas no coincide exactamente con el valor del pago, el sistema muestra alerta. El auxiliar puede: 1) Revisar selección, 2) Registrar diferencia como "pendiente de identificación", 3) Registrar pago parcial. |
| **E2** | **Sin incapacidades cobradas de esa entidad:** Si no hay incapacidades en estado "Cobrada" de la entidad, el sistema alerta que podría ser pago de períodos anteriores y sugiere buscar en históricos.                                                    |
| **E3** | **Pago global sin detalle:** Si la entidad paga valor global sin especificar detalle, el auxiliar debe consultar portal de la entidad para obtener detalle de liquidación antes de asignar.                                                               |
| **E4** | **Pago duplicado:** Si ya existe un registro de pago con misma referencia, fecha y valor, el sistema alerta posible duplicación y solicita confirmación.                                                                                                    |
| **E5** | **Diferencia por descuentos:** Si la entidad aplicó descuentos o deducciones, el auxiliar registra el valor neto recibido y documenta la diferencia en observaciones.                                                                                     |

---

| **Campo**               | **Descripción**        |
| ----------------------- | ---------------------- |
| **Frecuencia esperada** | 30-50 pagos por mes   |
| **Importancia**         | Alta                   |
| **Urgencia**            | Alta                   |

---

### UC13 - Conciliar pagos mensualmente

| **Campo**                  | **Descripción**                                                                                                                                                                                                         |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Conciliar pagos mensualmente                                                                                                                                                                                            |
| **Identificación**         | UC13                                                                                                                                                                                                                    |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                              |
| **Referencia**             | CAR-05, ON-04                                                                                                                                                                                                           |
| **Tipo implementación**    | Release 3.0                                                                                                                                                                                                             |
| **Actores**                | Contabilidad, Auxiliar de Gestión Humana                                                                                                                                                                                |
| **Propósito**              | Realizar conciliación mensual entre los pagos recibidos de EPS/ARL, los registros del sistema y los registros contables para garantizar coherencia financiera.                                                           |
| **Resumen**                | Al cierre de cada mes, Contabilidad y Gestión Humana realizan proceso de conciliación cruzando información de pagos recibidos, incapacidades pagadas y registros contables, generando reporte de conciliación.        |
| **Precondición**           | - Han transcurrido al menos un mes de operación<br>- Existen pagos registrados en el período<br>- Contabilidad tiene registros de movimientos bancarios                                                                 |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                | **Respuesta del Sistema**                                                                                                                                 |
| ----- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Contabilidad solicita reporte de pagos del mes                          | -                                                                                                                                                       |
| 2     | Auxiliar accede al módulo de conciliación                               | Muestra interfaz de conciliación mensual                                                                                                                |
| 3     | Selecciona período de conciliación (mes y año)                          | Valida período seleccionado                                                                                                                             |
| 4     | Solicita generar reporte de conciliación                                | Extrae datos del período: pagos registrados, incapacidades pagadas, valores                                                                              |
| 5     |                                                                        | Agrupa información por entidad (EPS/ARL)                                                                                                                |
| 6     |                                                                        | Calcula para cada entidad: total incapacidades pagadas, valor total pagado, cantidad de incapacidades, promedio de días de pago                       |
| 7     |                                                                        | Identifica incapacidades del mes que aún no están pagadas                                                                                                |
| 8     |                                                                        | Genera reporte consolidado con: resumen ejecutivo, detalle por entidad, listado de pagadas, listado de pendientes, análisis de antigüedad              |
| 9     |                                                                        | Muestra vista previa del reporte                                                                                                                        |
| 10    | Auxiliar revisa reporte y exporta a Excel                               | Sistema genera archivo Excel con múltiples hojas                                                                                                        |
| 11    | Envía reporte a Contabilidad                                            | -                                                                                                                                                       |
| 12    | Contabilidad compara con registros bancarios y contables                | -                                                                                                                                                       |
| 13    | Contabilidad identifica coincidencias y diferencias                     | -                                                                                                                                                       |
| 14    | Si hay diferencias: Contabilidad solicita aclaración al auxiliar        | -                                                                                                                                                       |
| 15    | Auxiliar investiga diferencias y proporciona documentación soporte      | Permite consultar detalle de cada transacción                                                                                                           |
| 16    | Una vez conciliado: Contabilidad confirma conciliación                  | -                                                                                                                                                       |
| 17    | Auxiliar marca el período como "Conciliado" en el sistema               | Sistema registra fecha de conciliación y usuarios participantes                                                                                         |
| 18    |                                                                        | Almacena reporte final de conciliación como documento histórico                                                                                         |

---

### **Postcondición**

* El período queda marcado como conciliado
* Se genera reporte oficial de conciliación
* Se identifican y documentan diferencias si existen
* Contabilidad puede causar correctamente los pagos

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                                           |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Sin movimientos en el período:** Si no hubo pagos en el mes seleccionado, el sistema genera reporte indicando "Sin movimientos" pero igual documenta el período.                                        |
| **E2** | **Diferencias no identificadas:** Si después de investigación persisten diferencias sin explicación, se documenta en observaciones y se puede escalar a coordinación y/o área jurídica.                  |
| **E3** | **Período ya conciliado:** Si se intenta conciliar un período ya marcado como conciliado, el sistema advierte y solicita confirmación para re-conciliar.                                                 |
| **E4** | **Pagos de años anteriores:** Si se identifican pagos de incapacidades de años anteriores, se documenta especialmente y se incluye en sección separada del reporte.                                       |
| **E5** | **Conciliación parcial:** Si Contabilidad solo puede conciliar parcialmente, el auxiliar puede marcar "Conciliación parcial pendiente" con observaciones de lo que falta.                                |

---

| **Campo**               | **Descripción**              |
| ----------------------- | ---------------------------- |
| **Frecuencia esperada** | 12 veces al año (mensual)   |
| **Importancia**         | Alta                         |
| **Urgencia**            | Media                        |

---

### UC14 - Generar reporte de pagos pendientes

| **Campo**                  | **Descripción**                                                                                                                                                                                                                  |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Generar reporte de pagos pendientes                                                                                                                                                                                             |
| **Identificación**         | UC14                                                                                                                                                                                                                             |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                                       |
| **Referencia**             | CAR-04, ON-02, ON-04                                                                                                                                                                                                             |
| **Tipo implementación**    | Release 3.0                                                                                                                                                                                                                      |
| **Actores**                | Auxiliar de Gestión Humana                                                                                                                                                                                                       |
| **Propósito**              | Generar reporte de todas las incapacidades que están en estado "Cobrada" (aprobadas por la entidad pero pendientes de pago) para hacer seguimiento y gestión de cobro.                                                           |
| **Resumen**                | El auxiliar genera un reporte que muestra todas las incapacidades pendientes de pago, organizadas por entidad y antigüedad, permitiendo priorizar gestiones de cobro e identificar casos críticos.                                 |
| **Precondición**           | - El auxiliar debe estar autenticado<br>- Deben existir incapacidades en estado "Cobrada"                                                                                                                                        |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                      | **Respuesta del Sistema**                                                                                                                 |
| ----- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------  |
| 1     | Accede al módulo de reportes de cobro                                          | Muestra opciones de reportes financieros                                                                                                 |
| 2     | Selecciona "Reporte de pagos pendientes"                                       | Muestra interfaz de generación                                                                                                           |
| 3     | (Opcional) Filtra por entidad específica                                       | Registra filtro                                                                                                                          |
| 4     | (Opcional) Define umbral de antigüedad (ej: mayores a 30 días)                 | Registra filtro de antigüedad                                                                                                            |
| 5     | Solicita generar reporte                                                       | Consulta todas las incapacidades en estado "Cobrada"                                                                                     |
| 6     |                                                                                | Calcula para cada una: días desde que fue marcada como cobrada                                                                            |
| 7     |                                                                                | Clasifica por antigüedad: Recientes (0-30), Moderadas (31-90), Críticas (91-180), Muy críticas (>180 días)                            |
| 8     |                                                                                | Agrupa por entidad (EPS/ARL)                                                                                                             |
| 9     |                                                                                | Calcula totales: cantidad pendiente, valor total, valor por entidad, antigüedad promedio                                                |
| 10    |                                                                                | Genera alertas para casos críticos (>180 días)                                                                                           |
| 11    |                                                                                | Identifica incapacidades que requieren acción jurídica                                                                                    |
| 12    |                                                                                | Muestra dashboard visual con: gráfico de torta por entidad, gráfico de barras por antigüedad, tabla detallada                           |
| 13    | Revisa información en pantalla                                                 | Presenta información de forma clara y accionable                                                                                         |
| 14    | Exporta reporte a Excel                                                        | Genera archivo con múltiples hojas: resumen, detalle por entidad, casos críticos                                                        |
| 15    | Descarga reporte para compartir con coordinación                               | Registra log de reporte generado                                                                                                        |

---

### **Postcondición**

* Se genera reporte actualizado de pagos pendientes
* Se identifican casos que requieren acción prioritaria
* Coordinación tiene información para tomar decisiones
* Se priorizan gestiones de cobro

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                                                            |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Sin pagos pendientes:** Si no hay incapacidades en estado "Cobrada", el sistema muestra mensaje positivo "¡Excelente! No hay pagos pendientes actualmente".                                                              |
| **E2** | **Casos críticos detectados:** Si hay incapacidades con más de 180 días pendientes, el sistema genera alerta prominente y sugiere revisar para posible acción jurídica.                                                     |
| **E3** | **Entidad con muchos pendientes:** Si una entidad específica tiene más de 20 incapacidades pendientes, el sistema sugiere contactar representante de la entidad.                                                             |
| **E4** | **Valor significativo pendiente:** Si el valor total pendiente supera umbral definido (ej: $50,000,000), el sistema destaca esta información para escalamiento.                                                            |

---

| **Campo**               | **Descripción**           |
| ----------------------- | ------------------------- |
| **Frecuencia esperada** | 20-30 veces por mes      |
| **Importancia**         | Alta                      |
| **Urgencia**            | Alta                      |

---

## Módulo de Gestión Documental

### UC15 - Almacenar documentos digitalmente

| **Campo**                  | **Descripción**                                                                                                                                                                                                                                |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del Caso de Uso** | Almacenar documentos digitalmente                                                                                                                                                                                                               |
| **Identificación**         | UC15                                                                                                                                                                                                                                           |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                                                                                                     |
| **Referencia**             | CAR-07, ON-03                                                                                                                                                                                                                                  |
| **Tipo implementación**    | Release 1.0                                                                                                                                                                                                                                    |
| **Actores**                | Sistema (automático)                                                                                                                                                                                                                           |
| **Propósito**              | Almacenar de forma segura y organizada todos los documentos digitales asociados a las incapacidades, garantizando custodia, trazabilidad y disponibilidad.                                                                                       |
| **Resumen**                | Cuando se cargan documentos al sistema (desde UC1 u otros casos de uso), el sistema los almacena en repositorio digital seguro con estructura organizada, aplicando políticas de seguridad y generando respaldos automáticos.                    |
| **Precondición**           | - Se ha cargado un documento al sistema<br>- El documento cumple con requisitos de formato y tamaño                                                                                                                                            |

---

### **Flujo Normal de los Eventos**

| **#** | **Acción de los Actores**                                                          | **Respuesta del Sistema**                                                                                                                                    |
| ----- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Se invoca desde UC1 u otro proceso que requiere almacenar documento                | Recibe archivo y metadata asociada                                                                                                                         |
| 2     |                                                                                    | Genera identificador único para el documento (UUID)                                                                                                         |
| 3     |                                                                                    | Calcula hash MD5 del archivo para verificación de integridad                                                                                                |
| 4     |                                                                                    | Determina ruta de almacenamiento según estructura: /año/mes/tipo_documento/colaborador_id/UUID.ext                                                       |
| 5     |                                                                                    | Verifica espacio disponible en almacenamiento                                                                                                               |
| 6     |                                                                                    | Almacena archivo físico en servidor de archivos                                                                                                             |
| 7     |                                                                                    | Registra en base de datos: ID único, nombre original, ruta, tamaño, tipo, hash MD5, fecha, usuario, ID incapacidad                                       |
| 8     |                                                                                    | Aplica permisos de acceso según rol (solo usuarios autorizados)                                                                                             |
| 9     |                                                                                    | Si es documento sensible (epicrisis, historia clínica): aplica cifrado adicional                                                                           |
| 10    |                                                                                    | Genera miniatura/vista previa si es imagen                                                                                                                 |
| 11    |                                                                                    | Programa respaldo automático en almacenamiento secundario                                                                                                   |
| 12    |                                                                                    | Registra log de operación de almacenamiento                                                                                                                |
| 13    |                                                                                    | Retorna confirmación de almacenamiento exitoso con ID del documento                                                                                        |

---

### **Postcondición**

* El documento está almacenado de forma segura
* Existe registro en base de datos con metadata completa
* Se ha generado respaldo automático
* Se han aplicado políticas de seguridad y permisos
* El documento es recuperable mediante su ID único

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                        |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Espacio insuficiente:** Si no hay espacio disponible en almacenamiento, el sistema notifica al administrador, intenta almacenar en ubicación secundaria y registra alerta.             |
| **E2** | **Error de escritura:** Si falla el almacenamiento físico, el sistema reintenta 3 veces. Si persiste, notifica error y no registra en base de datos.                                  |
| **E3** | **Archivo corrupto:** Si el archivo no se puede leer o está corrupto, el sistema rechaza el almacenamiento y notifica al usuario.                                                      |
| **E4** | **Documento duplicado:** Si ya existe un documento con el mismo hash MD5 para la misma incapacidad, el sistema alerta posible duplicación pero permite almacenar si se confirma.       |
| **E5** | **Error en respaldo:** Si falla el respaldo automático, el sistema registra alerta y programa reintento en siguiente ventana de respaldo.                                              |

---

| **Campo**               | **Descripción**              |
| ----------------------- | ---------------------------- |
| **Frecuencia esperada** | 200-500 documentos por mes  |
| **Importancia**         | Alta                         |
| **Urgencia**            | Alta                         |

---

### UC16 - Descargar incapacidad completa

| **Campo**                  | **Descripción**                                                                                                                                                          |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Nombre del Caso de Uso** | Descargar incapacidad completa                                                                                                                                           |
| **Identificación**         | UC16                                                                                                                                                                     |
| **Fecha Inicial**          | 04/10/2025                                                                                                                                                               |
| **Referencia**             | CAR-07, ON-03                                                                                                                                                           |
| **Tipo implementación**    | Release 2.0                                                                                                                                                              |
| **Actores**                | Auxiliar de Gestión Humana, Colaborador (limitado)                                                                                                                      |
| **Propósito**              | Permitir descargar toda la documentación asociada a una incapacidad de forma organizada para envío a entidades, archivo o consulta.                                      |
| **Resumen**                | El usuario autorizado puede descargar todos los documentos de una incapacidad específica, ya sea individualmente o en un archivo ZIP organizado con toda la documentación. |
| **Precondición**           | - El usuario debe estar autenticado con permisos adecuados<br>- La incapacidad debe tener documentos almacenados                                                       |

---

### **Flujo Normal de los Eventos - Descarga Individual**

| **#** | **Acción de los Actores**                                                                                                             | **Respuesta del Sistema**                                                                   |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| 1     | Usuario accede al detalle de una incapacidad                                                                                         | Muestra información completa y lista de documentos adjuntos                                 |
| 2     | Visualiza lista de documentos disponibles: Certificado, Epicrisis, FURIPS, Otros documentos                                         | Presenta tabla con nombre, tipo, tamaño, fecha de carga                                     |
| 3     | Selecciona un documento específico para descargar                                                                                    | Verifica permisos del usuario para ese documento                                            |
| 4     | Confirma descarga                                                                                                                    | Recupera archivo del almacenamiento                                                         |
| 5     |                                                                                                                                      | Verifica integridad mediante hash MD5                                                       |
| 6     |                                                                                                                                      | Genera token temporal de descarga                                                           |
| 7     |                                                                                                                                      | Inicia descarga del archivo individual                                                      |
| 8     |                                                                                                                                      | Registra log: quién descargó, qué documento, cuándo                                         |

---

### **Flujo Alterno - Descarga Paquete Completo**

| **#** | **Acción de los Actores**                                                   | **Respuesta del Sistema**                                                                                                                                  |
| ----- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Usuario selecciona "Descargar todo en ZIP"                                 | Verifica permisos para todos los documentos                                                                                                               |
| 2     |                                                                             | Recupera todos los documentos de la incapacidad                                                                                                           |
| 3     |                                                                             | Crea estructura de carpetas: Incapacidad_[código]/ con subcarpetas: Certificado/, Documentos_Soporte/, Comprobantes/, info.txt                          |
| 4     |                                                                             | Organiza documentos en carpetas correspondientes                                                                                                         |
| 5     |                                                                             | Genera archivo info.txt con: datos del colaborador, tipo de incapacidad, fechas y días, estado actual, historial de estados, lista de documentos       |
| 6     |                                                                             | Comprime todo en archivo ZIP                                                                                                                             |
| 7     |                                                                             | Calcula tamaño total del ZIP                                                                                                                             |
| 8     | Confirma descarga del ZIP                                                  | Inicia descarga del archivo comprimido                                                                                                                   |
| 9     |                                                                             | Registra log de descarga completa                                                                                                                        |
| 10    | Recibe archivo ZIP organizado                                              | Limpia archivos temporales del servidor                                                                                                                  |

---

### **Postcondición**

* El usuario ha descargado la documentación solicitada
* Queda registro de auditoría de la descarga
* Los documentos descargados mantienen integridad
* Si es ZIP: incluye estructura organizada y archivo de información

---

### **Flujo Alterno de los Eventos (Excepciones)**

| **#**  | **Descripción**                                                                                                                                                                                                                                |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1** | **Usuario sin permisos:** Si el usuario no tiene permisos para descargar ciertos documentos (ej: colaborador intentando descargar epicrisis de otro), el sistema niega acceso y muestra mensaje de permiso insuficiente.                        |
| **E2** | **Documento no encontrado:** Si un documento está registrado pero no se encuentra físicamente, el sistema notifica error, registra alerta para administrador y omite ese documento del ZIP.                                                     |
| **E3** | **Archivo corrupto:** Si la verificación de hash MD5 falla, el sistema no permite descarga y notifica que el archivo puede estar corrupto, sugiere contactar soporte.                                                                           |
| **E4** | **ZIP muy grande:** Si el tamaño total supera 100MB, el sistema advierte que la descarga puede tardar y ofrece descargar documentos individuales en lugar de ZIP completo.                                                                     |
| **E5** | **Falla en compresión:** Si hay error al crear el ZIP, el sistema permite descargar documentos individualmente como alternativa.                                                                                                                |
| **E6** | **Colaborador descargando propia incapacidad:** El colaborador solo puede descargar documentos que él mismo cargó, no documentos internos o confidenciales agregados por Gestión Humana.                                                       |

---

| **Campo**               | **Descripción**        |
| ----------------------- | ---------------------- |
| **Frecuencia esperada** | 80-120 descargas/mes  |
| **Importancia**         | Media                  |
| **Urgencia**            | Media                  |

