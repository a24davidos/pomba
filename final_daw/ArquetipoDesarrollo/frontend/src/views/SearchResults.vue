<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="p-6">
    <p class="text-surface-500">Buscando: {{ route.query.q }}</p>
  </div>
</template>
