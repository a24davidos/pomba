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
// El home siempre es fijo
const breadcrumbInicio = ref({
  icon: 'pi pi-home',
  command: () => cargarItems(null) // Carga la raíz
})

const rutaBreadcrumb = ref([])

// --- CARGA DE ITEMS ---
async function cargarItems(carpetaId = null) {
  cargandoTabla.value = true

  try {
    const response = await api.get('items/', {
      params: carpetaId ? { carpeta: carpetaId } : {}
    })

    // Recogemos los Items que nos devuelve el servidor
    items.value = response.data.items 
    carpetaActualId.value = carpetaId

    // Actualizamos el breadcrumb automáticamente con lo que devuelve el servidor
    const breadcrumbData = response.data.breadcrumb || []
    
    rutaBreadcrumb.value = breadcrumbData
      .filter(nodo => nodo.id !== null) // Evitamos duplicar el "Inicio" que ya está en :home
      .map(nodo => ({
        label: nodo.label,
        id: nodo.id,
        command: () => cargarItems(nodo.id) // Navegación directa
      }))

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
  cargarItems(carpeta.id)
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


// --- SOFT DELETE ---
async function eliminar() {

  const seleccion = [itemsSeleccionados.value].flat();
  const idsParaEliminar = seleccion.map(item => item.id);

  if (idsParaEliminar.length === 0) return;

  const url = "items/trash/";

  try {
      await api.post(url, { ids: idsParaEliminar });
      cargarItems(carpetaActualId.value);
      itemsSeleccionados.value = []; 
    } catch (error) {
      console.error("Error al mover a la papelera:", error);
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
    
    <Button
      icon="pi pi-trash"
      label="Eliminar"
      @click="eliminar"
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