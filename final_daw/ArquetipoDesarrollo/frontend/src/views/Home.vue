<script setup>
import { onMounted, ref, watch } from 'vue'
import FileTable from '../components/FileTable.vue'
import Breadcrumb from 'primevue/breadcrumb'
import Button from 'primevue/button'
import api from '@/api/api'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'

// --- ESTADO ---
const isTableLoading = ref(false)
const fileList = ref([]) //Datos que vienen del backend
const currentFolderId = ref(null) 
const selectedFiles = ref([]) 
const modalNuevaCarpeta = ref(false)
const nuevoNombreCarpeta = ref('')

// --- BREADCRUMB ---
const breadcrumbHome = ref({
  icon: 'pi pi-home',
  command: () => resetBreadcrumb()
})
const breadcrumbSteps = ref([])

// --- ACCIONES ---

// Carga los archivos de la API
async function fetchFiles(folderId = null) {
  isTableLoading.value = true
  try {
    const response = await api.get('items/', {
      params: folderId ? { carpeta: folderId } : {}
    })
    fileList.value = response.data
    currentFolderId.value = folderId
  } catch (error) {
    console.error("Error cargando archivos:", error)
  } finally {
    isTableLoading.value = false
    selectedFiles.value = [] // Reset selección al navegar
  }
}

// Navegar a una carpeta (desde la tabla)
function navegarCarpeta(folder) {
  if (folder.tipo !== 'carpeta') return

  // Añadimos el paso al breadcrumb
  breadcrumbSteps.value.push({
    label: folder.nombre,
    id: folder.id,
    command: () => navegarBreadcrumb(folder.id)
  })

  fetchFiles(folder.id)
}

// Navegar desde el breadcrumb
function navegarBreadcrumb(folderId) {  
  const index = breadcrumbSteps.value.findIndex(step => step.id === folderId)

  if (index !== -1) {
    // Cortamos el camino del breadcrumb hasta la carpeta clickeada
    breadcrumbSteps.value = breadcrumbSteps.value.slice(0, index + 1)
  }
  fetchFiles(folderId)
}

function resetBreadcrumb() {
  breadcrumbSteps.value = []
  fetchFiles(null)
}


// --- WATCHERS ---
watch(selectedFiles, (newList) => {
  console.log('Archivos seleccionados:', newList)
}, { deep: true })


async function crearCarpeta(){
  try {
    const response = await api.post('items/', {
      nombre: nuevoNombreCarpeta.value,
      tipo: "carpeta",
      padre: currentFolderId.value
    })
    cerrarModalNuevaCarpeta()

    fetchFiles(currentFolderId.value)

  } catch (error) {
    console.error("Error cargando archivos:", error)
  }
}

function cerrarModalNuevaCarpeta() {
  modalNuevaCarpeta.value = false 
  nuevoNombreCarpeta.value = ''
}

onMounted(() => {
  fetchFiles()
})
</script>

<template>
  <div class="p-4 space-y-4">
    <Button icon="pi pi-folder" label="Nueva carpeta" @click="modalNuevaCarpeta = true" />
    
    <Breadcrumb :home="breadcrumbHome" :model="breadcrumbSteps" />

    <FileTable
      :items="fileList"
      :loading="isTableLoading" 
      v-model:seleccionados="selectedFiles"
      @open="navegarCarpeta"
    />

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
        v-model="nuevoNombreCarpeta" 
        class="flex-auto" 
        autocomplete="off" 
        placeholder="Introduzca el nombre de la carpeta"
        @keyup.enter="crearCarpeta" 
      />
    </div>

    <template #footer>
      <Button label="Cancelar" text severity="secondary" @click="cerrarModalNuevaCarpeta" />
      <Button label="Crear" @click="crearCarpeta" :disabled="!nuevoNombreCarpeta.trim()" />
    </template>
    </Dialog>
  </div>
</template>