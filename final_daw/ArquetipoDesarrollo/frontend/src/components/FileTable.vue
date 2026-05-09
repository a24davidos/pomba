<template>
  <section class="w-full">
    <h2 class="text-xl font-bold mb-4">{{ title }}</h2>

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
          <i
            :class="data.tipo === 'carpeta' ? 'pi pi-folder' : 'pi pi-file'"
            class="mr-2"
          ></i>

          <span @click="abrirItem(data)" class="cursor-pointer hover:underline">
            {{ data.nombre }}
          </span>
        </template>
      </Column>

      <Column field="tipo" header="Tipo" />
      <Column field="tamano_bytes" header="Tamaño" />
      <Column field="fecha_modificacion" header="Modificado">
        <template #body="{ data }">
        {{ formatDate(data.fecha_modificacion) }}
        </template>
      </Column>
    </DataTable>
  </section>
</template>

<script setup>
import { ref, defineEmits } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { formatDate } from '../utils/date';

const emit = defineEmits(['open'])

defineProps({
  items: { type: Array, default: () => [] },
  title: { type: String, default: 'Mi Unidad' },
  loading: { type: Boolean, default: true },
})

const selectedItems = ref([])

function abrirItem(item) {
    emit('open', item) 
}
</script>
