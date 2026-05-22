<script setup>
import { ref, computed } from 'vue'
import { formatDate } from '../utils/date'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: Boolean,
})

const seleccionados = defineModel('seleccionados', { default: [] })
const emit = defineEmits(['open'])

const lastClickedIndex = ref(null)

const seleccionadosIds = computed(() => new Set(seleccionados.value.map((i) => i.id)))

function estaSeleccionado(item) {
  return seleccionadosIds.value.has(item.id)
}

function handleClick(event, item, index) {
  // Shift: rango
  if (event.shiftKey && lastClickedIndex.value !== null) {
    const desde = Math.min(lastClickedIndex.value, index)
    const hasta = Math.max(lastClickedIndex.value, index)
    const rango = props.items.slice(desde, hasta + 1)

    // Añadimos los del rango que no estén ya
    const idsActuales = seleccionadosIds.value
    const nuevos = rango.filter((i) => !idsActuales.has(i.id))
    seleccionados.value = [...seleccionados.value, ...nuevos]
    return
  }

  // Ctrl/Cmd: toggle individual sin perder los demás
  if (event.ctrlKey || event.metaKey) {
    if (estaSeleccionado(item)) {
      seleccionados.value = seleccionados.value.filter((i) => i.id !== item.id)
    } else {
      seleccionados.value = [...seleccionados.value, item]
    }
    lastClickedIndex.value = index
    return
  }

  // Click normal: si ya estaba seleccionado solo, deselecciona; si no, selecciona solo ese
  if (estaSeleccionado(item) && seleccionados.value.length === 1) {
    seleccionados.value = []
    lastClickedIndex.value = null
    return
  }

  seleccionados.value = [item]
  lastClickedIndex.value = index
}

function handleDoubleClick(item) {
  seleccionados.value = []
  lastClickedIndex.value = null
  emit('open', item)
}

// Click en el fondo vacío → deselecciona todo
function handleBackgroundClick(event) {
  if (event.target === event.currentTarget) {
    seleccionados.value = []
    lastClickedIndex.value = null
  }
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
    class="w-full min-h-96 select-none"
    @click="handleBackgroundClick"
  >
    <!-- CABECERA -->
    <div class="grid grid-cols-[1fr_120px_100px_140px] gap-4 px-3 py-2 text-xs font-medium text-surface-400 dark:text-surface-500 border-b border-surface-100 dark:border-surface-800">
      <span>Nombre</span>
      <span>Tipo</span>
      <span>Tamaño</span>
      <span>Modificado</span>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="flex items-center justify-center py-16 text-surface-400">
      <i class="pi pi-spin pi-spinner text-2xl" />
    </div>

    <!-- VACÍO -->
    <div
      v-else-if="!items.length"
      class="flex flex-col items-center justify-center py-16 gap-2 text-surface-400 dark:text-surface-500"
    >
      <i class="pi pi-folder-open text-4xl" />
      <span class="text-sm">Esta carpeta está vacía</span>
    </div>

    <!-- FILAS -->
    <div v-else>
      <div
        v-for="(item, index) in items"
        :key="item.id"
        @click.stop="handleClick($event, item, index)"
        @dblclick.stop="handleDoubleClick(item)"
        :class="[
          'grid grid-cols-[1fr_120px_100px_140px] gap-4 px-3 py-2 rounded-lg items-center cursor-pointer transition-colors duration-100 text-sm',
          estaSeleccionado(item)
            ? 'bg-primary/10 dark:bg-primary/20'
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
          <span class="truncate">{{ item.nombre }}</span>
          <!-- Estrella favorito -->
          <i
            v-if="item.favorito"
            class="pi pi-star-fill text-yellow-400 text-xs shrink-0"
          />
        </div>

        <!-- Tipo -->
        <span class="text-surface-500 dark:text-surface-400 capitalize">
          {{ item.tipo === 'carpeta' ? 'Carpeta' : (item.mime_type || 'Archivo') }}
        </span>

        <!-- Tamaño -->
        <span class="text-surface-500 dark:text-surface-400">
          {{ item.tipo === 'carpeta' ? '—' : formatBytes(item.tamano_bytes) }}
        </span>

        <!-- Fecha -->
        <span class="text-surface-500 dark:text-surface-400">
          {{ formatDate(item.fecha_modificacion) }}
        </span>
      </div>
    </div>
  </div>
</template>