<script setup>
import { useItemsStore } from '@/stores/items'
import { formatDate } from '../utils/date'

const store = useItemsStore()
const emit = defineEmits(['open'])

function handleClick(event, item, index) {
  if (event.shiftKey && store.seleccion.lastIndex !== null) {
    store.seleccionarRango(index)
    return
  }
  if (event.ctrlKey || event.metaKey) {
    store.toggleSeleccion(item, index)
    return
  }
  // Click normal: si es el único seleccionado, deselecciona
  if (store.seleccion.ids.length === 1 && store.seleccion.ids[0] === item.id) {
    store.limpiarSeleccion()
    return
  }
  store.seleccionar(item, index)
}

function handleDoubleClick(item) {
  store.limpiarSeleccion()
  emit('open', item)
}

function handleBackgroundClick(event) {
  if (event.target === event.currentTarget) {
    store.limpiarSeleccion()
  }
}

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
  <div class="w-full min-h-96 select-none" @click="handleBackgroundClick">

    <div class="grid grid-cols-[1fr_120px_100px_140px] gap-4 px-3 py-2 text-xs font-medium text-surface-400 dark:text-surface-500 border-b border-surface-100 dark:border-surface-800">
      <span>Nombre</span>
      <span>Tipo</span>
      <span>Tamaño</span>
      <span>Modificado</span>
    </div>

    <div v-if="store.loading" class="flex items-center justify-center py-16 text-surface-400">
      <i class="pi pi-spin pi-spinner text-2xl" />
    </div>

    <div
      v-else-if="!store.items.length"
      class="flex flex-col items-center justify-center py-16 gap-2 text-surface-400 dark:text-surface-500"
    >
      <i class="pi pi-folder-open text-4xl" />
      <span class="text-sm">Esta carpeta está vacía</span>
    </div>

    <div v-else>
      <div
        v-for="(item, index) in store.items"
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
        <div class="flex items-center gap-2 min-w-0">
          <i :class="[
            item.tipo === 'carpeta' ? 'pi pi-folder text-yellow-500' : 'pi pi-file text-surface-400',
            'text-base shrink-0',
          ]" />
          <span class="truncate">{{ item.nombre }}</span>
          <i v-if="item.favorito" class="pi pi-star-fill text-yellow-400 text-xs shrink-0" />
        </div>

        <span class="text-surface-500 dark:text-surface-400 capitalize">
          {{ item.tipo === 'carpeta' ? 'Carpeta' : (item.mime_type || 'Archivo') }}
        </span>

        <span class="text-surface-500 dark:text-surface-400">
          {{ item.tipo === 'carpeta' ? '—' : formatBytes(item.tamano_bytes) }}
        </span>

        <span class="text-surface-500 dark:text-surface-400">
          {{ formatDate(item.fecha_modificacion) }}
        </span>
      </div>
    </div>
  </div>
</template>