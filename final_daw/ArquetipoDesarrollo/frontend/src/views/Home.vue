<script setup>
import { onMounted, ref, watch, computed } from 'vue'
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
const itemsSeleccionados = ref([])

const fileInput = ref(null)

const modalNuevaCarpeta = ref(false)
const inputNuevaCarpeta = ref('')

const modalRenombrar = ref(false)
const inputRenombrar = ref('')

const route = useRoute();
const router = useRouter();

// --- BREADCRUMB ---
const breadcrumbInicio = computed(() => {
  const vistaActual = route.params.view || 'drive'
  const config = CONFIGURACION_VISTAS[vistaActual]

  return {
    label: config?.titulo || 'Mi unidad',
    icon: config?.icono || 'pi pi-home',
    command: () => {
      router.push({ 
        name: 'home', 
        params: { view: vistaActual }
      });
    }
  }
})
const rutaBreadcrumb = ref([])


const CONFIGURACION_VISTAS = {
  drive: {
    titulo: 'Mi unidad',
    icono: 'pi pi-folder',
    paramsBase: { papelera: 'false', favoritos: 'false' }
  },

  trash: {
    titulo: 'Papelera',
    icono: 'pi pi-trash',
    paramsBase: { papelera: 'true' }
  },

  fav: {
    titulo: 'Favoritos',
    icono: 'pi pi-star',
    paramsBase: { papelera: 'false', favorito: 'true' }
  },

  recent: {
    titulo: 'Recientes',
    icono: 'pi pi-clock',
    paramsBase: {}
  }
}

const actualizarBreadcrumb = (data) => {
  const breadcrumbData = data || [];
  
  rutaBreadcrumb.value = breadcrumbData
    .filter(nodo => nodo.id !== null) 
    .map(nodo => ({
      label: nodo.label,
      id: nodo.id,
      // Usamos router.push para que el botón "Atrás" funcione desde el breadcrumb también
      command: () => router.push({
        name: 'home',
        params: { view: route.params.view || 'drive', folderId: nodo.id }
      })
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
  if (carpeta.tipo !== 'carpeta') return;
  
  router.push({
    name: 'home',
    params: { 
      view: route.params.view || 'drive', 
      folderId: carpeta.id 
    }
  });
}

// --- SUBIR ARCHIVOS ---
function abrirSelectorArchivo() {
  fileInput.value?.click()
}

async function subirArchivo(event){
  const archivo = event.target.files[0]

  if (!archivo) return

  const formData = new FormData()

  formData.append("nombre", archivo.name)
  formData.append("tipo", "archivo")
  formData.append("file", archivo)

  const idPadre = route.params.folderId || null

  if (idPadre) {
    formData.append("padre", idPadre)
  }

  try {
    await api.post("items/", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    })

    await cargarItem(idPadre)

    console.log("Archivo subido correctamente");
  
  } catch (error){
    console.log("Error subiendo archivo: ", error);
  } finally {
    event.target.value = ""
  }
}

// --- MODAL CREAR CARPETA ---

function cerrarModal() {
  modalNuevaCarpeta.value = false
  inputNuevaCarpeta.value = ''
  modalRenombrar.value = false
  inputRenombrar.value = ""
}

async function crearCarpeta() {
  const idPadre = route.params.folderId || null
  try {
    await api.post('items/', {
      nombre: inputNuevaCarpeta.value,
      tipo: "carpeta",
      padre: idPadre
    })

    cerrarModal()
    cargarItems(idPadre)

  } catch (error) {
    console.error("Error creando carpeta:", error)
  }
}


// --- SOFT DELETE ---
async function eliminar() {
  const idPadre = route.params.folderId || null
  const seleccion = [itemsSeleccionados.value].flat();
  const idsParaEliminar = seleccion.map(item => item.id);

  if (idsParaEliminar.length === 0) return;

  const url = "items/trash/";

  try {
      await api.post(url, { ids: idsParaEliminar });
      cargarItems(idPadre);
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

function abirModalRenombrar() {
  inputRenombrar.value = itemsSeleccionados.value[0].nombre
  modalRenombrar.value = true
}

//CONTROLAR AQUI QUE NO SE PUEDA RENOMBRAR MAS DE UNO A LA VEZ, O POR LO MENOS QUE NO DE LA OPCION NOSE SI DEBERÍA DE MANDAR UN MENSAJE O QUE
async function renombrar(){
  //Solo debería de dejar coger 1!!!!

  if (itemsSeleccionados.value.length !== 1){
    return
  }
  const id = itemsSeleccionados.value[0].id
  const url = `items/${id}/renombrar/`
  const idPadre = route.params.folderId || null
  
  try{
    await api.post(url, {nombre: inputRenombrar.value})
    cargarItems(idPadre);
    itemsSeleccionados.value = [];
    cerrarModal()
  } catch (error){
    console.error("Error al renombrar", error)
  }

}

// --- WATCHERS ---
watch(itemsSeleccionados, (nuevoValor) => {
  console.log('items seleccionados:', nuevoValor)
}, { deep: true })

// Observamos tanto la vista (drive, trash...) como el folderId
watch(
  () => [route.params.view, route.params.folderId],
  ([nuevaVista, nuevoFolderId]) => {
    // Si cambia la vista o la carpeta en la URL, cargamos los datos correspondientes
    cargarItems(nuevoFolderId || null);
  },{ immediate: true }
);
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Botón para abrir el modal -->

    <Button
      icon="pi pi-file"
      label="Nuevo archivo"
      @click="abrirSelectorArchivo"
    />

    <input
      ref="fileInput"
      type="file"
      class="hidden"
      @change="subirArchivo"
    />

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
      @click="abirModalRenombrar"
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
          v-model="inputNuevaCarpeta" 
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
          @click="cerrarModal" 
        />
        <Button 
          label="Crear" 
          @click="crearCarpeta" 
          :disabled="!inputNuevaCarpeta.trim()" 
        />
      </template>
    </Dialog>

    <!-- Modal Renombrar -->
    <Dialog 
      v-model:visible="modalRenombrar" 
      header="Renombrar" 
      :style="{ width: '25rem' }" 
      modal
      :draggable="false"
      :closable="false"
    >
      <div class="flex flex-col gap-2 mb-4">
        <InputText 
          id="inputRename" 
          v-model="inputRenombrar" 
          class="flex-auto" 
          autocomplete="off" 
          placeholder="Introduzca el nuevo nombre"
          @keyup.enter="renombrar" 
          autofocus
        />
      </div>

      <template #footer>
        <Button 
          label="Cancelar" 
          text 
          severity="secondary" 
          @click="cerrarModal" 
        />
        <Button 
          label="Confirmar" 
          @click="renombrar" 
          :disabled="!inputRenombrar.trim()" 
        />
      </template>
    </Dialog>
  </div>
</template>