<template>
  <section class="w-full">

    <DataTable
      :value="items"
      v-model:selection="seleccionados"
      dataKey="id"
      selectionMode="multiple"
      class="w-full"
    >

    <Column selectionMode="multiple" headerStyle="width: 3rem" />

    <Column field="nombre" header="Nombre">
      <template #body="{ data }">
        <div
          @click="abrirItem(data)"
          class="flex items-center cursor-pointer hover:underline w-full"
        >
          <i
            :class="data.tipo === 'carpeta' ? 'pi pi-folder' : 'pi pi-file'"
            class="mr-2"
          ></i>

          <span>{{ data.nombre }}</span>
        </div>
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
import { computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { formatDate } from '../utils/date'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: Boolean,
})
//Uso este modelo para tener comunicación bidireccional
const seleccionados = defineModel('seleccionados', { default: [] })


const emit = defineEmits(['open'])



function abrirItem(item) {
  emit('open', item)
}
</script>