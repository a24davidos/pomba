import { defineStore } from 'pinia'
import api from '@/api/api'

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    breadcrumb: [],
    loading: false,
    currentParams: {},
    loadToken: 0
  }),

  actions: {
    async cargarItems(params = {}) {
      const token = ++this.loadToken

      this.loading = true
      this.currentParams = { ...params }

      try {
        const response = await api.get('items/', { params })

        // Ignoramos respuestas viejas
        if (token !== this.loadToken) return

        this.items = response.data.items
        this.breadcrumb = response.data.breadcrumb || []
      } catch (error) {
        console.error('Error cargando items:', error)
      } finally {
        // Solo apagamos loading si esta sigue siendo la última carga
        if (token === this.loadToken) {
          this.loading = false
        }
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

    async restaurarPapelera(){
        try{
            await api.post('items/restaurar_papelera/')
            await this.cargarItems(this.currentParams)
        } catch (error){
            console.error("Error restaurando papelera:", error);
        }
    },

    async eliminarItems(ids = []) {
      try {
        await api.post('items/trash/', { ids })
      } catch (error) {
        console.error('Error eliminando items:', error)
      }
    },

    async marcarFavoritos(ids = []) {
      try {
        await api.post('items/favorito/', { ids })
      } catch (error) {
        console.error('Error marcando favoritos:', error)
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
          headers: { 'Content-Type': 'multipart/form-data' }
        })
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
    }
  }
})