<template>
  <section class="w-full">
    <h1 class="text-2xl font-bold mb-4 ">Mis archivos</h1>
    <DataTable
    :value="items"
    v-model:selection="selectedItems"
    dataKey="id"
    selectionMode="multiple"
    class="w-full"
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
  </section>
</template>

<script setup>
import { ref, watch } from 'vue';
import ThemeToggle from '@/components/ThemeToggle.vue'

const selectedItems = ref([])

const items = [
  { id: 1, nombre: 'Documentos', tipo: 'carpeta', tamano_bytes: null, fecha_modificacion: '2024-06-01' },
  { id: 2, nombre: 'foto.jpg', tipo: 'archivo', tamano_bytes: 204800, fecha_modificacion: '2024-05-28' },
  { id: 3, nombre: 'proyecto.zip', tipo: 'archivo', tamano_bytes: 5120000, fecha_modificacion: '2024-05-30' },
  { id: 4, nombre: 'Música', tipo: 'carpeta', tamano_bytes: null, fecha_modificacion: '2024-06-02' },
]

watch(selectedItems, (newVal) => {
  console.log('Elementos seleccionados:', newVal.length);
})

</script>