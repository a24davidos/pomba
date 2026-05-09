<script setup>
import { onMounted, ref } from 'vue'
import FileTable from '../components/FileTable.vue'
import Breadcrumb from 'primevue/breadcrumb'
import api from '@/api/api'

const loading = ref(false)
const datos = ref([])

const currentFolder = ref(null)
const selectedItems = ref([])

// breadcrumb
const home = ref({
  icon: 'pi pi-home',
  command: () => goHome()
})

const items = ref([])

async function loadItems(folderId = null) {
  loading.value = true

  const res = await api.get('items/', {
    params: folderId ? { carpeta: folderId } : {}
  })

  datos.value = res.data
  loading.value = false
  currentFolder.value = folderId

  //reset selección SIEMPRE al cambiar carpeta
  selectedItems.value = []
}

// entrar en carpeta
function handlerAbrir(item) {
  if (item.tipo !== 'carpeta') return

  currentFolder.value = item.id

  items.value.push({
    label: item.nombre,
    id: item.id,
    command: () => goToFolder(item.id)
  })

  loadItems(item.id)
}

// breadcrumb click
function goToFolder(folderId) {  
  const index = items.value.findIndex(i => i.id === folderId)

  if (index !== -1) {
    items.value = items.value.slice(0, index + 1)
  }

  loadItems(folderId)
}

// home
function goHome() {
  items.value = []
  currentFolder.value = null
  loadItems(null)
}

onMounted(() => {
  loadItems()
})
</script>

<template>
  <Breadcrumb :home="home" :model="items" />

  <FileTable
    :items="datos"
    :loading="loading" 
    v-model:selected="selectedItems"
    @open="handlerAbrir"
  />
</template>