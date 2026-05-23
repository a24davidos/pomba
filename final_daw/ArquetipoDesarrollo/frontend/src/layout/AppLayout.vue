<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/api/auth'
import { servicioUsuario } from '@/api/users'
import SettingsModal from '@/components/SettingsModal.vue'
import Sidebar from '@/components/Sidebar.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()

// ── Perfil ────────────────────────────────────────────────────────
const perfil = ref({ nombre: '', apellidos: '', email: '', foto_perfil_url: null })

const cargarPerfil = async () => {
  try {
    const datos = await servicioUsuario.obtenerPerfil()
    perfil.value = { ...datos }
  } catch {}
}

onMounted(cargarPerfil)

const inicial = computed(() =>
  perfil.value.nombre ? perfil.value.nombre.charAt(0).toUpperCase() : null
)

// ── Menú de usuario (solo desktop) ───────────────────────────────
const menuUsuario = ref()
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
    command: cerrarSesion,
  },
])

function toggleMenuUsuario(evento) {
  menuUsuario.value.toggle(evento)
}

function cerrarSesion() {
  authService.logout()
  router.push('/')
}

function alActualizarPerfil(actualizado) {
  perfil.value = { ...perfil.value, ...actualizado }
}

// ── Panel de usuario móvil ────────────────────────────────────────
const panelUsuarioMovil = ref(false)
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-[60px_1fr] lg:grid-cols-[260px_1fr] grid-rows-[64px_1fr] min-h-screen w-full bg-surface-100 dark:bg-surface-950 gap-y-2 pt-2">

    <!-- ── TOPBAR ───────────────────────────────────────────────── -->
    <!-- Sub-grid que espeja las mismas columnas del layout principal -->
    <header class="col-span-full grid grid-cols-1 sm:grid-cols-[60px_1fr] lg:grid-cols-[260px_1fr] items-center z-10">

      <!-- Logo — ocupa exactamente la columna del sidebar -->
      <div class="hidden sm:flex items-center justify-center sm:p-1 lg:p-3 lg:justify-start">
        <div class="w-9 h-9 bg-primary rounded-lg flex items-center justify-center shrink-0">
          <i class="pi pi-cloud text-primary-contrast text-lg" />
        </div>
      </div>

      <!-- Buscador + controles — columna del main, con el mismo margen izquierdo que <main> -->
      <div class="flex gap-2 items-center px-4 sm:pl-3 lg:pl-3 lg:pr-6">

        <!-- Buscador -->
        <div class="flex-1">
          <div class="w-full max-w-4xl">
            <IconField class="w-full group">
              <InputIcon>
                <i class="pi pi-search text-surface-500 group-focus-within:text-surface-900 dark:group-focus-within:text-surface-0 transition-colors duration-200" />
              </InputIcon>
              <InputText
                placeholder="Buscar"
                class="w-full py-3 px-12 border-none rounded-3xl transition-all duration-200
                       bg-surface-150 dark:bg-surface-800
                       hover:bg-surface-200 dark:hover:bg-surface-700
                       focus:bg-surface-0 dark:focus:bg-surface-900
                       focus:shadow-[0_1px_1px_0_rgba(65,69,73,.3),0_1px_3px_1px_rgba(65,69,73,.15)]
                       dark:focus:shadow-[0_1px_3px_rgba(0,0,0,.5)]"
              />
            </IconField>
          </div>
        </div>

        <!-- Controles derecha -->
        <div class="hidden sm:flex items-center gap-2 shrink-0">
          <ThemeToggle />

          <button
            class="w-9 h-9 rounded-full shrink-0 p-0 border-0 bg-transparent focus:outline-none cursor-pointer"
            style="line-height:0"
            @click="toggleMenuUsuario"
            aria-label="Menú de usuario"
          >
            <div class="w-full h-full rounded-full overflow-hidden ring-2 ring-transparent hover:ring-primary transition-all duration-200 bg-surface-200 dark:bg-surface-700 flex items-center justify-center">
              <img
                v-if="perfil.foto_perfil_url"
                :src="perfil.foto_perfil_url"
                alt="Avatar"
                class="w-full h-full object-cover block pointer-events-none"
              />
              <span
                v-else-if="inicial"
                class="text-sm font-semibold text-surface-600 dark:text-surface-300 select-none pointer-events-none leading-none"
              >
                {{ inicial }}
              </span>
              <i v-else class="pi pi-user text-surface-500 text-sm pointer-events-none" />
            </div>
          </button>

          <Menu ref="menuUsuario" :model="opcionesMenu" popup />
        </div>
      </div>
    </header>

    <!-- ── SIDEBAR desktop ──────────────────────────────────────── -->
    <aside class="hidden sm:block sm:p-1 lg:p-3">
      <Sidebar
        :perfil="perfil"
        @abrir-ajustes="mostrarAjustes = true"
        @cerrar-sesion="cerrarSesion"
      />
    </aside>

    <!-- ── MAIN ─────────────────────────────────────────────────── -->
    <main class="overflow-auto bg-surface-0 dark:bg-surface-900 rounded-2xl ml-3 mr-3 pb-24 lg:pb-0">
      <router-view />
    </main>

  </div>

  <!-- ── PANEL USUARIO MÓVIL ──────────────────────────────────────── -->
  <Teleport to="body">
    <Transition name="panel-movil">
      <div
        v-if="panelUsuarioMovil"
        class="lg:hidden fixed inset-0 z-[60] flex flex-col justify-end"
      >
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="panelUsuarioMovil = false" />
        <div
          class="relative bg-surface-0 dark:bg-surface-900 rounded-t-2xl px-5 pt-5"
          style="padding-bottom: calc(2rem + env(safe-area-inset-bottom))"
        >
          <div class="w-10 h-1 bg-surface-300 dark:bg-surface-600 rounded-full mx-auto mb-5" />

          <div class="flex items-center gap-3 mb-5">
            <div class="w-12 h-12 rounded-full overflow-hidden bg-surface-200 dark:bg-surface-700 flex items-center justify-center shrink-0">
              <img v-if="perfil.foto_perfil_url" :src="perfil.foto_perfil_url" class="w-full h-full object-cover" />
              <span v-else-if="inicial" class="text-lg font-semibold text-surface-600 dark:text-surface-300">{{ inicial }}</span>
              <i v-else class="pi pi-user text-surface-500" />
            </div>
            <div class="min-w-0">
              <p class="font-semibold text-surface-900 dark:text-surface-0 truncate">{{ perfil.nombre }} {{ perfil.apellidos }}</p>
              <p class="text-xs text-surface-500 truncate">{{ perfil.email }}</p>
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <button
              @click="() => { panelUsuarioMovil = false; mostrarAjustes = true }"
              class="flex items-center gap-3 px-3 py-3 rounded-xl text-sm text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors text-left w-full"
            >
              <i class="pi pi-cog text-surface-400" /> Configuración
            </button>
            <div class="flex items-center gap-3 px-3 py-3 rounded-xl">
              <i class="pi pi-moon text-surface-400 text-sm" />
              <span class="text-sm text-surface-700 dark:text-surface-300 flex-1">Tema oscuro</span>
              <ThemeToggle />
            </div>
            <div class="my-1 border-t border-surface-100 dark:border-surface-800" />
            <button
              @click="() => { panelUsuarioMovil = false; cerrarSesion() }"
              class="flex items-center gap-3 px-3 py-3 rounded-xl text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors text-left w-full"
            >
              <i class="pi pi-sign-out" /> Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <SettingsModal
    v-model="mostrarAjustes"
    :profile="perfil"
    @profile-updated="alActualizarPerfil"
  />
</template>

<style scoped>
.panel-movil-enter-active,
.panel-movil-leave-active { transition: opacity 0.25s ease; }
.panel-movil-enter-active .relative,
.panel-movil-leave-active .relative { transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.panel-movil-enter-from,
.panel-movil-leave-to { opacity: 0; }
.panel-movil-enter-from .relative,
.panel-movil-leave-to .relative { transform: translateY(100%); }
</style>
