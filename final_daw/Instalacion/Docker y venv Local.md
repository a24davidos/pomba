# Guía: Entorno de Desarrollo Híbrido (Docker + venv Local)

Esta configuración permite que el código de tu backend (Django) corra dentro de **Docker**, pero que las librerías vivan en una carpeta de tu **Mac**. Esto une lo mejor de los dos mundos: la estabilidad de Docker y la comodidad del autocompletado en local.

## 1. El Problema: El "Aislamiento" de Docker

Normalmente, cuando instalas librerías dentro de un contenedor Docker, estas son "invisibles" para tu editor de código (VS Code/PyCharm) en el Mac.

- **Resultado:** El código funciona en el navegador, pero tu editor llena todo de líneas rojas (`Import "django" could not be resolved`) y no tienes autocompletado.

## 2. La Solución: El Volumen y el PYTHONPATH

Para solucionar esto, hemos creado un puente de comunicación:

### A. El Volumen (Sincronización de archivos)

En el `docker-compose.yml`, mapeamos la carpeta de nuestro ordenador al contenedor:

YAML

```
volumes:
  - ../backend:/app
```

Esto significa que cualquier librería que instales en la carpeta `backend/libraries` de tu Mac, aparecerá mágicamente dentro de la carpeta `/app/libraries` del contenedor.

### B. El PYTHONPATH (El mapa de búsqueda)

Aunque los archivos están dentro del contenedor, el Python de Docker no sabe que debe usarlos porque están en una ruta "no estándar". En lugar de modificar el código de Django, usamos una **Variable de Entorno**:

YAML

```
environment:
  - PYTHONPATH=/app/libraries/lib/python3.12/site-packages
```

**¿Qué hace esto?**

Le da una instrucción directa al intérprete de Python: *"Antes de empezar, añade esta carpeta a tu lista de búsqueda de librerías"*. Es el equivalente limpio y profesional a usar `sys.path.append()`, pero sin tocar una sola línea de código.

------

## 3. Ventajas de este Sistema

1. **Autocompletado Total (IntelliSense):** Como las librerías están físicamente en tu Mac, tu editor puede leerlas. Al escribir `models.`, el editor te sugerirá opciones porque "ve" el código de Django.
2. **Cero Modificación de Código:** No ensuciamos `manage.py` con rutas locales que podrían fallar en producción (servidores reales).
3. **Depuración Fácil:** Puedes abrir cualquier archivo de una librería (ej. el código fuente de Django) directamente en tu editor para entender errores.
4. **Portabilidad:** Si compartes el proyecto, cualquier persona con Docker tendrá exactamente las mismas versiones de librerías que tú, sin instalar nada en su sistema.

------

## 4. Flujo de Trabajo Diario

### Cómo instalar nuevas librerías

Para que la librería se instale correctamente para la arquitectura de Docker pero sea visible en tu Mac, usa este comando desde tu terminal:

Bash

```
docker exec django_backend pip install <nombre-libreria> --target=/app/libraries/lib/python3.12/site-packages
```

### Configuración del Editor (VS Code)

Para que el autocompletado sea perfecto:

1. Pulsa `Cmd + Shift + P`.
2. Busca **"Python: Select Interpreter"**.
3. Selecciona el ejecutable que está dentro de tu carpeta de librerías local.

------

## 5. Resumen Técnico para el Recuerdo

- **`sys.path`**: Lista interna de Python con las rutas de búsqueda.
- **`PYTHONPATH`**: Variable de entorno que alimenta a `sys.path` antes de que el programa arranque.
- **Volumen**: Sincroniza los archivos entre el Host (Mac) y el Guest (Docker).
- **Target**: Parámetro de pip para forzar la instalación en una carpeta específica del proyecto en lugar de en el sistema global.

> **Nota de David:** "Uso el PYTHONPATH en el compose para no tocar el manage.py. Así mantengo el código limpio y el contenedor sabe dónde buscar mis librerías compartidas".

---

### El "Antes" vs. el "Ahora"

**Antes (Sin el puente configurado):**

Para que Docker encontrara Django y tus archivos, probablemente tenías que ejecutar comandos pesados indicando la ruta completa del ejecutable de Python o de las librerías, algo tipo:

```
docker exec django_backend /app/libraries/bin/python manage.py migrate
```

**Ahora (Con PYTHONPATH y el volumen):**

Como el contenedor ya sabe de antemano dónde están las librerías gracias al `PYTHONPATH`, puedes usar el Python estándar del contenedor. Solo tienes que decir:

```
docker exec django_backend python manage.py migrate
```

### ¿Por qué ahora es así de corto?

1. **Reconocimiento automático:** Al poner la ruta en el `environment` del `docker-compose.yml`, Python ya tiene "cargado" el mapa de tus librerías en su memoria desde que arranca el contenedor.
2. **El comando `python` se vuelve inteligente:** Cuando escribes `python manage.py`, el intérprete busca `django` automáticamente en esa carpeta `/app/libraries/...` que le indicaste. No necesitas recordarle dónde está cada vez.
3. **Transparencia:** Para ti, es como si estuvieras trabajando en tu Mac de toda la vida, pero con la potencia de Docker por debajo.

### Un truco extra para tus apuntes (Alias)

Si quieres que sea aún más corto, como eres de los que les gusta la eficiencia, puedes añadir un **alias** en tu Mac (en tu archivo `.zshrc` o `.bash_profile`).

Si añades esto:

```
alias d-manage="docker exec django_backend python manage.py"
```

Entonces, para migrar, solo tendrías que escribir en tu terminal:

```
d-manage migrate
```

**En resumen:** Has simplificado la comunicación. Ya no tienes que darle la dirección completa a Python; ahora Python ya vive en esa dirección. ¿Has probado ya a lanzar un `migrate` o un `createsuperuser` para ver qué tal responde?