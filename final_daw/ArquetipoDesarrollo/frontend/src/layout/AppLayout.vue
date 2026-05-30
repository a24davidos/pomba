<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from '@/api/auth'
import { servicioUsuario } from '@/api/users'
import api from '@/api/api'
import { useItemsStore } from '@/stores/items'
import SettingsModal from '@/components/SettingsModal.vue'
import Sidebar from '@/components/Sidebar.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

const store = useItemsStore()

const router = useRouter()
const route = useRoute()

// ── Búsqueda ──────────────────────────────────────────────────────
const textoBusqueda = ref('')
let timerBusqueda = null

// Sincroniza el input cuando el usuario naveg
watch(() => route.query.q, (q) => {
  textoBusqueda.value = q || ''
}, { immediate: true })

watch(textoBusqueda, (texto) => {
  clearTimeout(timerBusqueda)
  const trimado = texto.trim()
  if (!trimado) {
    if (route.name === 'search') router.push('/home')
    return
  }
  timerBusqueda = setTimeout(() => {
    router.push({ name: 'search', query: { q: trimado } })
  }, 400)
})

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

// ── Modal renombrar (global, compartido por Home y SearchResults) ─
const inputRenombrar = ref('')

// ── Modal mover!! ──────────────────────────────────────────
// Le llamo Picker porque como el file explorer tb te permite seleccionar para que no haya lios
const carpetaPickerId = ref(null)
const carpetasEnPicker = ref([])
const breadcrumbPicker = ref([{ label: 'Mi unidad', id: null }])
const cargandoPicker = ref(false)
const idsMoviendo = ref([])
let tokenPicker = 0

watch(() => store.ui.modal, async (modal) => {
  if (modal.open && modal.name === 'renombrar') {
    inputRenombrar.value = modal.payload?.nombre || ''
  } else if (modal.open && modal.name === 'mover') {
    carpetaPickerId.value = null
    breadcrumbPicker.value = [{ label: 'Mi unidad', id: null }]
    if (modal.payload && modal.payload.ids) {
      idsMoviendo.value = modal.payload.ids
    } else {
      idsMoviendo.value = []
    }
    await cargarCarpetasEnPicker(null)
  }
}, { deep: true })

async function cargarCarpetasEnPicker(carpetaId) {
  const token = ++tokenPicker
  cargandoPicker.value = true
  try {
    const params = { papelera: 'false' }
    if (carpetaId) {
      params.carpeta = carpetaId
    }
    const resp = await api.get('items/', { params })
    if (token !== tokenPicker) return
    carpetasEnPicker.value = resp.data.items.filter(
      (i) => i.tipo === 'carpeta' && !idsMoviendo.value.includes(i.id)
    )
  } catch {
    carpetasEnPicker.value = []
  } finally {
    if (token === tokenPicker) cargandoPicker.value = false
  }
}

async function navegarAPicker(carpeta) {
  carpetaPickerId.value = carpeta.id
  breadcrumbPicker.value.push({ label: carpeta.nombre, id: carpeta.id })
  await cargarCarpetasEnPicker(carpeta.id)
}

async function irABreadcrumbPicker(idx) {
  const nodo = breadcrumbPicker.value[idx]
  breadcrumbPicker.value = breadcrumbPicker.value.slice(0, idx + 1)
  carpetaPickerId.value = nodo.id
  await cargarCarpetasEnPicker(nodo.id)
}

async function confirmarMover() {
  await store.moverItems(idsMoviendo.value, carpetaPickerId.value)
  store.cerrarModal()
}

async function renombrar() {
  const id = store.ui.modal.payload.id
  const exito = await store.renombrarItem(id, inputRenombrar.value)
  if (exito) {
    store.cerrarModal()
    inputRenombrar.value = ''
  }
}

// ── Snackbars ─────────────────────────────────────────────────────
const CLASES_SNACKBAR = {
  neutro:      'bg-surface-800 dark:bg-surface-100 text-white dark:text-surface-900',
  exito:       'bg-green-700 dark:bg-green-100 text-white dark:text-green-900',
  advertencia: 'bg-amber-600 dark:bg-amber-100 text-white dark:text-amber-900',
  peligro:     'bg-red-700 dark:bg-red-100 text-white dark:text-red-900',
}

function clasesSnackbar(notif) {
  if (notif.tipo === 'error') return CLASES_SNACKBAR.peligro
  return CLASES_SNACKBAR[notif.severidad] ?? CLASES_SNACKBAR.neutro
}
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-[60px_1fr] lg:grid-cols-[260px_1fr] grid-rows-[64px_1fr] h-screen w-full bg-surface-100 dark:bg-surface-950 gap-y-2 py-2 pr-3">

    <!-- ── TOPBAR ───────────────────────────────────────────────── -->
    <!-- Sub-grid que utiliza las mismas columnas del layout principal -->
    <header class="col-span-full grid grid-cols-subgrid items-center z-10">

      <!-- Logo — ocupa exactamente la columna del sidebar -->
      <div class="hidden sm:flex items-center justify-center gap-3 sm:p-1 lg:py-3 lg:pl-6 lg:justify-start">
        <div class="w-11 h-11 shrink-0 text-surface-900 dark:text-surface-0">
          <svg viewBox="0 0 358 316" class="w-full h-full" fill="currentColor" aria-hidden="true">
            <path d="m309.01 239.53c-2.52-6.63-5.75-11.31-12.32-17.86-13.38-13.34-25.8-18.61-45.69-19.39-9.73-0.39-13.94-0.12-19 1.19-6.65 1.72-17.69 7.24-19.97 9.99-1.5 1.81-0.75 1.91 3.98 0.51 13.57-4.02 27.08-4.9 39.15-2.54 17.29 3.39 29.62 9.87 47.12 24.79 3.72 3.18 6.97 5.78 7.22 5.78 0.25 0 0.03-1.11-0.49-2.47zm-232.51-13.97c1.1-0.74 8.19-3.47 15.75-6.08l13.75-4.73 8.39 4.25c9.18 4.66 9.07 4.65 21.07 1.08q22.84-6.79 43.33 2.9l6.2 2.93 3.34-5.2c7.09-11.08 21.96-21.09 37.67-25.36 10.38-2.82 25.16-2.38 37.4 1.12l9.9 2.84 2.86-3.41c4.5-5.35 10.65-18.6 12.94-27.9 1.89-7.65 2.03-10.26 1.45-26-0.36-9.62-0.57-19.3-0.47-21.5 0.32-7.11 0.11-12.91-0.61-16.79-0.63-3.4-0.25-4.43 3.56-9.86l4.25-6.07-3.82-7.43c-6.1-11.84-15.23-18.78-28.27-21.47-10.75-2.22-23.19 1.41-31.78 9.28-6.7 6.14-11.58 14.16-15.86 26.05-2.03 5.66-5.23 14.33-7.11 19.27l-3.41 8.98 3.88 4.02c5.28 5.46 8.99 13.28 9.75 20.52 0.34 3.3 0.38 6 0.08 6-0.3 0-1.69-1.94-3.08-4.32-3.64-6.21-14.87-16.37-24.69-22.32-18.17-11.03-50.88-25.74-78.97-35.51-18.8-6.55-47.57-15.85-48.99-15.85-3.27 0 2.8 19.79 8.67 28.26 4.78 6.91 13.81 13.5 27.96 20.4 11.84 5.78 15.96 8.11 12.11 6.88-0.69-0.23-6.9-1.77-13.81-3.43-6.9-1.66-13.83-3.5-15.39-4.09l-2.84-1.08 0.6 5.03c1.96 16.52 12.92 25.81 37.65 31.89 6.01 1.48 11.25 3.01 11.65 3.41 1.12 1.13-17.53 0.86-24.02-0.34-3.18-0.59-6.01-0.85-6.28-0.58-0.27 0.28 0.73 3.22 2.23 6.56 8.14 18.13 34.53 28.36 64.71 25.08 11.79-1.29 25.03-5.37 34.43-10.63 3.54-1.97 6.64-3.37 6.91-3.11 0.71 0.72-6.6 9.63-11.85 14.45-5.83 5.34-16.22 10.57-25.45 12.8-11.22 2.72-33.97 1.74-44.79-1.92-4.4-1.49-10.54-4.25-13.64-6.14-6.05-3.68-7.14-3.88-52.36-9.46-8.8-1.09-17.01-2.21-18.25-2.5-2.96-0.68-2.96 1.72 0.02 6.93 3.6 6.29 5.93 7.39 18.59 8.78 11.82 1.29 12.13 1.84 2.14 3.79-7.6 1.48-8.67 2.26-7.27 5.33 1.67 3.66 7.04 9.43 11.86 12.75 4.8 3.3 5.12 3.36 7.91 1.5zm181.9-127.96c-2.9-2.9-3.4-4.09-3.4-8.1 0-10.89 12.1-17.5 18.72-10.23 6.03 6.62 5.51 14.25-1.33 19.64-4.27 3.36-9.85 2.83-13.99-1.31zm49.08 5.27c4.39-1.06 8.35-2.3 8.79-2.74 0.99-0.99-9.45-5.13-12.92-5.13-3.81 0-6.21 1.73-7.85 5.66-0.83 1.97-1.5 3.75-1.5 3.96 0 0.84 5.94 0.07 13.48-1.75z"/>
          </svg>
        </div>
        <span class="hidden lg:block text-2xl font-bold tracking-tight text-surface-900 dark:text-surface-0 select-none">
          Pomba
        </span>
      </div>

      <!-- Buscador + controles — columna del main, con el mismo margen izquierdo que <main> -->
      <div class="flex gap-2 items-center pl-4 pr-0 sm:pl-3 lg:pr-6">

        <!-- Buscador -->
        <div class="flex-1">
          <div class="w-full max-w-4xl">
            <IconField class="w-full group">
              <InputIcon>
                <i class="pi pi-search text-surface-500 group-focus-within:text-surface-900 dark:group-focus-within:text-surface-0 transition-colors duration-200" />
              </InputIcon>
              <InputText
                v-model="textoBusqueda"
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

          <Menu ref="menuUsuario" class="text-base" :model="opcionesMenu" popup />
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
    <main class="overflow-hidden bg-surface-0 dark:bg-surface-900 rounded-2xl ml-3">
      <router-view />
    </main>

  </div>

  <!-- ── PANEL USUARIO MÓVIL ──────────────────────────────────────── -->
  <Teleport to="body">
    <Transition name="panel-movil">
      <div
        v-if="panelUsuarioMovil"
        class="lg:hidden fixed inset-0 z-60 flex flex-col justify-end"
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

  <!-- SNACKBARS — globales, visibles en cualquier vista -->
  <div class="fixed bottom-20 left-3 z-50 flex flex-col-reverse gap-2 sm:bottom-6 sm:left-6">
    <TransitionGroup name="snack">
      <div
        v-for="notif in store.notificaciones"
        :key="notif.id"
        class="flex items-center gap-3 text-sm font-medium px-4 py-3 rounded-xl shadow-lg"
        :class="clasesSnackbar(notif)"
      >
        <i
          class="pi text-base shrink-0"
          :class="notif.tipo === 'cargando' ? 'pi-spin pi-spinner' : notif.icono"
        />
        <span>{{ notif.mensaje }}</span>
        <button
          v-if="notif.tipo !== 'cargando'"
          @click="store.eliminarNotificacion(notif.id)"
          class="ml-1 shrink-0 opacity-60 hover:opacity-100 transition-opacity cursor-pointer"
          aria-label="Cerrar"
        >
          <i class="pi pi-times text-xs" />
        </button>
      </div>
    </TransitionGroup>
  </div>

  <!-- MODAL RENOMBRAR — global, abierto desde cualquier vista -->
  <Dialog
    v-if="store.ui.modal.name === 'renombrar'"
    v-model:visible="store.ui.modal.open"
    header="Renombrar"
    :style="{ width: '25rem' }"
    modal :draggable="false" :closable="false"
  >
    <div class="flex flex-col gap-2 mb-4">
      <InputText
        v-model="inputRenombrar"
        class="flex-auto"
        autocomplete="off"
        placeholder="Nuevo nombre"
        @keyup.enter="renombrar"
        autofocus
      />
    </div>
    <template #footer>
      <Button label="Cancelar" text severity="secondary" @click="store.cerrarModal" />
      <Button label="Confirmar" @click="renombrar" :disabled="!inputRenombrar.trim()" />
    </template>
  </Dialog>

  <!-- MODAL MOVER-->
  <Dialog
    v-if="store.ui.modal.name === 'mover'"
    v-model:visible="store.ui.modal.open"
    header="Mover a..."
    :style="{ width: '28rem' }"
    modal :draggable="false" :closable="false"
  >
    <!-- Breadcrumb del picker -->
    <div class="flex items-center gap-1 text-sm mb-3 flex-wrap min-h-6">
      <template v-for="(nodo, idx) in breadcrumbPicker" :key="idx">
        <span v-if="idx > 0" class="text-surface-300 dark:text-surface-600 select-none">›</span>
        <button
          v-if="idx < breadcrumbPicker.length - 1"
          @click="irABreadcrumbPicker(idx)"
          class="font-medium text-primary hover:underline cursor-pointer bg-transparent border-none p-0"
        >{{ nodo.label }}</button>
        <span v-else class="text-surface-600 dark:text-surface-400 font-medium">{{ nodo.label }}</span>
      </template>
    </div>

    <!-- Lista de carpetas -->
    <div class="min-h-40 max-h-65 overflow-y-auto rounded-lg border border-surface-200 dark:border-surface-700">
      <div v-if="cargandoPicker" class="flex items-center justify-center py-10 text-surface-400">
        <i class="pi pi-spin pi-spinner text-xl" />
      </div>
      <div
        v-else-if="!carpetasEnPicker.length"
        class="flex flex-col items-center justify-center py-10 gap-2 text-surface-400"
      >
        <i class="pi pi-folder-open text-2xl" />
        <span class="text-xs">Sin subcarpetas</span>
      </div>
      <div v-else>
        <button
          v-for="carpeta in carpetasEnPicker"
          :key="carpeta.id"
          @click="navegarAPicker(carpeta)"
          class="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-left
                 text-surface-700 dark:text-surface-300
                 hover:bg-surface-50 dark:hover:bg-surface-800
                 transition-colors border-b border-surface-100 dark:border-surface-800 last:border-0"
        >
          <i class="pi pi-folder text-yellow-500 shrink-0" />
          <span class="truncate flex-1">{{ carpeta.nombre }}</span>
          <i class="pi pi-chevron-right text-surface-300 dark:text-surface-600 text-xs shrink-0" />
        </button>
      </div>
    </div>

    <template #footer>
      <Button label="Cancelar" text severity="secondary" @click="store.cerrarModal" />
      <Button label="Mover aquí" icon="pi pi-check" @click="confirmarMover" />
    </template>
  </Dialog>
</template>

<style scoped>
.snack-enter-active,
.snack-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.snack-enter-from,
.snack-leave-to { opacity: 0; transform: translateY(0.5rem); }
.snack-move { transition: transform 0.2s ease; }

.panel-movil-enter-active,
.panel-movil-leave-active { transition: opacity 0.25s ease; }
.panel-movil-enter-active .relative,
.panel-movil-leave-active .relative { transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.panel-movil-enter-from,
.panel-movil-leave-to { opacity: 0; }
.panel-movil-enter-from .relative,
.panel-movil-leave-to .relative { transform: translateY(100%); }
</style>
