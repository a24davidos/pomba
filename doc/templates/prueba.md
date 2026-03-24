```sql
CREATE TABLE usuario (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  
    foto_perfil TEXT,                
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE carpeta (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    parent_id INT REFERENCES carpeta(id) ON DELETE CASCADE,  
    usuario_id INT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    UNIQUE (usuario_id, parent_id, nombre)
);

CREATE TABLE archivo (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    ruta_minio TEXT NOT NULL,            
    carpeta_id INT NOT NULL REFERENCES carpeta(id) ON DELETE CASCADE,
    usuario_id INT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    metadatos JSONB,
    tipo_archivo VARCHAR(20) NOT NULL,
    favorito BOOLEAN DEFAULT FALSE,
    eliminado BOOLEAN DEFAULT FALSE,
    fecha_eliminacion TIMESTAMP,
    tamaño BIGINT NOT NULL,
    fecha_subida TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
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

