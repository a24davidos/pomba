# Estudo preliminar - Anteproxecto

## Descrición do proxecto

El proyecto consiste en crear una plataforma web de almacenamiento personal de archivos, que permita a los usuarios guardar, organizar, y compartir documentos, imágenes y otro tipo de ficheros.

### Xustificación do proxecto.

Este proyecto nace como una alternativa para usuarios que buscan soluciones de almacenamiento en línea simples y seguras, sin depender de servicios externos como Google Drive o Dropbox.

Además, ante la creciente evolución de la inteligencia artificial, la privacidad de tus datos ya no está garantizada, y no existe certeza de que empresas como Google no puedan estar utilizando información o fotografías de los usuarios para entrenar sus modelos.

### Funcionalidades do proxecto.

#### Requisitos funcionales

1. **Gestión de usuarios**
   - El sistema debe permitir registrar nuevos usuarios.
   - El sistema debe permitir iniciar sesión y cerrar sesión.
   - El sistema debe permitir que los usuarios vean y editen su perfil.
   - El sistema permitirá a los usuarios subir una foto de perfil.
   - El sistema debe registrar el historial de actividad del usuario. (Aún no se si meter esto, o si tiene sentido)
2. **Gestión de carpetas**
   - El sistema debe permitir crear carpetas dentro de otras carpetas (estructura en árbol).
   - El sistema debe permitir renombrar carpetas.
   - El sistema debe permitir eliminar carpetas.
   - El sistema debe mostrar al usuario la jerarquía completa de carpetas a la que tiene acceso.
3. **Gestión de archivos**
   - El sistema debe permitir subir archivos al servidor y guardar sus metadatos en la base de datos.
   - El sistema debe permitir descargar archivos según permisos.
   - El sistema debe permitir eliminar archivos.
   - El sistema debe permitir organizar archivos dentro de carpetas.
   - El sistema debe validar el tipo de archivo y el tamaño máximo permitido.
4. **Compartir y permisos**
   - El sistema debe permitir compartir archivos o carpetas con otros usuarios.
   - El sistema debe permitir asignar permisos de lectura o escritura a otros usuarios.
   - El sistema debe restringir el acceso a archivos y carpetas según permisos.
5. **Búsqueda y navegación**
   - El sistema debe permitir buscar archivos por nombre, tipo, carpeta, metadatos y contenido de archivos TXT.
   - El sistema debe permitir navegar por la estructura de carpetas como un explorador.
6. **Extras opcionales**
   - El sistema debe mostrar al usuario la cuota de almacenamiento utilizada.
   - El sistema guardará los archivos eliminados hasta 30 días en la papelera
   - El sistema debe permitir recuperar archivos eliminados desde la papelera.

#### Requisitos no funcionales

1. **Seguridad**
   - El sistema debe almacenar las contraseñas de forma segura.
   - El sistema debe usar autenticación basada en sesiones.
   - El sistema debe validar todos los datos introducidos por el usuario.
2. **Disponibilidad y rendimiento**
   - El sistema debe permitir subir archivos de hasta un tamaño límite sin afectar la estabilidad.
   - La navegación por carpetas y archivos debe ser rápida y eficiente.
3. **Escalabilidad y mantenibilidad**
   - El sistema debe estar dockerizado para facilitar su despliegue y mantenimiento.
   - La arquitectura debe permitir añadir futuras funcionalidades como versionado de archivos o previsualización.
4. **Usabilidad**
   - La interfaz debe ser intuitiva y sencilla, tipo explorador de archivos.
   - Los mensajes de error deben ser claros y útiles para el usuario.

### Persoas destinatarias.

- Estudiantes
- Profesionales que necesiten un lugar donde guardar y organizar documentos.
- Usuarios con interés en la privacidad y el control

### Promoción.

- El proyecto será accesible únicamente mediante un repositorio público en Git Lab.
- Cualquier persona podrá clonar el proyecto y crear su propia version.

### Modelo de negocio.

- El proyecto seguirá un modelo open source, permitiendo que cualquier pueda acceder al código, clonarlo y crear su propia version. 

## Requirimentos

##### Backend: 

- Framework: Django
  - Gestionar usuarios, permisos etc.
  - Implementar API Rest para comunicación con frontend
  - Controlar la validación de datos
  - Controlar sesiones
- ElasticSearch
  - Se encarga de la búsqueda de los archivos, por nombre, tipo o contenido

##### Base de datos:

- PostgreSQL

##### Almacenamiento: 

- MinIO
  - Aqui guardaremos los archivos subidos por los usuarios

##### Frontend:

- Vue.js
  - Mostrar la interfaz tipo explorador de archivos
  - Comunicación con el backend vía API REST
