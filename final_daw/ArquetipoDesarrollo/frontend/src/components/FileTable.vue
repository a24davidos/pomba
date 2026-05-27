<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useItemsStore } from '@/stores/items'
import { formatDate } from '../utils/date'

const store = useItemsStore()
const route = useRoute()
const router = useRouter()

const emit = defineEmits(['rename', 'move'])

const menuAbierto = ref(null)
const esTactil = window.matchMedia('(pointer: coarse)').matches
const enPapelera = computed(() => (route.params.view || 'drive') === 'trash')

function abrirItem(item) {
  if (item.tipo !== 'carpeta') return
  router.push({
    name: 'home',
    params: { view: route.params.view || 'drive', folderId: item.id },
  })
}

function handleClick(event, item, index) {
  if (contextMenu.value.visible) contextMenu.value.visible = false

  if (menuAbierto.value !== null) {
    menuAbierto.value = null
    return
  }

  if (esTactil) {
    store.limpiarSeleccion()
    abrirItem(item)
    return
  }

  if (event.shiftKey && store.seleccion.lastIndex !== null) {
    store.seleccionarRango(index)
    return
  }
  if (event.ctrlKey || event.metaKey) {
    store.toggleSeleccion(item, index)
    return
  }
  if (store.seleccion.ids.length === 1 && store.seleccion.ids[0] === item.id) {
    store.limpiarSeleccion()
    return
  }
  store.seleccionar(item, index)
}

function handleDoubleClick(item) {
  store.limpiarSeleccion()
  abrirItem(item)
}

function handleBackgroundClick(event) {
  if (event.target === event.currentTarget) {
    store.limpiarSeleccion()
    menuAbierto.value = null
  }
}

// ── Lógica compartida de acciones ────────────────────────────────────
async function ejecutarAccion(accion, item) {
  if (accion === 'download') {
    store.seleccionar(item, null)
    await store.descargarItems()
  } else if (accion === 'favorite' || accion === 'unfavorite') {
    await store.marcarFavoritos([item.id])
  } else if (accion === 'delete') {
    await store.eliminarItems([item.id])
  } else if (accion === 'restore') {
    await store.restaurarItems([item.id])
  } else if (accion === 'deleteForever') {
    await store.eliminarDefinitivamente([item.id])
  } else {
    emit(accion, item)
  }
}

// ── Menú ··· ─────────────────────────────────────────────────────────
function toggleMenu(event, itemId) {
  event.stopPropagation()
  menuAbierto.value = menuAbierto.value === itemId ? null : itemId
}

async function accionMenu(event, accion, item) {
  event.stopPropagation()
  menuAbierto.value = null
  await ejecutarAccion(accion, item)
}

// ── Context menu (click derecho) ──────────────────────────────────────
const contextMenu = ref({ visible: false, x: 0, y: 0, item: null })

function handleContextMenu(event, item, index) {
  event.preventDefault()
  menuAbierto.value = null

  if (!store.seleccion.ids.includes(item.id)) {
    store.seleccionar(item, index)
  }

  const MENU_W = 176
  const MENU_H = 230
  const x = event.clientX + MENU_W > window.innerWidth ? event.clientX - MENU_W : event.clientX
  const y = event.clientY + MENU_H > window.innerHeight ? event.clientY - MENU_H : event.clientY

  contextMenu.value = { visible: true, x, y, item }
}

async function accionContextMenu(accion) {
  const item = contextMenu.value.item
  contextMenu.value.visible = false
  await ejecutarAccion(accion, item)
}

// ── Cierre de menús ───────────────────────────────────────────────────
function handleDocumentClick() {
  if (menuAbierto.value !== null) menuAbierto.value = null
  if (contextMenu.value.visible) contextMenu.value.visible = false
}

function handleKeydown(event) {
  if (event.key === 'Escape') {
    menuAbierto.value = null
    contextMenu.value.visible = false
  }
}

document.addEventListener('click', handleDocumentClick)
document.addEventListener('keydown', handleKeydown)
onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleKeydown)
})

function estaSeleccionado(item) {
  return store.seleccion.ids.includes(item.id)
}

function formatBytes(bytes) {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<template>
  <div
    class="w-full min-h-96 select-none relative"
    @click="handleBackgroundClick"
  >

    <!-- ── Cabecera sticky -->
    <div
      class="sticky top-0 z-10 grid grid-cols-[1fr_80px_32px] sm:grid-cols-[1fr_100px_130px_32px] gap-3 px-4 py-2
             text-sm font-medium text-surface-400 dark:text-surface-500
             bg-surface-0 dark:bg-surface-900
             border-b border-surface-200 dark:border-surface-800"
    >
      <span>Nombre</span>
      <span>Tamaño</span>
      <span class="hidden sm:block">Modificado</span>
      <span />
    </div>

    <!-- ── Loading ─────────────────────────────────────────────── -->
    <div v-if="store.loading" class="flex items-center justify-center py-16 text-surface-400">
      <i class="pi pi-spin pi-spinner text-2xl" />
    </div>

    <!-- ── Vacío ───────────────────────────────────────────────── -->
    <div
      v-else-if="!store.items.length"
      class="flex flex-col items-center justify-center py-16 gap-2
             text-surface-400 dark:text-surface-500"
    >
      <i class="pi pi-folder-open text-4xl" />
      <span class="text-sm">Esta carpeta está vacía</span>
    </div>

    <!-- ── Lista ───────────────────────────────────────────────── -->
    <div v-else>
      <div
        v-for="(item, index) in store.items"
        :key="item.id"
        @click.stop="handleClick($event, item, index)"
        @dblclick.stop="handleDoubleClick(item)"
        @contextmenu="handleContextMenu($event, item, index)"
        :class="[
          'group grid grid-cols-[1fr_80px_32px] sm:grid-cols-[1fr_100px_130px_32px] gap-3 px-4 py-3 items-center cursor-pointer transition-colors duration-100 border-b border-surface-200 dark:border-surface-800',
          estaSeleccionado(item)
            ? 'bg-primary/20 dark:bg-primary/25'
            : 'hover:bg-surface-100 dark:hover:bg-surface-800',
        ]"
      >
        <!-- Nombre -->
        <div class="flex items-center gap-2 min-w-0">
          <i
            :class="[
              item.tipo === 'carpeta' ? 'pi pi-folder text-yellow-500' : 'pi pi-file text-surface-400',
              'text-base shrink-0',
            ]"
          />
          <span class="truncate text-sm">{{ item.nombre }}</span>
          <i v-if="item.favorito" class="pi pi-star-fill text-yellow-400 text-xs shrink-0" />
        </div>

        <!-- Tamaño -->
        <span class="text-xs text-surface-500 dark:text-surface-400">
          {{ item.tipo === 'carpeta' ? '—' : formatBytes(item.tamano_bytes) }}
        </span>

        <!-- Modificado: solo escriotrioo -->
        <span class="hidden sm:block text-xs text-surface-500 dark:text-surface-400">
          {{ formatDate(item.fecha_modificacion) }}
        </span>

        <!-- Botón ··· -->
        <div class="relative flex items-center justify-center">
          <button
            @click.stop="toggleMenu($event, item.id)"
            :aria-label="`Opciones de ${item.nombre}`"
            :class="[
              'w-7 h-7 flex items-center justify-center rounded-md transition-colors',
              menuAbierto === item.id
                ? 'bg-surface-200 dark:bg-surface-700'
                : 'sm:opacity-0 sm:group-hover:opacity-100 hover:bg-surface-200 dark:hover:bg-surface-700',
            ]"
          >
            <i class="pi pi-ellipsis-h text-surface-400 dark:text-surface-500" style="font-size:13px" />
          </button>

          <!-- Dropdown menú ··· -->
          <Transition name="menu-drop">
            <div
              v-if="menuAbierto === item.id"
              @click.stop
              class="absolute right-0 top-8 z-50 w-44
                     bg-white dark:bg-surface-900
                     border border-surface-200 dark:border-surface-700
                     rounded-xl shadow-lg py-1 overflow-hidden"
            >
              <template v-if="enPapelera">
                <button
                  @click="accionMenu($event, 'restore', item)"
                  class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
                >
                  <i class="pi pi-replay text-surface-400" /> Restaurar
                </button>
                <div class="my-1 border-t border-surface-200 dark:border-surface-800" />
                <button
                  @click="accionMenu($event, 'deleteForever', item)"
                  class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                >
                  <i class="pi pi-trash" /> Eliminar definitivo
                </button>
              </template>

              <template v-else>
                <button
                  @click="accionMenu($event, 'download', item)"
                  class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
                >
                  <i class="pi pi-download text-surface-400" /> Descargar
                </button>
                <button
                  @click="accionMenu($event, 'rename', item)"
                  class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
                >
                  <i class="pi pi-pencil text-surface-400" /> Cambiar nombre
                </button>
                <button
                  @click="accionMenu($event, 'move', item)"
                  class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
                >
                  <i class="pi pi-arrow-right text-surface-400" /> Mover a...
                </button>
                <button
                  v-if="!item.favorito"
                  @click="accionMenu($event, 'favorite', item)"
                  class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
                >
                  <i class="pi pi-star text-surface-400" /> Marcar favorito
                </button>
                <button
                  v-else
                  @click="accionMenu($event, 'unfavorite', item)"
                  class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
                >
                  <i class="pi pi-star-fill text-yellow-400" /> Quitar favorito
                </button>
                <div class="my-1 border-t border-surface-200 dark:border-surface-800" />
                <button
                  @click="accionMenu($event, 'delete', item)"
                  class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                >
                  <i class="pi pi-trash" /> Eliminar
                </button>
              </template>
            </div>
          </Transition>
        </div>
      </div>
    </div>

  </div>

  <!-- ── Context menu (click derecho) -->
  <Teleport to="body">
    <Transition name="menu-drop">
      <div
        v-if="contextMenu.visible"
        @click.stop
        class="fixed z-[200] w-44
               bg-white dark:bg-surface-900
               border border-surface-200 dark:border-surface-700
               rounded-xl shadow-lg py-1 overflow-hidden"
        :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      >
        <template v-if="enPapelera">
          <button
            @click="accionContextMenu('restore')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
          >
            <i class="pi pi-replay text-surface-400" /> Restaurar
          </button>
          <div class="my-1 border-t border-surface-200 dark:border-surface-800" />
          <button
            @click="accionContextMenu('deleteForever')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
          >
            <i class="pi pi-trash" /> Eliminar definitivo
          </button>
        </template>

        <template v-else>
          <button
            @click="accionContextMenu('download')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
          >
            <i class="pi pi-download text-surface-400" /> Descargar
          </button>
          <button
            @click="accionContextMenu('rename')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
          >
            <i class="pi pi-pencil text-surface-400" /> Cambiar nombre
          </button>
          <button
            @click="accionContextMenu('move')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
          >
            <i class="pi pi-arrow-right text-surface-400" /> Mover a...
          </button>
          <button
            v-if="!contextMenu.item?.favorito"
            @click="accionContextMenu('favorite')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
          >
            <i class="pi pi-star text-surface-400" /> Marcar favorito
          </button>
          <button
            v-else
            @click="accionContextMenu('unfavorite')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
          >
            <i class="pi pi-star-fill text-yellow-400" /> Quitar favorito
          </button>
          <div class="my-1 border-t border-surface-200 dark:border-surface-800" />
          <button
            @click="accionContextMenu('delete')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
          >
            <i class="pi pi-trash" /> Eliminar
          </button>
        </template>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.menu-drop-enter-active,
.menu-drop-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.menu-drop-enter-from { opacity: 0; transform: translateY(-6px) scale(0.97); }
.menu-drop-leave-to   { opacity: 0; transform: translateY(-6px) scale(0.97); }
</style>
