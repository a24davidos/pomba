## 📝 Apuntes: Instalación en Entrypoint vs. Dockerfile

### 💡 El Concepto
En lugar de "quemar" las librerías dentro de la imagen de Docker durante la construcción (`build`), las instalamos justo cuando el contenedor se enciende (`runtime`).

---

### ✅ Ventajas (Por qué hacerlo así en Desarrollo)

1. **Agilidad Total ("Hot-Reload" de Librerías):**
   * **El problema:** Si instalas en el `Dockerfile`, cada vez que añades una librería al `requirements.txt` tienes que hacer un `docker compose build`, lo cual es lento y reconstruye capas.
   * **La solución:** Al estar en el `entrypoint`, solo editas el archivo `.txt` y haces `make up`. El contenedor arranca, detecta el cambio e instala solo lo nuevo. **Ahorras minutos de espera.**

2. **Imagen "Limpia" y Ligera:**
   * La imagen que creas no pesa casi nada porque no contiene las librerías de Python. Es solo una "caja vacía" con Python instalado. Esto hace que subir o bajar la imagen de un repositorio sea instantáneo.

3. **Transparencia para el Desarrollador:**
   * Alguien que no sepa de Docker puede trabajar en tu proyecto. Solo necesita saber que el `requirements.txt` es la fuente de la verdad. No necesita aprender comandos complejos de construcción de imágenes.

4. **Persistencia con Volúmenes:**
   * Si usas volúmenes para la carpeta de librerías de Python (site-packages), una vez instaladas, no se pierden aunque apagues el contenedor. El `pip install` del entrypoint simplemente dirá "Requirement already satisfied" y arrancará en un segundo.

---

### ⚠️ Desventajas (Por qué NO hacerlo así en Producción)

1. **Dependencia de Internet:**
   * Si el servidor donde vas a desplegar no tiene internet o PyPI (el servidor de Python) está caído, el contenedor **no arrancará** porque no puede descargar las librerías.
2. **Inconsistencia:**
   * En producción quieres que el contenedor sea una "piedra": que nunca cambie. Si instalas al arrancar, corres el riesgo de que se instale una versión ligeramente distinta que rompa algo.
3. **Arranque en frío lento:**
   * La primera vez que despliegues en un servidor nuevo, el arranque tardará varios minutos mientras descarga todo.

---

### 🚀 Resumen de Estrategia

* **En el Arquetipo de Desarrollo:** Usamos el **Entrypoint**. Priorizamos la **comodidad y la rapidez** al añadir nuevas herramientas.
* **En el Arquetipo de Producción:** Usamos el **Dockerfile**. Priorizamos la **seguridad, la velocidad de despliegue y la estabilidad**.

---

### 🛠️ ¿Cómo se ve el comando en el `entrypoint.sh`?

Para que sea eficiente, tu script suele tener algo así:

```bash
# Instala solo lo que falte o se haya actualizado
pip install --no-cache-dir -r requirements.txt

# Luego lanza el servidor
python manage.py runserver 0.0.0.0:8000
```
