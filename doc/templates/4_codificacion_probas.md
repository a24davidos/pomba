# URL da páxina web

# Deseño dos prototipos 

## Prototipo 1
### Data de entrega: 21 de abril de 2026
### Funcionalidades implementadas:
- Conexión entre Django e Vue.js
- API REST para rexistro e autenticación de usuarios
- Endpoint de logout
### Observacións: 
Nesta primeira quincena centreime en establecer as bases do proxecto: a conexión entre o backend en Django e o frontend en Vue.js, e a creación da API para xestionar o login, o rexistro e o logout de usuarios. De momento as probas fíxenas a través da consola e de Postman, xa que aínda non hai interface gráfica implementada. O obxectivo para os próximos días é deixar todo rematado para a reunión do venres e definir os novos obxectivos para a seguinte quincena.
### Innovación: 
A separación entre backend e frontend dende o inicio facilita o desenvolvemento e senta as bases para ter unha arquitectura escalable e desacoplada.

## Prototipo 2
### Data de entrega: 5 de maio de 2026
### Funcionalidades implementadas:
- Integración de PrimeVue e Tailwind para dar coherencia visual á aplicación
- Toggle de tema claro/escuro
- Login e logout con deseño responsive
- Layout principal da aplicación
### Observacións: 
Nesta quincena traballei principalmente na GUI e na estrutura da aplicación. Durante as probas decateime de que tiña unha versión moi antiga de Garage S3, polo que actualiceino a unha versión máis actual. Tamén subín a versión de Node e baixei as versións de Kibana e Elasticsearch para resolver incompatibilidades. Estes problemas, xunto coas dificultades para crear un script de automatización do despregamento de Garage, ralentizáronme bastante. Ademais, debido á ponte non avancei tanto como me gustaría. Para a seguinte quincena o plan é engadir as táboas do sistema de ficheiros e implementar as primeiras interaccións reais, como subir e eliminar arquivos, empregando a librería de DataTables.
### Innovación: 
A integración de PrimeVue xunto con Tailwind permite manter unha coherencia visual sólida en toda a interface, reducindo a necesidade de escribir estilos personalizados e facilitando a escalabilidade do frontend.

## Prototipo 3
### Data de entrega: 19 de maio de 2026
### Funcionalidades implementadas:
- Sistema completo de cartafoles (creación, renomeado, eliminación e navegación xerárquica)
- Subida de ficheiros e almacenamento en Garage S3 con URLs pre-asinadas
- Papeleira con recuperación de contidos eliminados
- Soft delete  de ficheiros e cartafoles
- Marcado de cartafoles/arquivo como favoritos
### Observacións:
Nesta quincena avancei considerablemente nas funcionalidades do xestor de ficheiros. O sistema de cartafoles quedou completamente operativo, e a integración con Garage S3 para a subida e almacenamento de arquivos funciona correctamente. Tamén implementei a lóxica de soft delete, que permite recuperar contidos dende a papeleira antes de que sexan eliminados de forma definitiva. Para as seguintes semanas o obxectivo é introducir Elasticsearch para indexar metadatos e implementar as funcionalidades básicas restantes dun xestor de ficheiros completo.
### Innovación: 
O uso de soft delete en lugar dun borrado directo aporta robustez ao sistema, permitindo unha papeleira funcional similar á que ofrecen solucións como Google Drive ou Dropbox. O sistema de favoritos mellora a navegación para usuarios con gran volume de arquivos, evitando ter que percorrer a xerarquía de cartafoles cada vez.

## Prototipo Final
### Data de entrega: 2 de xuño de 2026
### Funcionalidades implementadas:
- Autenticación con JWT (login e rexistro)
- Xestión de ficheiros: subida, descarga, eliminación e organización en cartafoles
- Clasificación automática por tipo MIME
- Previsualización de arquivos (audio, PDF e imaxes)
- Control de versións de ficheiros (especialmente audio)
- Búsqueda de ficheiros con Elasticsearch
- Almacenamento en obxecto S3 compatible (Garage) con URLs pre-asinadas
- Documentación da API xerada con drf-spectacular
- Interface en Vue.js con tema claro/escuro
### Observacións: 
O desenvolvemento seguiu unha arquitectura desacoplada con backend en Django REST Framework e frontend en Vue.js, contenerizados con Docker. Empregouse PostgreSQL como base de datos relacional e Garage como almacenamento de obxectos compatible con S3.
### Innovación: 
Sistema de control de versións aplicado a ficheiros de audio, orientado a músicos, que permite comparar distintas versións dunha mesma canción. Integración dun motor de busca con ElasticSearch, que me permite indexar ficheiros e ter un buscador con integración de metadatos.




