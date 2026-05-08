<script setup>
import { onMounted, ref } from 'vue'
import FileTable from '../components/FileTable.vue';
import api from '@/api/api'

const datos = ref([])
const loading = ref(false)


async function loadItems() {
  loading.value = true
  const res = await api.get('items/')  
  loading.value = false
  datos.value = res.data
  console.log(datos.value);
  
  
}

onMounted(loadItems)

</script>

<template>
  <FileTable :items="datos" :loading="loading"/>
</template>