<script setup>
import { ref, watch } from 'vue'
import { useGestorItems } from '@/stores/items'
import { apiItems } from '@/api/items'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

const gestor = useGestorItems()

const carpetaPickerId = ref(null)
const carpetasEnPicker = ref([])
const breadcrumbPicker = ref([{ label: 'Mi unidad', id: null }])
const cargandoPicker = ref(false)
const idsMoviendo = ref([])
let tokenPicker = 0

watch(() => gestor.modal, async (modal) => {
  if (modal.open && modal.name === 'mover') {
    carpetaPickerId.value = null
    breadcrumbPicker.value = [{ label: 'Mi unidad', id: null }]
    idsMoviendo.value = modal.payload?.ids ?? []
    await cargarCarpetasEnPicker(null)
  }
}, { deep: true }) //observa cambios en propiedades internas del objeto, no solo si cambia su referencia (Por eso no me funcionaba, necesitas que cambie la referencia de dentro)

async function cargarCarpetasEnPicker(carpetaId) {
  const token = ++tokenPicker
  cargandoPicker.value = true
  try {
    const params = { papelera: 'false' }
    if (carpetaId) params.carpeta = carpetaId
    const data = await apiItems.listar(params)
    if (token !== tokenPicker) return
    carpetasEnPicker.value = data.items.filter(
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

async function irABreadcrumbPicker(id) {
  const nodo = breadcrumbPicker.value[id]
  breadcrumbPicker.value = breadcrumbPicker.value.slice(0, id + 1)
  carpetaPickerId.value = nodo.id
  await cargarCarpetasEnPicker(nodo.id)
}

async function confirmarMover() {
  await gestor.moverItems(idsMoviendo.value, carpetaPickerId.value)
  gestor.cerrarModal()
}
</script>

<template>
  <Dialog
    v-if="gestor.modal.name === 'mover'"
    v-model:visible="gestor.modal.open"
    header="Mover a..."
    :style="{ width: '28rem' }"
    modal :draggable="false" :closable="false"
  >
    <!-- Breadcrumb del picker -->
    <div class="flex items-center gap-1 text-sm mb-3 flex-wrap min-h-6">
      <template v-for="(nodo, indice) in breadcrumbPicker" :key="indice">
        <span v-if="indice > 0" class="text-surface-300 dark:text-surface-600 select-none">›</span>
        <button
          v-if="indice < breadcrumbPicker.length - 1"
          @click="irABreadcrumbPicker(indice)"
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
      <Button label="Cancelar" text severity="secondary" @click="gestor.cerrarModal" />
      <Button label="Mover aquí" icon="pi pi-check" @click="confirmarMover" />
    </template>
  </Dialog>
</template>
