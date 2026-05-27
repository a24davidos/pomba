import axios from 'axios'
import { defineStore } from 'pinia'
import api from '@/api/api'

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    breadcrumb: [],
    loading: false,
    notificaciones: [],
    currentParams: {},
    loadToken: 0,
    queryBusqueda: '',

    seleccion: {
      ids: [],
      lastIndex: null,
    },

    ui: {
      modal: {
        open: false,
        name: null,
        payload: null,
      },
    },
  }),

  getters: {
    itemsSeleccionados(state) {
      const set = new Set(state.seleccion.ids)
      return state.items.filter((i) => set.has(i.id))
    },
    descargando: (state) =>
      state.notificaciones.some((n) => n.id === 'descargar' && n.tipo === 'cargando'),
  },

  actions: {

    // -------------------------------------------------------
    // MODALS
    // -------------------------------------------------------

    abrirModal(name, payload = null) {
      this.ui.modal.open = true
      this.ui.modal.name = name
      this.ui.modal.payload = payload
    },

    abrirModalRenombrar(item) {
      const objetivo = item ?? this.itemsSeleccionados[0]
      if (!objetivo) return
      this.abrirModal('renombrar', objetivo)
    },

    abrirModalMover(item) {
      const items = item ? [item] : this.itemsSeleccionados
      if (!items.length) return
      this.abrirModal('mover', { ids: items.map((i) => i.id) })
    },

    cerrarModal() {
      this.ui.modal.open = false
      this.ui.modal.name = null
      this.ui.modal.payload = null
    },

    // -------------------------------------------------------
    // NOTIFICACIONES
    // -------------------------------------------------------

    agregarNotificacion({ id, tipo, mensaje, icono, severidad = 'neutro' }) {
      this.eliminarNotificacion(id)
      this.notificaciones.push({ id, tipo, mensaje, icono, severidad, timerId: null })
      if (tipo === 'exito' || tipo === 'error') {
        const notif = this.notificaciones.find((n) => n.id === id)
        const secs = tipo === 'error' ? 5 : 3
        if (notif) notif.timerId = setTimeout(() => this.eliminarNotificacion(id), secs * 1000)
      }
    },

    actualizarNotificacion(id, cambios, autoCloseSeg = 3) {
      const notif = this.notificaciones.find((n) => n.id === id)
      if (!notif) return
      if (notif.timerId) clearTimeout(notif.timerId)
      Object.assign(notif, cambios)
      if (cambios.tipo === 'exito' || cambios.tipo === 'error') {
        const secs = cambios.tipo === 'error' ? 5 : autoCloseSeg
        notif.timerId = setTimeout(() => this.eliminarNotificacion(id), secs * 1000)
      }
    },

    eliminarNotificacion(id) {
      const idx = this.notificaciones.findIndex((n) => n.id === id)
      if (idx !== -1) {
        if (this.notificaciones[idx].timerId) clearTimeout(this.notificaciones[idx].timerId)
        this.notificaciones.splice(idx, 1)
      }
    },

    // -------------------------------------------------------
    // ITEMS — LECTURA
    // -------------------------------------------------------

    recargar() {
      return this.cargarItems(this.currentParams)
    },

    async cargarItems(params = {}) {
      const token = ++this.loadToken
      this.loading = true
      this.currentParams = { ...params }
      try {
        const response = await api.get('items/', { params })
        if (token !== this.loadToken) return
        this.items = response.data.items
        this.breadcrumb = response.data.breadcrumb || []
      } catch (error) {
        console.error('Error cargando items:', error)
      } finally {
        if (token === this.loadToken) this.loading = false
      }
    },

    async buscarItems(q) {
      this.loading = true
      this.queryBusqueda = q
      this.limpiarSeleccion()
      try {
        const response = await api.get('items/buscar/', { params: { q } })
        this.items = response.data.items
        this.breadcrumb = []
      } catch (error) {
        this.items = []
        console.error('Error en búsqueda:', error)
      } finally {
        this.loading = false
      }
    },

    // -------------------------------------------------------
    // ITEMS — ESCRITURA
    // -------------------------------------------------------

    async crearCarpeta(data) {
      try {
        await api.post('items/', data)
      } catch (error) {
        console.error('Error creando carpeta:', error)
      }
    },

    /**
     * Sube un único archivo usando el flujo presigned URL:
     * 1. Pide a Django una URL de subida + key
     * 2. Hace PUT directo a Garage (sin pasar por Django)
     * 3. Confirma a Django para que registre el Item en BD
     */
    async _subirArchivoPresignado(file, padreId) {
      const mimeType = file.type || 'application/octet-stream'

      // Paso 1: obtener URL presignada
      const { data: { url_subida, key } } = await api.post('items/solicitar_subida/', {
        nombre: file.name,
        mime_type: mimeType,
      })

      // Paso 2: PUT directo al bucket (sin token JWT, la URL ya lleva la firma S3)
      await axios.put(url_subida, file, {
        headers: { 'Content-Type': mimeType },
      })

      // Paso 3: registrar en BD
      await api.post('items/confirmar_subida/', {
        nombre: file.name,
        key,
        padre: padreId,
        tamano_bytes: file.size,
        mime_type: mimeType,
      })
    },

    async subirArchivo(file, padreId = null) {
      this.agregarNotificacion({
        id: 'subir',
        tipo: 'cargando',
        mensaje: 'Subiendo archivo…',
        icono: 'pi-upload',
        severidad: 'neutro',
      })
      try {
        await this._subirArchivoPresignado(file, padreId)
        await this.cargarItems(this.currentParams)
      } catch (error) {
        console.error('Error subiendo archivo:', error?.response?.data ?? error)
      } finally {
        this.eliminarNotificacion('subir')
      }
    },

    // -------------------------------------------------------
    // SUBIDA DE CARPETA
    // -------------------------------------------------------

    _parsearEstructuraCarpeta(files) {
      // Ficheros del sistema que nunca deben subirse
      const IGNORADOS = new Set(['.DS_Store', 'Thumbs.db', 'desktop.ini', '.localized'])

      const carpetas = new Set()
      const archivos = []

      for (const file of files) {
        if (IGNORADOS.has(file.name)) continue

        // webkitRelativePath siempre empieza con el nombre de la carpeta raíz
        const partes = file.webkitRelativePath.split('/')

        // Registrar todas las carpetas intermedias (excluye el nombre del archivo)
        for (let i = 1; i < partes.length; i++) {
          carpetas.add(partes.slice(0, i).join('/'))
        }

        archivos.push({
          file,
          rutaRelativa: file.webkitRelativePath,
        })
      }

      // Ordenar por profundidad para que el backend siempre reciba el padre antes que el hijo
      const carpetasOrdenadas = Array.from(carpetas).sort(
        (a, b) => a.split('/').length - b.split('/').length
      )

      return { carpetasOrdenadas, archivos }
    },

    async subirCarpeta(files, padreId = null) {
      if (!files.length) return

      const NOTIF_ID = 'subir-carpeta'
      const LOTE = 3

      this.agregarNotificacion({
        id: NOTIF_ID,
        tipo: 'cargando',
        mensaje: 'Preparando estructura de carpetas…',
        icono: 'pi-folder',
        severidad: 'neutro',
      })

      try {
        const { carpetasOrdenadas, archivos } = this._parsearEstructuraCarpeta(files)

        // 1. Crear árbol de carpetas 
        this.actualizarNotificacion(NOTIF_ID, {
          mensaje: `Creando ${carpetasOrdenadas.length} carpeta${carpetasOrdenadas.length !== 1 ? 's' : ''}…`,
        })

        const { data } = await api.post('items/crear_arbol_carpetas/', {
          rutas: carpetasOrdenadas,
          padre: padreId,
        })

        // mapa: { "MiCarpeta": 12, "MiCarpeta/sub": 34, ... }
        const mapa = data.mapa

        // 2. Subir archivos en lotes 
        let subidos = 0
        let fallidos = 0
        const total = archivos.length

        this.actualizarNotificacion(NOTIF_ID, {
          mensaje: `Subiendo archivos… 0 / ${total}`,
        })

        for (let i = 0; i < archivos.length; i += LOTE) {
          const lote = archivos.slice(i, i + LOTE)

          const resultados = await Promise.allSettled(
            lote.map(async ({ file, rutaRelativa }) => {
              const partes = rutaRelativa.split('/')
              const rutaPadre = partes.slice(0, -1).join('/')
              const padreArchivo = mapa[rutaPadre] ?? padreId
              await this._subirArchivoPresignado(file, padreArchivo)
            })
          )

          for (const resultado of resultados) {
            if (resultado.status === 'fulfilled') {
              subidos++
            } else {
              fallidos++
              console.error('Error subiendo archivo:', resultado.reason?.response?.data ?? resultado.reason)
            }
          }

          this.actualizarNotificacion(NOTIF_ID, {
            mensaje: `Subiendo archivos… ${subidos + fallidos} / ${total}`,
          })
        }

        if (fallidos === 0) {
          this.actualizarNotificacion(
            NOTIF_ID,
            {
              tipo: 'exito',
              mensaje: `Carpeta subida correctamente (${subidos} archivo${subidos !== 1 ? 's' : ''})`,
              icono: 'pi-check',
              severidad: 'exito',
            },
            3,
          )
        } else {
          this.actualizarNotificacion(
            NOTIF_ID,
            {
              tipo: 'error',
              mensaje: `${subidos} subidos, ${fallidos} fallaron`,
              icono: 'pi-exclamation-triangle',
              severidad: 'advertencia',
            },
            5,
          )
        }

      } catch (error) {
        console.error('Error subiendo carpeta:', error?.response?.data ?? error)
        this.actualizarNotificacion(
          NOTIF_ID,
          {
            tipo: 'error',
            mensaje: 'Error al crear la estructura de carpetas',
            icono: 'pi-times',
            severidad: 'peligro',
          },
          5,
        )
      } finally {
        await this.cargarItems(this.currentParams)
      }
    },

    async renombrarItem(id, nombre) {
      try {
        await api.post(`items/${id}/renombrar/`, { nombre })
        this.actualizarItemsLocal([id], { nombre })
        this.agregarNotificacion({
          id: 'renombrar',
          tipo: 'exito',
          mensaje: 'Elemento renombrado',
          icono: 'pi-pencil',
          severidad: 'exito',
        })
        return true
      } catch (error) {
        const mensaje = error?.response?.data?.detail || 'No se pudo renombrar el elemento'
        this.agregarNotificacion({
          id: 'renombrar',
          tipo: 'error',
          mensaje,
          icono: 'pi-times',
        })
        return false
      }
    },

    actualizarItemsLocal(ids, cambios) {
      const set = new Set(ids)
      this.items = this.items.map((item) =>
        set.has(item.id) ? { ...item, ...cambios } : item
      )
    },

    async moverItems(ids, destinoId) {
      try {
        await api.post('items/mover/', { ids, destino: destinoId })
        this.items = this.items.filter((item) => !ids.includes(item.id))
        this.limpiarSeleccion()
        this.agregarNotificacion({
          id: 'mover',
          tipo: 'exito',
          mensaje: ids.length === 1 ? 'Elemento movido' : `${ids.length} elementos movidos`,
          icono: 'pi-arrow-right',
          severidad: 'exito',
        })
      } catch (error) {
        this.agregarNotificacion({
          id: 'mover',
          tipo: 'error',
          mensaje: 'No se pudo mover el elemento',
          icono: 'pi-times',
        })
        console.error('Error moviendo items:', error)
      }
    },

    async marcarFavoritos(ids = []) {
      try {
        const response = await api.post('items/favorito/', { ids })
        const nuevoFavorito = response.data.favorito
        if (!nuevoFavorito && this.currentParams.favorito === 'true') {
          this.items = this.items.filter((item) => !ids.includes(item.id))
        } else {
          this.actualizarItemsLocal(ids, { favorito: nuevoFavorito })
        }
        this.limpiarSeleccion()
      } catch (error) {
        console.error('Error marcando favoritos:', error)
      }
    },

    // -------------------------------------------------------
    // ITEMS — PAPELERA Y ELIMINACIÓN
    // -------------------------------------------------------

    async eliminarItems(ids = []) {
      try {
        await api.post('items/trash/', { ids })
        this.items = this.items.filter((item) => !ids.includes(item.id))
        this.limpiarSeleccion()
        this.agregarNotificacion({
          id: 'papelera',
          tipo: 'exito',
          mensaje: 'Movido a la papelera',
          icono: 'pi-trash',
          severidad: 'advertencia',
        })
      } catch (error) {
        console.error('Error enviando a papelera:', error)
      }
    },

    async eliminarDefinitivamente(ids = []) {
      this.agregarNotificacion({
        id: 'eliminar',
        tipo: 'cargando',
        mensaje: 'Eliminando archivos de S3…',
        icono: 'pi-times-circle',
        severidad: 'peligro',
      })
      try {
        await api.delete('items/eliminar_definitivo/', { data: { ids } })
        this.items = this.items.filter((item) => !ids.includes(item.id))
        this.limpiarSeleccion()
        this.actualizarNotificacion(
          'eliminar',
          { tipo: 'exito', mensaje: 'Eliminado definitivamente', icono: 'pi-check-circle' },
          3,
        )
      } catch (error) {
        this.actualizarNotificacion('eliminar', { tipo: 'error', mensaje: 'Error al eliminar' }, 5)
        console.error('Error eliminando definitivamente:', error)
      }
    },

    async restaurarItems(ids = []) {
      try {
        await api.post('items/restaurar/', { ids })
        this.items = this.items.filter((item) => !ids.includes(item.id))
        this.limpiarSeleccion()
        this.agregarNotificacion({
          id: 'restaurar',
          tipo: 'exito',
          mensaje: 'Elemento restaurado',
          icono: 'pi-replay',
          severidad: 'exito',
        })
      } catch (error) {
        console.error('Error restaurando items:', error)
      }
    },

    async restaurarPapelera() {
      try {
        await api.post('items/restaurar_papelera/')
        await this.cargarItems(this.currentParams)
        this.agregarNotificacion({
          id: 'restaurar',
          tipo: 'exito',
          mensaje: 'Papelera restaurada',
          icono: 'pi-replay',
          severidad: 'exito',
        })
      } catch (error) {
        console.error('Error restaurando papelera:', error)
      }
    },

    async vaciarPapelera() {
      this.agregarNotificacion({
        id: 'vaciar-papelera',
        tipo: 'cargando',
        mensaje: 'Vaciando papelera…',
        icono: 'pi-trash',
        severidad: 'peligro',
      })
      try {
        await api.post('items/vaciar_papelera/')
        await this.cargarItems(this.currentParams)
        this.actualizarNotificacion(
          'vaciar-papelera',
          { tipo: 'exito', mensaje: 'Papelera vaciada', icono: 'pi-check-circle' },
          3,
        )
      } catch (error) {
        this.actualizarNotificacion(
          'vaciar-papelera',
          { tipo: 'error', mensaje: 'Error al vaciar la papelera' },
          5,
        )
        console.error('Error vaciando papelera:', error)
      }
    },

    // -------------------------------------------------------
    // DESCARGA
    // -------------------------------------------------------

    async descargarItems() {
      const seleccion = this.itemsSeleccionados
      if (!seleccion.length) return

      // Un solo archivo - presigned URL directa
      if (seleccion.length === 1 && seleccion[0].tipo === 'archivo') {
        try {
          const resp = await api.get(`items/${seleccion[0].id}/descargar_archivo/`)
          const a = document.createElement('a')
          a.href = resp.data.url
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
        } catch (error) {
          console.error('Error descargando archivo:', error)
        }
        return
      }

      // Carpeta o selección múltiple - ZIP generado en Django
      this.agregarNotificacion({
        id: 'descargar',
        tipo: 'cargando',
        mensaje: 'Comprimiendo archivos…',
        icono: 'pi-download',
        severidad: 'neutro',
      })
      try {
        const ids = seleccion.map((i) => i.id)
        const nombre = seleccion.length === 1 ? `${seleccion[0].nombre}.zip` : 'descarga.zip'

        const resp = await api.post('items/descargar/', { ids }, { responseType: 'blob' })

        const blobUrl = URL.createObjectURL(resp.data)
        const a = document.createElement('a')
        a.href = blobUrl
        a.download = nombre
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(blobUrl)
      } catch (error) {
        console.error('Error descargando ZIP:', error)
      } finally {
        this.eliminarNotificacion('descargar')
      }
    },

    // -------------------------------------------------------
    // SELECCIÓN
    // -------------------------------------------------------

    seleccionar(item, index) {
      this.seleccion.ids = [item.id]
      this.seleccion.lastIndex = index
    },

    toggleSeleccion(item, index) {
      const ya = this.seleccion.ids.includes(item.id)
      if (ya) {
        this.seleccion.ids = this.seleccion.ids.filter((id) => id !== item.id)
      } else {
        this.seleccion.ids = [...this.seleccion.ids, item.id]
      }
      this.seleccion.lastIndex = index
    },

    seleccionarRango(index) {
      if (this.seleccion.lastIndex === null) return
      const desde = Math.min(this.seleccion.lastIndex, index)
      const hasta = Math.max(this.seleccion.lastIndex, index)
      const rango = this.items.slice(desde, hasta + 1).map((i) => i.id)
      const merged = new Set([...this.seleccion.ids, ...rango])
      this.seleccion.ids = [...merged]
    },

    limpiarSeleccion() {
      this.seleccion.ids = []
      this.seleccion.lastIndex = null
    },
  },
})
