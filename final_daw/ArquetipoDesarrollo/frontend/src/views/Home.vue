<template>
  <section class="w-full">
    <h1 class="text-2xl font-bold mb-4">Mis archivos</h1>

    <DataTable
      :value="items"
      v-model:selection="selectedItems"
      dataKey="id"
      selectionMode="multiple"
      class="w-full"
      contextMenu
      v-model:contextMenuSelection="contextMenuItem"
      @rowContextmenu="onRowContextMenu"
    >
      <Column selectionMode="multiple" headerStyle="width: 3rem" />

      <Column field="nombre" header="Nombre">
        <template #body="{ data }">
          <i :class="data.tipo === 'carpeta' ? 'pi pi-folder' : 'pi pi-file'"></i>
          {{ data.nombre }}
        </template>
      </Column>

      <Column field="tipo" header="Tipo" />
      <Column field="tamano_bytes" header="Tamaño" />
      <Column field="fecha_modificacion" header="Modificado" />
    </DataTable>

    <!-- 🔥 CONTEXT MENU -->
    <ContextMenu ref="menu" :model="menuModel" />
  </section>
</template>
<script setup>
import { ref } from 'vue'
import ContextMenu from 'primevue/contextmenu'

const selectedItems = ref([])
const contextMenuItem = ref(null)
const menu = ref(null)

const items = ref([
  { id: 1, nombre: 'Documentos', tipo: 'carpeta' },
  { id: 2, nombre: 'foto.jpg', tipo: 'archivo' },
  { id: 3, nombre: 'proyecto.zip', tipo: 'archivo' },
  { id: 4, nombre: 'Música', tipo: 'carpeta' },
])

const menuModel = ref([
  {
    label: 'Abrir',
    icon: 'pi pi-folder-open',
    command: () => openItem(contextMenuItem.value)
  },
  {
    label: 'Renombrar',
    icon: 'pi pi-pencil',
    command: () => renameItem(contextMenuItem.value)
  },
  {
    label: 'Eliminar',
    icon: 'pi pi-trash',
    command: () => deleteItem(contextMenuItem.value)
  }
])

function onRowContextMenu(event) {
  contextMenuItem.value = event.data
  menu.value.show(event.originalEvent)
}

function openItem(item) {
  console.log('Abrir:', item)
}

function renameItem(item) {
  console.log('Renombrar:', item)
}

function deleteItem(item) {
  console.log('Eliminar:', item)
}
</script>

<style scoped>
    /* Quita el focus visual raro en filas */
  .p-datatable .p-datatable-tbody > tr:focus {
    outline: none;
    box-shadow: none;
  }

  .p-datatable .p-datatable-tbody > tr.p-highlight {
  background: transparent;
}
</style>