<template>
  <aside class="w-55 h-full flex flex-col p-3">

    <!-- BOTÓN NUEVO -->
    <Button
      label="Nuevo"
      icon="pi pi-plus"
      class="mb-4 w-full"
      rounded
      @click="toggleNuevoMenu"
    />

    <!-- MENU NUEVO -->
    <Menu
      ref="nuevoMenu"
      :model="nuevoMenuItems"
      popup
    />

    <!-- INPUT FILE OCULTO -->
    <input
      ref="fileInput"
      type="file"
      class="hidden"
      @change="subirArchivo"
    />

    <!-- MENU PAPELERA -->
    <ContextMenu
      ref="menu"
      :model="trashMenuItems"
    />

    <!-- NAVEGACIÓN -->
    <nav class="flex flex-col gap-1">

      <button
        v-for="item in items"
        :key="item.key"
        @click="setActive(item.key)"
        @contextmenu.prevent="item.key === 'trash' && modalPapelera($event)"
        :class="[
          'flex items-center gap-5 px-3 py-2 rounded-lg transition-all duration-200 cursor-pointer border-none outline-none text-sm',

          active === item.key
            ? 'bg-primary text-primary-contrast shadow-sm'
            : 'text-surface-700 dark:text-surface-200 hover:bg-surface-200 dark:hover:bg-surface-800'
        ]"
      >
        <i :class="[item.icon, 'text-base']"></i>

        <span class="font-medium">
          {{ item.label }}
        </span>
      </button>

    </nav>
  </aside>
</template>

<script setup>
import { ref, computed } from "vue";

import { useRoute, useRouter } from "vue-router";

import { useItemsStore } from "@/stores/items";

import ContextMenu from "primevue/contextmenu";
import Menu from "primevue/menu";
import Button from "primevue/button";

// ROUTER
const route = useRoute();
const router = useRouter();

// STORE
const store = useItemsStore();

// REFS
const menu = ref(null);

const nuevoMenu = ref(null);

const fileInput = ref(null);

// ACTIVE VIEW
const active = computed(() => route.params.view || "drive");

// ITEMS SIDEBAR
const items = [
  { key: "drive", label: "Mi unidad", icon: "pi pi-folder" },
  { key: "fav", label: "Favoritos", icon: "pi pi-star" },
  { key: "recent", label: "Reciente", icon: "pi pi-clock" },
  { key: "trash", label: "Papelera", icon: "pi pi-trash" },
];

// MENU NUEVO
const nuevoMenuItems = [
  {
    label: "Subir archivo",
    icon: "pi pi-upload",

    command: () => {
      fileInput.value?.click();
    }
  },

  {
    label: "Nueva carpeta",
    icon: "pi pi-folder",

    command: () => {
      store.abrirModal("crearCarpeta")
    }
  }
];

// MENU PAPELERA
const trashMenuItems = [
  {
    label: "Vaciar papelera",
    icon: "pi pi-trash",

    command: async () => {
      await store.vaciarPapelera();
    }
  },

  {
    label: "Restaurar todo",
    icon: "pi pi-replay",

    command: async () => {
      await store.restaurarPapelera();
    }
  }
];

// NAVEGACIÓN
const setActive = (key) => {
  router.push({
    name: "home",
    params: {
      view: key
    }
  });
};

// MENU PAPELERA
const modalPapelera = (event) => {
  menu.value.show(event);
};

// MENU NUEVO
const toggleNuevoMenu = (event) => {
  nuevoMenu.value.toggle(event);
};

// SUBIR ARCHIVO
async function subirArchivo(event) {
  const archivo = event.target.files[0];

  if (!archivo) return;

  const formData = new FormData();

  formData.append("nombre", archivo.name);

  formData.append("tipo", "archivo");

  formData.append("file", archivo);

  const folderId = route.params.folderId || null;

  if (folderId) {
    formData.append("padre", folderId);
  }

  await store.subirArchivo(formData);

  await store.cargarItems(store.currentParams);

  event.target.value = "";
}
</script>