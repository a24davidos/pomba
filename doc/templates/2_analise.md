# Análise: Requirimentos do sistema
## Tipos de usuarios

En la aplicación existirán 2 tipos de usuarios: 

##### Usuario anónimo:

- No tiene cuenta en el sistema
- Solo puede acceder a la página principal
- Puede registrarse en la aplicacion

##### Usuario registrado:

- Usuario con cuenta en el sistema
- Puede iniciar sesión
- Puede modificar su perfil
- Puede gestionar sus archivos
- Puede eliminar su cuenta

## Requirimentos

#### Requisitos funcionales: 

##### RF1. Gestión de usuarios

- RF1.1 La aplicación permitirá el registro de nuevos usuarios
- RF1.2 La aplicación permitirá a los usuarios iniciar sesión
- RF1.3 La aplicación permitirá a los usuarios cerrar sesión
- RF1.4 La aplicación permitirá a los usuarios modificar sus datos personales (nombre de usuario, correo electrónico y contraseña)
- RF1.5 La aplicación permitirá a los usuarios a subir una imagen de perfil
- RF1.6 La aplicación permitirá a los usuarios eliminar su cuenta

##### RF2. Gestión de carpetas

- RF2.1 La aplicación permitirá crear carpetas
- RF2.2 La aplicación permitirá crear subcarpetas dentro de otras carpetas 
- RF2.3 La aplicación permitirá renombrar carpetas
- RF2.4 La aplicación permitirá eliminar carpetas

**RF3. Gestión de archivos**

- RF3.1 La aplicación permitirá subir archivos
- RF3.2 La aplicación validará el tipo de archivos permitido (Inicialmente archivos TXT e imágenes JPEG)
- RF3.3 La aplicación validará el tamaño máximo de los archivos
- RF3.4 La aplicación guardará los metadatos de los archivos en la base de datos
- RF3.5 La aplicación guardará los archivos en MinIO
- RF3.6 La aplicación permitirá eliminar archivos
- RF3.7 La aplicación permitirá descargar archivos
- RF3.8 El sistema permitirá mover archivos entre carpetas del mismo usuario

##### RF4. Búsqueda

- RF4.1 La aplicación permitirá buscar archivos por nombre
- RF4.2 La aplicación permitirá buscar archivos por tipo
- RF4.3 La aplicación permitirá buscar archivos por contenido (Los archivos TXT)
- RF4.4 La aplicación permitirá buscar archivos por metadatos

##### RF5. Papelera

- RF5.1 La aplicación almacenará temporalmente los archivos eliminados
- RF5.2 La aplicación permitirá restaurar archivos eliminados
- RF5.3 La aplicación eliminará permanentemente los archivos tras un periodo determinado de 30 días

#### Requisitos no funcionales: 

##### RNF1. Seguridad

- RNF1.1 La aplicación almacenará las contraseñas de forma cifrada
- RNF1.2 La aplicación utilizará autenticación basada en sesiones
- RNF1.3 La aplicación validará todos los datos introducidos por el usuario
- RNF1.4 La aplicación restringirá el acceso a los datos de cada usuario

##### RNF2. Rendimiento

- RNF2.1 La aplicación deberá responder de forma rápida y eficiente durante la navegación y la subida de archivos

##### RNF3. Escalabilidad y mantenibilidad

- RNF3.1 El sistema estará dockerizado
- RNF3.2 La arquitectura permitirá ir añadiendo nuevas funcionalidades
- RNF3.3 La aplicación estará dividida en frontend y backend, comunicándose mediante API REST, lo que permitirá independencia entre la interfaz de usuario y la lógica del servidor

**RNF4. Usabilidad**

- RNF4.1 La interfaz será intuitiva y similar a un explorador de archivos
- RNF4.2 Los mensajes de error serán claros y comprensibles

**RNF5. Compatibilidad**

- RNF5.1 La aplicación será accesible y funcional en los navegadores web modernos, incluyendo Chrome, Firefox, Edge y Safari, garantizando que la interfaz de usuario se muestre correctamente
