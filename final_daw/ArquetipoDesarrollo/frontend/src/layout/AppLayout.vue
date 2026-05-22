<template>
  <div class="grid grid-cols-1 lg:grid-cols-[260px_1fr] grid-rows-[64px_1fr] min-h-screen w-full bg-surface-100 dark:bg-surface-950 gap-y-2 pt-2">

    <!-- TOPBAR -->
    <header class="col-span-1 lg:col-span-2 flex gap-2 items-center px-6 z-10">

      <!-- LOGO -->
      <div class="flex items-center lg:w-59 shrink-0">
        <div class="w-9 h-9 bg-primary rounded-lg flex items-center justify-center">
          <i class="pi pi-cloud text-primary-contrast text-lg"></i>
        </div>
      </div>

      <!-- BUSCADOR -->
      <div class="flex-1 flex justify-start ml-1">
        <div class="w-full max-w-4xl">
          <IconField class="w-full group">
            <InputIcon>
              <i class="pi pi-search text-surface-500 group-focus-within:text-surface-900 dark:group-focus-within:text-surface-0 transition-colors duration-200" />
            </InputIcon>
            <InputText
              placeholder="Buscar"
              class="w-full py-3 px-12 border-none
                    rounded-3xl transition-all duration-200
                    bg-surface-150 dark:bg-surface-800
                    hover:bg-surface-200 dark:hover:bg-surface-700
                    focus:bg-surface-0 dark:focus:bg-surface-900
                    focus:shadow-[0_1px_1px_0_rgba(65,69,73,.3),0_1px_3px_1px_rgba(65,69,73,.15)]
                    dark:focus:shadow-[0_1px_3px_rgba(0,0,0,.5)]"
            />
          </IconField>
        </div>
      </div>

      <!-- USUARIO Y TOGGLE -->
      <div class="flex items-center gap-3 shrink-0">
        <ThemeToggle />

        <!-- Botón de avatar -->
        <button
          class="w-9 h-9 rounded-full shrink-0 p-0 border-0 bg-transparent focus:outline-none cursor-pointer"
          style="line-height: 0;"
          @click="toggle"
          aria-label="Menú de usuario"
        >
          <div
            class="w-full h-full rounded-full overflow-hidden ring-2 ring-transparent hover:ring-primary transition-all duration-200 bg-surface-200 dark:bg-surface-700 flex items-center justify-center"
          >
            <img
              v-if="perfil.foto_perfil_url"
              :src="perfil.foto_perfil_url"
              alt="Avatar"
              class="w-full h-full object-cover block pointer-events-none"
            />
            <span
              v-else-if="perfil.nombre"
              class="text-sm font-semibold text-surface-600 dark:text-surface-300 select-none pointer-events-none leading-none"
            >
              {{ perfil.nombre.charAt(0).toUpperCase() }}
            </span>
            <i v-else class="pi pi-user text-surface-500 text-sm pointer-events-none" />
          </div>
        </button>

        <Menu ref="menu" :model="opcionesMenu" popup />
      </div>
    </header>

    <!-- SIDEBAR -->
    <aside class="hidden lg:block p-3">
      <Sidebar />
    </aside>

    <!-- MAIN -->
    <main class="p-6 overflow-auto bg-surface-0 dark:bg-surface-900 rounded-2xl ml-3 mr-3">
      <router-view />
    </main>

  </div>

  <!-- MODAL DE CONFIGURACIÓN -->
  <SettingsModal
    v-model="mostrarAjustes"
    :profile="perfil"
    @profile-updated="alActualizarPerfil"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authService } from '@/api/auth'
import { servicioUsuario } from '@/api/users'
import { useRouter } from 'vue-router'
import SettingsModal from '@/components/SettingsModal.vue'

const router = useRouter()

// Perfil del usuario autenticado
const perfil = ref({
  nombre: '',
  apellidos: '',
  email: '',
  foto_perfil_url: null,
})

const cargarPerfil = async () => {
  try {
    const datos = await servicioUsuario.obtenerPerfil()
    perfil.value = { ...datos }
  } catch {
    // Si falla, dejamos los valores vacíos sin bloquear la UI
  }
}

onMounted(cargarPerfil)

// Menú contextual
const menu = ref()
const mostrarAjustes = ref(false)

const opcionesMenu = ref([
  {
    label: 'Configuración',
    icon: 'pi pi-cog',
    command: () => { mostrarAjustes.value = true },
  },
  { separator: true },
  {
    label: 'Cerrar sesión',
    icon: 'pi pi-sign-out',
    command: () => cerrarSesion(),
  },
])

const toggle = (evento) => {
  menu.value.toggle(evento)
}

const cerrarSesion = () => {
  authService.logout()
  router.push('/')
}

// Actualizar perfil local cuando el modal confirma cambios
const alActualizarPerfil = (actualizado) => {
  perfil.value = { ...perfil.value, ...actualizado }
}
</script>
