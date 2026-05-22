import { defineStore } from 'pinia'
import api from '@/api/api'

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    breadcrumb: [],
    loading: false,
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
  },

  actions: {
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

    async crearCarpeta(data) {
      try {
        await api.post('items/', data)
      } catch (error) {
        console.error('Error creando carpeta:', error)
      }
    },

    async subirArchivo(formData) {
      try {
        await api.post('items/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        await this.cargarItems(this.currentParams)
      } catch (error) {
        console.error('Error subiendo archivo:', error)
      }
    },

    async renombrarItem(id, nombre) {
      try {
        await api.post(`items/${id}/renombrar/`, { nombre })
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
        // Actualizamos local sin recargar
        this.actualizarItemsLocal(ids, { favorito: response.data.favorito })
        this.limpiarSeleccion()
      } catch (error) {
        console.error('Error marcando favoritos:', error)
      }
    },

    async eliminarItems(ids = []) {
      try {
        await api.post('items/trash/', { ids })
      } catch (error) {
        console.error('Error enviando a papelera:', error)
      }
    },

    async eliminarDefinitivamente(ids = []) {
      try {
        await api.delete('items/eliminar_definitivo/', { data: { ids } })
      } catch (error) {
        console.error('Error eliminando definitivamente:', error)
      }
    },

    async restaurarItems(ids = []) {
      try {
        await api.post('items/restaurar/', { ids })
      } catch (error) {
        console.error('Error restaurando items:', error)
      }
    },

    async restaurarPapelera() {
      try {
        await api.post('items/restaurar_papelera/')
        await this.cargarItems(this.currentParams)
      } catch (error) {
        console.error('Error restaurando papelera:', error)
      }
    },

    async vaciarPapelera() {
      try {
        await api.post('items/vaciar_papelera/')
        await this.cargarItems(this.currentParams)
      } catch (error) {
        console.error('Error vaciando papelera:', error)
      }
    },

    // --- SELECCIÓN ---

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