<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from "vue-router";

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

const route = useRoute();
const router = useRouter();

// --- BREADCRUMB ---
// El home siempre es fijo
const breadcrumbInicio = ref({
  icon: 'pi pi-home',
  command: () => cargarItems(null) // Carga la raíz
})

const rutaBreadcrumb = ref([])


const CONFIGURACION_VISTAS = {
  drive: {
    titulo: 'Mi unidad',
    paramsBase: { papelera: 'false', favoritos: 'false' }
  },
  trash: {
    titulo: 'Papelera',
    paramsBase: { papelera: 'true' }
  },
  fav: {
    titulo: 'Mis favoritos',
    paramsBase: {papelera: 'false', favorito: 'true'}
  }
}

const actualizarBreadcrumb = (data) => {
  const breadcrumbData = data || [];
  
  rutaBreadcrumb.value = breadcrumbData
    .filter(nodo => nodo.id !== null) 
    .map(nodo => ({
      label: nodo.label,
      id: nodo.id,
      command: () => cargarItems(nodo.id) 
    }));
};

// --- CARGA DE ITEMS ---
async function cargarItems(carpetaId = null) {
  cargandoTabla.value = true;

  //Identificamos en qué vista estamos (por defecto 'drive')
  const vistaActual = route.params.view || 'drive';
  
  //Obtenemos la configuración de esa vista
  const config = CONFIGURACION_VISTAS[vistaActual] || CONFIGURACION_VISTAS.drive;

  const parametros = {
    ...config.paramsBase, // Copiamos los filtros base (papelera, fav, etc.)
    carpeta: carpetaId    // Añadimos la carpeta si existe
  };

  try {
    const response = await api.get('items/', { params: parametros });

    items.value = response.data.items;
    carpetaActualId.value = carpetaId;
    
    // Actualización del breadcrumb...
    actualizarBreadcrumb(response.data.breadcrumb);

  } catch (error) {
    console.error("Error cargando items:", error);
  } finally {
    cargandoTabla.value = false;
    itemsSeleccionados.value = [];
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

async function marcarFavoritos() {
  const seleccion = [itemsSeleccionados.value].flat();
  const ids = seleccion.map(item => item.id);

  if (ids.length === 0) return;

  const url = "items/favorito/"

  try{
    await api.post(url, {ids:ids})
    itemsSeleccionados.value = []
  } catch (error){
    console.error("Error al marcar como favorito", error)
  }
}

//CONTROLAR AQUI QUE NO SE PUEDA RENOMBRAR MAS DE UNO A LA VEZ, O POR LO MENOS QUE NO DE LA OPCION NOSE SI DEBERÍA DE MANDAR UN MENSAJE O QUE
async function renombrar(){
  //Solo debería de dejar coger 1!!!!
  if (itemsSeleccionados.value.length !== 1){
    return
  }
  
  const id = itemsSeleccionados.value[0].id

  const url = `items/${id}/renombrar/`
  
  try{
    await api.post(url, {nombre: "probando si va"})
    cargarItems(carpetaActualId.value);
    itemsSeleccionados.value = []; 
  } catch (error){
    console.error("Erorr al renombrar", error)
  }

  
}


// --- WATCHERS ---
watch(itemsSeleccionados, (nuevoValor) => {
  console.log('items seleccionados:', nuevoValor)
}, { deep: true })

watch(() => route.params.view, () => {
  // Cuando cambias de sección, reseteamos a la raíz (carpetaId = null)
  cargarItems(null);
});

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

    <Button
      icon="pi pi-star"
      label="Marcar Favorito"
      @click="marcarFavoritos"
    />

    <Button
      icon="pi pi-pencil"
      label="renombrar"
      @click="renombrar"
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