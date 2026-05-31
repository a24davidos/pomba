<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import { useGestorItems } from '@/stores/items'
import FileTable from '@/components/FileTable.vue'
import Button from 'primevue/button'
import Divider from 'primevue/divider'

const route = useRoute()
const gestor = useGestorItems()

watch(
  () => route.query.q,
  (q) => { if (q) gestor.buscarItems(q) },
  { immediate: true }
)
</script>

<template>
  <div class="flex flex-col h-full">

    <!-- CABECERA -->
    <div class="px-4 pt-4 space-y-4 shrink-0">
      <div>
        <h1 class="text-lg font-semibold text-surface-900 dark:text-surface-0">
          Resultados para "{{ gestor.queryBusqueda }}"
        </h1>
        <p v-if="!gestor.loading" class="text-sm text-surface-500 mt-0.5">
          {{ gestor.items.length }} {{ gestor.items.length === 1 ? 'resultado' : 'resultados' }}
        </p>
      </div>

      <!-- ACTION BAR -->
      <div class="h-9 hidden sm:block">
        <Transition
          enter-active-class="transition-all duration-150 ease-out"
          enter-from-class="opacity-0 -translate-y-1"
          leave-active-class="transition-all duration-150 ease-in"
          leave-to-class="opacity-0 -translate-y-1"
        >
          <div
            v-if="gestor.itemsSeleccionados.length > 0"
            class="flex items-center gap-1
                   bg-surface-0 dark:bg-surface-900
                   border border-surface-200 dark:border-surface-700
                   rounded-full px-2 py-1 h-9 w-fit"
          >
            <div class="flex items-center gap-2 pr-3 border-r border-surface-200 dark:border-surface-700 mr-1">
              <button
                @click="gestor.limpiarSeleccion()"
                aria-label="Deseleccionar todo"
                class="w-6 h-6 rounded-full flex items-center justify-center
                       text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-800
                       transition-colors cursor-pointer"
              >
                <i class="pi pi-times text-xs" />
              </button>
              <span class="text-xs font-medium whitespace-nowrap">
                {{ gestor.itemsSeleccionados.length }}
                {{ gestor.itemsSeleccionados.length === 1 ? 'seleccionado' : 'seleccionados' }}
              </span>
            </div>

            <Button
              icon="pi pi-download"
              label="Descargar"
              text size="small" rounded
              :loading="gestor.descargando"
              @click="gestor.descargarItems()"
            />
            <Button icon="pi pi-arrow-right" label="Mover a..." text size="small" rounded @click="gestor.abrirModalMover()" />
            <Button
              v-if="gestor.itemsSeleccionados.length === 1"
              icon="pi pi-pencil" label="Renombrar" text size="small" rounded
              @click="gestor.abrirModalRenombrar()"
            />
            <Divider layout="vertical" class="h-4! mx-1!" />
            <Button
              icon="pi pi-trash" label="Eliminar" text size="small" rounded severity="danger"
              @click="gestor.eliminarItems(gestor.itemsSeleccionados.map(i => i.id))"
            />
          </div>
        </Transition>
      </div>
    </div>

    <!-- LOADING -->
    <div v-if="gestor.loading" class="flex-1 flex items-center justify-center">
      <i class="pi pi-spin pi-spinner text-2xl text-surface-400" />
    </div>

    <!-- SIN RESULTADOS -->
    <div
      v-else-if="!gestor.items.length"
      class="flex-1 flex flex-col items-center justify-center gap-3 text-surface-400"
    >
      <i class="pi pi-search text-5xl" />
      <p class="text-sm">No se encontraron resultados para "{{ gestor.queryBusqueda }}"</p>
    </div>

    <!-- TABLA DE RESULTADOS -->
    <div
      v-else
      class="flex-1 min-h-0 overflow-auto pb-24 lg:pb-0
             [&::-webkit-scrollbar]:w-1.5
             [&::-webkit-scrollbar-track]:bg-transparent
             [&::-webkit-scrollbar-thumb]:rounded-full
             [&::-webkit-scrollbar-thumb]:bg-surface-300
             dark:[&::-webkit-scrollbar-thumb]:bg-surface-600"
    >
      <FileTable @rename="gestor.abrirModalRenombrar" @move="gestor.abrirModalMover" />
    </div>

  </div>
</template>
