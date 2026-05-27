<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useItemsStore } from '@/stores/items'
import { formatDate } from '../utils/date'

const store = useItemsStore()
//Por defecto
const sortCampo = ref('fecha_modificacion')
const sortDir = ref('desc')

function ordenarPor(campo) {
  if (sortCampo.value === campo) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortCampo.value = campo
    sortDir.value = 'asc'
  }
}

const comparadores = {
  //Uso base, para que ignore mayúsculas y minúsculas
  nombre: (a, b) => a.nombre.localeCompare(b.nombre, 'es', { sensitivity: 'base' }),
  tamano_bytes: (a, b) => (a.tamano_bytes ?? -1) - (b.tamano_bytes ?? -1),
  fecha_modificacion: (a, b) => new Date(a.fecha_modificacion) - new Date(b.fecha_modificacion),
}

const itemsOrdenados = computed(() => {
  const dir = sortDir.value === 'asc' ? 1 : -1
  const comparar = comparadores[sortCampo.value]
  return [...store.items].sort((a, b) => dir * comparar(a, b))
})
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
    store.seleccionarRango(index, itemsOrdenados.value)
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
  contextMenu.value.visible = false
  const ids = store.seleccion.ids

  if (accion === 'download') {
    await store.descargarItems()
  } else if (accion === 'favorite' || accion === 'unfavorite') {
    await store.marcarFavoritos(ids)
  } else if (accion === 'delete') {
    await store.eliminarItems(ids)
  } else if (accion === 'restore') {
    await store.restaurarItems(ids)
  } else if (accion === 'deleteForever') {
    await store.eliminarDefinitivamente(ids)
  } else {
    emit(accion)
  }
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

    <!-- ── Tabla ───────────────────────────────────────────────── -->
    <table v-else role="grid" aria-label="Archivos" class="w-full table-fixed border-collapse">
      <thead class="sticky top-0 z-10">
        <tr
          role="presentation"
          class="bg-surface-0 dark:bg-surface-900 border-b border-surface-200 dark:border-surface-800
                 text-sm font-medium text-surface-400 dark:text-surface-500"
        >
          <th scope="col" class="text-left px-4 py-2 font-medium">
            <button @click="ordenarPor('nombre')" class="flex items-center gap-1 hover:text-surface-600 dark:hover:text-surface-300 transition-colors">
              Nombre
              <i :class="sortCampo === 'nombre' ? (sortDir === 'asc' ? 'pi pi-arrow-up' : 'pi pi-arrow-down') : 'pi pi-arrow-up opacity-0'" class="text-xs" />
            </button>
          </th>
          <th scope="col" class="text-left px-4 py-2 font-medium w-24">
            <button @click="ordenarPor('tamano_bytes')" class="flex items-center gap-1 hover:text-surface-600 dark:hover:text-surface-300 transition-colors">
              Tamaño
              <i :class="sortCampo === 'tamano_bytes' ? (sortDir === 'asc' ? 'pi pi-arrow-up' : 'pi pi-arrow-down') : 'pi pi-arrow-up opacity-0'" class="text-xs" />
            </button>
          </th>
          <th scope="col" class="hidden sm:table-cell text-left px-4 py-2 font-medium w-32">
            <button @click="ordenarPor('fecha_modificacion')" class="flex items-center gap-1 hover:text-surface-600 dark:hover:text-surface-300 transition-colors">
              Modificado
              <i :class="sortCampo === 'fecha_modificacion' ? (sortDir === 'asc' ? 'pi pi-arrow-up' : 'pi pi-arrow-down') : 'pi pi-arrow-up opacity-0'" class="text-xs" />
            </button>
          </th>
          <th scope="col" class="w-10 px-4 py-2" />
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(item, index) in itemsOrdenados"
          :key="item.id"
          role="row"
          :aria-selected="estaSeleccionado(item)"
          :tabindex="index === 0 ? 0 : -1"
          @click.stop="handleClick($event, item, index)"
          @dblclick.stop="handleDoubleClick(item)"
          @contextmenu="handleContextMenu($event, item, index)"
          :class="[
            'group cursor-pointer transition-colors duration-100 border-b border-surface-200 dark:border-surface-800',
            estaSeleccionado(item)
              ? 'bg-primary/20 dark:bg-primary/25'
              : 'hover:bg-surface-100 dark:hover:bg-surface-800',
          ]"
        >
          <!-- Nombre -->
          <td class="px-4 py-3 max-w-0">
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
          </td>

          <!-- Tamaño -->
          <td class="px-4 py-3">
            <span class="text-xs text-surface-500 dark:text-surface-400">
              {{ item.tipo === 'carpeta' ? '—' : formatBytes(item.tamano_bytes) }}
            </span>
          </td>

          <!-- Modificado -->
          <td class="hidden sm:table-cell px-4 py-3">
            <span class="text-xs text-surface-500 dark:text-surface-400">
              {{ formatDate(item.fecha_modificacion) }}
            </span>
          </td>

          <!-- Botón ··· -->
          <td class="px-4 py-3">
            <div class="relative flex items-center justify-center">
              <button
                @click.stop="toggleMenu($event, item.id)"
                :aria-label="`Opciones de ${item.nombre}`"
                :class="[
                  'w-7 h-7 shrink-0 flex items-center justify-center rounded-full transition-colors',
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
          </td>
        </tr>
      </tbody>
    </table>

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
            v-if="store.seleccion.ids.length === 1"
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
            v-if="store.seleccion.ids.length === 1 && !store.itemsSeleccionados[0]?.favorito"
            @click="accionContextMenu('favorite')"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
          >
            <i class="pi pi-star text-surface-400" /> Marcar favorito
          </button>
          <button
            v-else-if="store.seleccion.ids.length === 1 && store.itemsSeleccionados[0]?.favorito"
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
