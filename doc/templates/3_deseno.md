# Deseño

## Esquema (boceto ou wireframe).

![](../img/Mockup%20-%20Deseño.png)

## Identidade visual 

La aplicación tendrá un  estilo retro y minimalista inspirado en interfaces clásicas de Mac OS y antiguos exploradores de archivos, pero adaptado a estándares actuales de usabilidad y legibilidad.

- **Tipografía**: Press Start 2P, VT323, monospace

- **Paleta de colores:**

  - Los colores principales serán el blanco, el gris y el negro.

  - Opcionalmente se podrán añadir otros colores como por ejemplo el azul, para realzar ciertos elementos y dar un estilo moderno.

- **Estilo general**:

  - Ventanas y paneles con bordes simples y esquinas ligeramente redondeadas.
  - Íconos claros y minimalistas, inspirados en pixel art, pero adaptados a resoluciones actuales.
  - Uso de espacios en blanco generoso para mejorar la legibilidad y la navegación.
  - Botones y elementos interactivos con feedback visual

## Diagrama de Bases de Datos

##### Base de datos:

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
```

##### Diagrama de base de datos:

![](../img/Diagrama%20de%20base%20de%20datos.png)