Base de datos:

```sql
-- =========================
-- TABLA USUARIO
-- =========================
CREATE TABLE usuario (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- almacenar hash
    foto_perfil TEXT,                -- URL de MinIO
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()  -- fecha de creación de la cuenta
);

-- =========================
-- TABLA CARPETA
-- =========================
CREATE TABLE carpeta (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    parent_id INT REFERENCES carpeta(id) ON DELETE CASCADE,  -- NULL permitido para carpetas raíz
    usuario_id INT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    UNIQUE (usuario_id, parent_id, nombre)  -- evita carpetas duplicadas en el mismo nivel
);

-- =========================
-- TABLA ARCHIVO
-- =========================
CREATE TABLE archivo (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    ruta_minio TEXT NOT NULL,            -- URL o path en MinIO
    carpeta_id INT NOT NULL REFERENCES carpeta(id) ON DELETE CASCADE,
    usuario_id INT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    
    -- Metadatos flexibles
    metadatos JSONB,
    
    -- Tipo de archivo (mime type)
    tipo_archivo VARCHAR(20) NOT NULL,
    
    -- Favoritos
    favorito BOOLEAN DEFAULT FALSE,
    
    -- Papelera
    eliminado BOOLEAN DEFAULT FALSE,
    fecha_eliminacion TIMESTAMP,
    
    -- Tamaño y fechas
    tamaño BIGINT NOT NULL,               -- tamaño en bytes
    fecha_subida TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    
    -- Evita archivos duplicados en la misma carpeta
    UNIQUE (carpeta_id, nombre)
);

-- =========================
-- ÍNDICES RECOMENDADOS
-- =========================
-- Para listar rápido los archivos de un usuario
CREATE INDEX idx_archivo_usuario ON archivo(usuario_id);

-- Para listar archivos dentro de una carpeta
CREATE INDEX idx_archivo_carpeta ON archivo(carpeta_id);

-- Para filtrar archivos en papelera
CREATE INDEX idx_archivo_eliminado ON archivo(eliminado);
```

Posibles tablas a mayores:

## 1️⃣ Seguridad

- **Hash seguro de la contraseña**: aunque lo indicaste, asegúrate de usar un algoritmo fuerte como **BCrypt o Argon2**.
- **Tokens de verificación / recuperación de contraseña**: si quieres funcionalidad de “olvidé mi contraseña” o verificación de email, necesitarás una tabla adicional:

```sql
CREATE TABLE usuario_token (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL,  -- ejemplo: 'recuperacion', 'verificacion'
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_expiracion TIMESTAMP NOT NULL
);
```

------

## 2️⃣ Control de auditoría (opcional)

- Guardar **quién modificó qué y cuándo**, útil si tu sistema tendrá logs de actividad:

```sql
CREATE TABLE archivo_auditoria (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    archivo_id INT NOT NULL REFERENCES archivo(id) ON DELETE CASCADE,
    usuario_id INT NOT NULL REFERENCES usuario(id),
    accion VARCHAR(20) NOT NULL,  -- ejemplo: 'crear', 'modificar', 'eliminar'
    fecha TIMESTAMP DEFAULT NOW(),
    detalle JSONB
);
```

------

## 3️⃣ Optimización de búsqueda con PostgreSQL (aunque uses ElasticSearch)

- Para consultas muy rápidas dentro de filtros (ej. listar archivos por usuario y carpeta), podrías usar **índices compuestos**:

```sql
CREATE INDEX idx_archivo_usuario_carpeta ON archivo(usuario_id, carpeta_id);
CREATE INDEX idx_archivo_usuario_eliminado ON archivo(usuario_id, eliminado);
```

- Así, si haces queries como:

```sql
SELECT * FROM archivo WHERE usuario_id = 10 AND carpeta_id = 5;
SELECT * FROM archivo WHERE usuario_id = 10 AND eliminado = TRUE;
```

- Se aceleran muchísimo.

------

## 4️⃣ Consideraciones de escalabilidad

- **Tamaños de archivos grandes**: `BIGINT` ya cubre hasta TB, perfecto.
- **MinIO**: asegúrate de que los buckets y objetos tengan nombres únicos o rutas que incluyan `usuario_id` o `UUID`, para evitar colisiones.
- **ElasticSearch**: cuando indexas archivos, incluye campos como `nombre`, `tipo_archivo`, `favorito`, `metadatos`, `fecha_subida` → así las búsquedas serán completas y rápidas.

------

## 5️⃣ Extras opcionales

- **Campos de status**: por ejemplo, `activo BOOLEAN DEFAULT TRUE` en `usuario` para bloquear cuentas.
- **Tags / categorías**: si quieres permitir etiquetar archivos, podrías crear una tabla de relaciones `archivo_tag`.
- **Versionado de archivos**: si quieres que un archivo pueda tener varias versiones, sería otra tabla `archivo_version` vinculada a `archivo`.

------

💡 **En resumen**:

Tu esquema ya cubre **lo esencial y casi todo lo que necesitas**. Mis sugerencias son **extras para mejorar seguridad, auditoría y rendimiento en consultas complejas**, pero no son estrictamente necesarias si tu MVP solo necesita subir, organizar y buscar archivos vía ElasticSearch.

------

Si quieres, puedo hacerte una **versión “full production ready”** de tu base de datos con estas mejoras integradas, lista para escalar y auditar archivos, usuarios y acciones.

¿Quieres que haga esa versión?