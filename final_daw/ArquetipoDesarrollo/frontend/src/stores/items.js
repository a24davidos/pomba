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
    // Derivados del array de notificaciones (usados en el template)
    descargando: (state) =>
      state.notificaciones.some((n) => n.id === 'descargar' && n.tipo === 'cargando'),
  },

  actions: {

    // MODALS

    abrirModal(name, payload = null) {
      this.ui.modal.open = true
      this.ui.modal.name = name
      this.ui.modal.payload = payload
    },

    cerrarModal() {
      this.ui.modal.open = false
      this.ui.modal.name = null
      this.ui.modal.payload = null
    },

    // NOTIFICACIONES
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

    async subirArchivo(formData) {
      this.agregarNotificacion({
        id: 'subir',
        tipo: 'cargando',
        mensaje: 'Subiendo archivo…',
        icono: 'pi-upload',
        severidad: 'neutro',
      })
      try {
        await api.post('items/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        await this.cargarItems(this.currentParams)
      } catch (error) {
        console.error('Error subiendo archivo:', error)
      } finally {
        this.eliminarNotificacion('subir')
      }
    },

    async renombrarItem(id, nombre) {
      try {
        await api.post(`items/${id}/renombrar/`, { nombre })
        this.agregarNotificacion({
          id: 'renombrar',
          tipo: 'exito',
          mensaje: 'Elemento renombrado',
          icono: 'pi-pencil',
          severidad: 'exito',
        })
      } catch (error) {
        console.error('Error renombrando item:', error)
      }
    },

    actualizarItemsLocal(ids, cambios) {
      const set = new Set(ids)
      this.items = this.items.map((item) =>
        set.has(item.id) ? { ...item, ...cambios } : item
      )
    },

    async marcarFavoritos(ids = []) {
      try {
        const response = await api.post('items/favorito/', { ids })
        this.actualizarItemsLocal(ids, { favorito: response.data.favorito })
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

      // Un solo archivo  presigned URL directa (instantáneo, sin notificación)
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

      // Carpeta o selección múltiple  ZIP generado en Django
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
