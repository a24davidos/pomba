<script setup>
import { ref, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useItemsStore } from "@/stores/items";

import FileTable from "../components/FileTable.vue";
import Breadcrumb from "primevue/breadcrumb";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";

// --- ESTADO ---
const store = useItemsStore();

const route = useRoute();
const router = useRouter();

const itemsSeleccionados = ref([]);

const fileInput = ref(null);

const modalNuevaCarpeta = ref(false);
const inputNuevaCarpeta = ref("");

const modalRenombrar = ref(false);
const inputRenombrar = ref("");

// ---VISTAS---
const CONFIGURACION_VISTAS = {
  drive: {
    titulo: "Mi unidad",
    icono: "pi pi-folder",
    paramsBase: { papelera: "false", favoritos: "false" },
  },

  trash: {
    titulo: "Papelera",
    icono: "pi pi-trash",
    paramsBase: { papelera: "true" },
  },

  fav: {
    titulo: "Favoritos",
    icono: "pi pi-star",
    paramsBase: { papelera: "false", favorito: "true" },
  },

  recent: {
    titulo: "Recientes",
    icono: "pi pi-clock",
    paramsBase: {},
  },
};

const breadcrumbInicio = computed(() => {
  const vistaActual = route.params.view || "drive";
  const config = CONFIGURACION_VISTAS[vistaActual];

  return {
    label: config?.titulo || "Mi unidad",
    icon: config?.icono || "pi pi-home",

    command: () => {
      router.push({
        name: "home",
        params: {
          view: vistaActual,
        },
      });
    },
  };
});

const rutaBreadcrumb = computed(() => {
  return store.breadcrumb
    .filter((nodo) => nodo.id !== null)
    .map((nodo) => ({
      label: nodo.label,
      id: nodo.id,

      command: () => {
        router.push({
          name: "home",
          params: {
            view: route.params.view || "drive",
            folderId: nodo.id,
          },
        });
      },
    }));
});

function cargarDesdeRuta() {
  const vista = route.params.view || "drive";
  const folderId = route.params.folderId || null;

  const config = CONFIGURACION_VISTAS[vista] || CONFIGURACION_VISTAS.drive;

  return store.cargarItems({
    ...config.paramsBase,
    carpeta: folderId,
  });
}

function abrirCarpeta(carpeta) {
  if (carpeta.tipo !== "carpeta") return;

  router.push({
    name: "home",
    params: {
      view: route.params.view || "drive",
      folderId: carpeta.id,
    },
  });
}

function abrirSelectorArchivo() {
  fileInput.value?.click();
}

async function subirArchivo(event) {
  const archivo = event.target.files[0];

  if (!archivo) return;

  const formData = new FormData();

  formData.append("nombre", archivo.name);
  formData.append("tipo", "archivo");
  formData.append("file", archivo);

  const idPadre = route.params.folderId || null;

  if (idPadre) {
    formData.append("padre", idPadre);
  }

  await store.subirArchivo(formData);

  await cargarDesdeRuta();

  event.target.value = "";
}

function cerrarModal() {
  modalNuevaCarpeta.value = false;
  inputNuevaCarpeta.value = "";

  modalRenombrar.value = false;
  inputRenombrar.value = "";
}

async function crearCarpeta() {
  const idPadre = route.params.folderId || null;

  await store.crearCarpeta({
    nombre: inputNuevaCarpeta.value,
    tipo: "carpeta",
    padre: idPadre,
  });

  cerrarModal();

  await cargarDesdeRuta();
}

async function eliminar() {
  const ids = itemsSeleccionados.value.map((item) => item.id);

  if (!ids.length) return;

  await store.eliminarItems(ids);

  itemsSeleccionados.value = [];

  await cargarDesdeRuta();
}

async function marcarFavoritos() {
  const ids = itemsSeleccionados.value.map((item) => item.id);

  if (!ids.length) return;

  await store.marcarFavoritos(ids);

  itemsSeleccionados.value = [];

  await cargarDesdeRuta();
}

function abrirModalRenombrar() {
  if (itemsSeleccionados.value.length !== 1) return;

  inputRenombrar.value = itemsSeleccionados.value[0].nombre;

  modalRenombrar.value = true;
}

async function renombrar() {
  if (itemsSeleccionados.value.length !== 1) return;

  const id = itemsSeleccionados.value[0].id;

  await store.renombrarItem(id, inputRenombrar.value);

  itemsSeleccionados.value = [];

  cerrarModal();

  await cargarDesdeRuta();
}

watch(
  () => [route.params.view, route.params.folderId],
  async () => {
    itemsSeleccionados.value = []

    await cargarDesdeRuta()
  },
  {
    immediate: true,
  },
)

</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Botón para abrir el modal -->

    <Button
      icon="pi pi-file"
      label="Nuevo archivo"
      @click="abrirSelectorArchivo"
    />

    <input ref="fileInput" type="file" class="hidden" @change="subirArchivo" />

    <Button
      icon="pi pi-folder"
      label="Nueva carpeta"
      @click="modalNuevaCarpeta = true"
    />

    <Button icon="pi pi-trash" label="Eliminar" @click="eliminar" />

    <Button
      icon="pi pi-star"
      label="Marcar Favorito"
      @click="marcarFavoritos"
    />

    <Button icon="pi pi-pencil" label="renombrar" @click="abrirModalRenombrar" />
    <!-- Breadcrumb sincronizado con rutaBreadcrumb -->
    <Breadcrumb :home="breadcrumbInicio" :model="rutaBreadcrumb" />

    <!-- Tabla de items sincronizada -->
    <FileTable
      :items="store.items"
      :loading="store.loading"
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
