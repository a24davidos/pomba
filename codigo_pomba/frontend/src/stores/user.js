import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { apiUsers } from '@/api/users'

export const useUserStore = defineStore('user', () => {
  const perfil = ref({ nombre: '', apellidos: '', email: '', foto_perfil_url: null })

  const inicial = computed(() =>
    perfil.value.nombre ? perfil.value.nombre.charAt(0).toUpperCase() : null
  )

  async function cargarPerfil() {
    try {
      const datos = await apiUsers.obtenerPerfil()
      perfil.value = { ...datos }
      if (datos.tema) {
        const dark = datos.tema === 'oscuro'
        document.documentElement.classList.toggle('dark', dark)
        localStorage.setItem('theme', datos.tema)
      }
    } catch {}
  }

  //Lo utilizamos para guardar localmente sin tener que recargar la página entera 
  function actualizarPerfil(datos) {
    perfil.value = { ...perfil.value, ...datos }
  }

  return { perfil, inicial, cargarPerfil, actualizarPerfil }
})
