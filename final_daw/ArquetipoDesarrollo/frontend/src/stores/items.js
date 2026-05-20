import { defineStore } from 'pinia'
import api from '@/api/api'

export const useItemsStore = defineStore('items', {
    state: () => ({
        items: [],
        loading: false
    }),

    actions: {
        async cargarItems(params = {}) {
            this.loading = true

            try {
                const res = await api.get('items/', { params })
                this.items = res.data.items
            } finally {
                this.loading = false
            }
        },

        async vaciarPapelera() {
            await api.post('items/vaciar_papelera/')
            await this.cargarItems({ papelera: true })
        }
    }
})