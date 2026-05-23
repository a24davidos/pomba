<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useItemsStore } from '@/stores/items'

import FileTable from '../components/FileTable.vue'
import Breadcrumb from 'primevue/breadcrumb'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Divider from 'primevue/divider'

const store = useItemsStore()
const route = useRoute()
const router = useRouter()

const inputNuevaCarpeta = ref('')
const inputRenombrar = ref('')

const CONFIGURACION_VISTAS = {
  drive: {
    titulo: 'Mi unidad',
    icono: 'pi pi-folder',
    paramsBase: { papelera: 'false', favoritos: 'false' },
  },
  trash: {
    titulo: 'Papelera',
    icono: 'pi pi-trash',
    paramsBase: { papelera: 'true' },
  },
  fav: {
    titulo: 'Favoritos',
    icono: 'pi pi-star',
    paramsBase: { papelera: 'false', favorito: 'true' },
  },
  recent: {
    titulo: 'Recientes',
    icono: 'pi pi-clock',
    paramsBase: {},
  },
}

const enPapelera = computed(() => (route.params.view || 'drive') === 'trash')

const breadcrumbInicio = computed(() => {
  const vistaActual = route.params.view || 'drive'
  const config = CONFIGURACION_VISTAS[vistaActual]
  return {
    label: config?.titulo || 'Mi unidad',
    icon: config?.icono || 'pi pi-home',
    command: () => router.push({ name: 'home', params: { view: vistaActual } }),
  }
})

const rutaBreadcrumb = computed(() =>
  store.breadcrumb
    .filter((nodo) => nodo.id !== null)
    .map((nodo) => ({
      label: nodo.label,
      id: nodo.id,
      command: () =>
        router.push({
          name: 'home',
          params: { view: route.params.view || 'drive', folderId: nodo.id },
        }),
    }))
)

function cargarDesdeRuta() {
  const vista = route.params.view || 'drive'
  const folderId = route.params.folderId || null
  const config = CONFIGURACION_VISTAS[vista] || CONFIGURACION_VISTAS.drive
  return store.cargarItems({ ...config.paramsBase, carpeta: folderId })
}

function cerrarModal() {
  store.cerrarModal()
  inputNuevaCarpeta.value = ''
  inputRenombrar.value = ''
}

async function crearCarpeta() {
  const idPadre = route.params.folderId || null
  await store.crearCarpeta({ nombre: inputNuevaCarpeta.value, tipo: 'carpeta', padre: idPadre })
  cerrarModal()
  await cargarDesdeRuta()
}

// ── Barra de acciones para elementos seleccionados ─────────────────
async function eliminar() {
  const ids = store.itemsSeleccionados.map((i) => i.id)
  if (!ids.length) return
  await store.eliminarItems(ids)
  store.limpiarSeleccion()
  await cargarDesdeRuta()
}

async function eliminarDefinitivamente() {
  const ids = store.itemsSeleccionados.map((i) => i.id)
  if (!ids.length) return
  await store.eliminarDefinitivamente(ids)
  store.limpiarSeleccion()
  await cargarDesdeRuta()
}

async function restaurar() {
  const ids = store.itemsSeleccionados.map((i) => i.id)
  if (!ids.length) return
  await store.restaurarItems(ids)
  store.limpiarSeleccion()
  await cargarDesdeRuta()
}

async function marcarFavoritos() {
  const ids = store.itemsSeleccionados.map((i) => i.id)
  if (!ids.length) return
  await store.marcarFavoritos(ids)
  store.limpiarSeleccion()
  await cargarDesdeRuta()
}

function abrirModalRenombrar(item) {
  // Se puede llamar desde la action bar o los ...
  const objetivo = item ?? store.itemsSeleccionados[0]
  if (!objetivo) return
  inputRenombrar.value = objetivo.nombre
  store.abrirModal('renombrar', objetivo)
}

async function renombrar() {
  const id = store.ui.modal.payload.id
  await store.renombrarItem(id, inputRenombrar.value)
  store.limpiarSeleccion()
  cerrarModal()
  await cargarDesdeRuta()
}

async function descargar() {
  await store.descargarItems()
}

// COLORES PUESTOS UN POCO DE PLACEHOLDER REVISAR CUANDO LE DES ESTILOS GLOBALES QUE VAYA BIEN
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

watch(
  () => [route.params.view, route.params.folderId],
  async () => {
    store.limpiarSeleccion()
    await cargarDesdeRuta()
  },
  { immediate: true }
)
</script>

<template>
  <div class="flex flex-col h-full">

    <!-- ZONA FIJA: breadcrumb + action bar -->
    <div class="px-4 pt-4 space-y-4 shrink-0">

    <!-- BREADCRUMB -->
    <Breadcrumb
      :home="breadcrumbInicio"
      :model="rutaBreadcrumb"
      :pt="{
        root: { class: 'p-0 bg-transparent border-none' },
        homeItem: { class: 'text-lg font-semibold text-surface-900 dark:text-surface-0' },
        item: { class: 'text-xl font-semibold text-surface-900 dark:text-surface-0' },
        separator: { class: 'text-surface-400 dark:text-surface-500 mx-1' },
      }"
    />

    <!--
      ACTION BAR — solo desktop (sm:flex).
      En móvil las acciones vienen del menú ··· y de la barra
      de selección integrada en FileTable.
    -->
    <div class="h-9 hidden sm:block">
      <Transition
        enter-active-class="transition-all duration-150 ease-out"
        enter-from-class="opacity-0 -translate-y-1"
        leave-active-class="transition-all duration-150 ease-in"
        leave-to-class="opacity-0 -translate-y-1"
      >
        <div
          v-if="store.itemsSeleccionados.length > 0"
          class="flex items-center gap-1
                 bg-surface-0 dark:bg-surface-900
                 border border-surface-200 dark:border-surface-700
                 rounded-full px-2 py-1 h-9 w-fit"
        >
          <div class="flex items-center gap-2 pr-3 border-r border-surface-200 dark:border-surface-700 mr-1">
            <button
              @click="store.limpiarSeleccion()"
              aria-label="Deseleccionar todo"
              class="w-6 h-6 rounded-full flex items-center justify-center
                     text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-800
                     transition-colors cursor-pointer"
            >
              <i class="pi pi-times text-xs" />
            </button>
            <span class="text-xs font-medium whitespace-nowrap">
              {{ store.itemsSeleccionados.length }}
              {{ store.itemsSeleccionados.length === 1 ? 'seleccionado' : 'seleccionados' }}
            </span>
          </div>

          <template v-if="enPapelera">
            <Button icon="pi pi-replay" label="Restaurar" text size="small" rounded @click="restaurar" />
            <Divider layout="vertical" class="h-4! mx-1!" />
            <Button icon="pi pi-trash" label="Eliminar para siempre" text size="small" rounded severity="danger" @click="eliminarDefinitivamente" />
          </template>

          <template v-else>
            <Button
              icon="pi pi-download"
              label="Descargar"
              text size="small" rounded
              :loading="store.descargando"
              @click="descargar()"
            />
            <Button icon="pi pi-star" label="Favorito" text size="small" rounded @click="marcarFavoritos" />
            <Button
              v-if="store.itemsSeleccionados.length === 1"
              icon="pi pi-pencil" label="Renombrar" text size="small" rounded
              @click="abrirModalRenombrar()"
            />
            <Divider layout="vertical" class="h-4! mx-1!" />
            <Button icon="pi pi-trash" label="Eliminar" text size="small" rounded severity="danger" @click="eliminar" />
          </template>
        </div>
      </Transition>
    </div>
    </div>

    <!-- ZONA SCROLLABLE: tabla de archivos -->
    <div class="flex-1 min-h-0 overflow-auto pb-24 lg:pb-0
                [&::-webkit-scrollbar]:w-1.5
                [&::-webkit-scrollbar-track]:bg-transparent
                [&::-webkit-scrollbar-thumb]:rounded-full
                [&::-webkit-scrollbar-thumb]:bg-surface-300
                dark:[&::-webkit-scrollbar-thumb]:bg-surface-600">
      <FileTable @rename="abrirModalRenombrar" />
    </div>

    <!-- SNACKBARS -->
    <div class="fixed bottom-20 left-3 z-50 flex flex-col-reverse gap-2 sm:bottom-6 sm:left-6">
      <!-- ↑ bottom-20 en móvil para no quedar tapado por la bottom nav -->
      <TransitionGroup name="snack">
        <div
          v-for="notif in store.notificaciones"
          :key="notif.id"
          class="flex items-center gap-3 text-sm font-medium px-4 py-3 rounded-xl shadow-lg"
          :class="clasesSnackbar(notif)"
        >
          <i
            class="pi text-base"
            :class="notif.tipo === 'cargando' ? 'pi-spin pi-spinner' : notif.icono"
          />
          <span>{{ notif.mensaje }}</span>
        </div>
      </TransitionGroup>
    </div>

    <!-- MODAL NUEVA CARPETA -->
    <Dialog
      v-if="store.ui.modal.name === 'crearCarpeta'"
      v-model:visible="store.ui.modal.open"
      header="Nueva Carpeta"
      :style="{ width: '25rem' }"
      modal :draggable="false" :closable="false"
    >
      <div class="flex flex-col gap-2 mb-4">
        <InputText
          id="folderName"
          v-model="inputNuevaCarpeta"
          class="flex-auto"
          autocomplete="off"
          placeholder="Nombre de la carpeta"
          @keyup.enter="crearCarpeta"
          autofocus
        />
      </div>
      <template #footer>
        <Button label="Cancelar" text severity="secondary" @click="cerrarModal" />
        <Button label="Crear" @click="crearCarpeta" :disabled="!inputNuevaCarpeta.trim()" />
      </template>
    </Dialog>

    <!-- MODAL RENOMBRAR -->
    <Dialog
      v-if="store.ui.modal.name === 'renombrar'"
      v-model:visible="store.ui.modal.open"
      header="Renombrar"
      :style="{ width: '25rem' }"
      modal :draggable="false" :closable="false"
    >
      <div class="flex flex-col gap-2 mb-4">
        <InputText
          id="inputRename"
          v-model="inputRenombrar"
          class="flex-auto"
          autocomplete="off"
          placeholder="Nuevo nombre"
          @keyup.enter="renombrar"
          autofocus
        />
      </div>
      <template #footer>
        <Button label="Cancelar" text severity="secondary" @click="cerrarModal" />
        <Button label="Confirmar" @click="renombrar" :disabled="!inputRenombrar.trim()" />
      </template>
    </Dialog>
    
  </div>
</template>

<style scoped>
.snack-enter-active,
.snack-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.snack-enter-from,
.snack-leave-to {
  opacity: 0;
  transform: translateY(0.5rem);
}
.snack-move {
  transition: transform 0.2s ease;
}
</style>
