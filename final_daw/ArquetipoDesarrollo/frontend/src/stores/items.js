import { defineStore } from 'pinia'
import api from '@/api/api'

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    breadcrumb: [],
    loading: false,
    currentParams: {},
    loadToken: 0,
    ui: {
      modal: {
        open: false,
        name: null,
        payload: null,
      },
    },
  }),

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

    async marcarFavoritos(ids = []) {
      try {
        await api.post('items/favorito/', { ids })
      } catch (error) {
        console.error('Error marcando favoritos:', error)
      }
    },

    // --- PAPELERA ---

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
  },
})