<script setup>
import { onMounted, ref, watch } from 'vue'
import FileTable from '../components/FileTable.vue'
import Breadcrumb from 'primevue/breadcrumb'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import api from '@/api/api'

// --- ESTADO ---
const cargandoTabla = ref(false)
const items = ref([])
const carpetaActualId = ref(null)
const itemsSeleccionados = ref([])

const modalNuevaCarpeta = ref(false)
const nombreNuevaCarpeta = ref('')

// --- BREADCRUMB ---
const breadcrumbInicio = ref({
  icon: 'pi pi-home',
  command: () => resetearBreadcrumb()
})

const rutaBreadcrumb = ref([])

// --- CARGA DE ITEMS ---
async function cargarItems(carpetaId = null) {
  cargandoTabla.value = true

  try {
    const response = await api.get('items/', {
      params: carpetaId ? { carpeta: carpetaId } : {}
    })

    items.value = response.data
    carpetaActualId.value = carpetaId

  } catch (error) {
    console.error("Error cargando items:", error)

  } finally {
    cargandoTabla.value = false
    itemsSeleccionados.value = []
  }
}

// --- NAVEGACIÓN ---

function abrirCarpeta(carpeta) {
  if (carpeta.tipo !== 'carpeta') return

  rutaBreadcrumb.value.push({
    label: carpeta.nombre,
    id: carpeta.id,
    command: () => navegarBreadcrumb(carpeta.id)
  })

  cargarItems(carpeta.id)
}

function navegarBreadcrumb(carpetaId) {
  const index = rutaBreadcrumb.value.findIndex(r => r.id === carpetaId)

  if (index !== -1) {
    rutaBreadcrumb.value = rutaBreadcrumb.value.slice(0, index + 1)
  }

  cargarItems(carpetaId)
}

function resetearBreadcrumb() {
  rutaBreadcrumb.value = []
  cargarItems(null)
  carpetaActualId.value = null
}

// --- MODAL CREAR CARPETA ---

function cerrarModalNuevaCarpeta() {
  modalNuevaCarpeta.value = false
  nombreNuevaCarpeta.value = ''
}

async function crearCarpeta() {
  try {
    await api.post('items/', {
      nombre: nombreNuevaCarpeta.value,
      tipo: "carpeta",
      padre: carpetaActualId.value
    })

    cerrarModalNuevaCarpeta()
    cargarItems(carpetaActualId.value)

  } catch (error) {
    console.error("Error creando carpeta:", error)
  }
}

// --- WATCHERS ---
watch(itemsSeleccionados, (nuevoValor) => {
  console.log('items seleccionados:', nuevoValor)
}, { deep: true })

// --- INIT ---
onMounted(() => {
  cargarItems()
})
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Botón para abrir el modal -->
    <Button 
      icon="pi pi-folder" 
      label="Nueva carpeta" 
      @click="modalNuevaCarpeta = true" 
    />
    
    <!-- Breadcrumb sincronizado con rutaBreadcrumb -->
    <Breadcrumb 
      :home="breadcrumbInicio" 
      :model="rutaBreadcrumb" 
    />

    <!-- Tabla de items sincronizada -->
    <FileTable
      :items="items"
      :loading="cargandoTabla" 
      v-model:seleccionados="itemsSeleccionados"
      @open="abrirCarpeta"
    />

    <!-- Modal de Nueva Carpeta -->
    <Dialog 
      v-model:visible="modalNuevaCarpeta" 
      header="Nueva Carpeta" 
      :style="{ width: '25rem' }" 
      modal
      :draggable="false"
      :closable="false"
    >
      <div class="flex flex-col gap-2 mb-4">
        <InputText 
          id="folderName" 
          v-model="nombreNuevaCarpeta" 
          class="flex-auto" 
          autocomplete="off" 
          placeholder="Introduzca el nombre de la carpeta"
          @keyup.enter="crearCarpeta" 
          autofocus
        />
      </div>

      <template #footer>
        <Button 
          label="Cancelar" 
          text 
          severity="secondary" 
          @click="cerrarModalNuevaCarpeta" 
        />
        <Button 
          label="Crear" 
          @click="crearCarpeta" 
          :disabled="!nombreNuevaCarpeta.trim()" 
        />
      </template>
    </Dialog>
  </div>
</template>