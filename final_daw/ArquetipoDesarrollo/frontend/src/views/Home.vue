<script setup>
import { onMounted, ref } from 'vue'
import FileTable from '../components/FileTable.vue';
import api from '@/api/api'

const datos = ref([])
const loading = ref(false)
const currentFolder = ref()

async function loadItems(folderId = null) {
  loading.value = true


  const res = await api.get('items/', {
    params: folderId ? { carpeta: folderId } : {}
  })

  datos.value = res.data
  loading.value = false

  currentFolder.value = folderId
}

function handlerAbrir(item) {
  if (item.tipo === 'carpeta') {
    loadItems(item.id)
  }
}

//Al cargar por primera vez cargamos la tabla
onMounted(loadItems)

</script>

<template>
  <FileTable :items="datos" :loading="loading" @open="handlerAbrir"/>
</template>