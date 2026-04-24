<template>
  <div class="landing p-8"> <h1 class="text-4xl font-bold text-surface-900 dark:text-surface-0 mb-4">
        Bienvenido a mi App
    </h1>
    
    <p class="text-surface-600 dark:text-surface-400 mb-6">
        Esta es la página de inicio para probar el router.
    </p>
    
    <div class="actions mb-8 text-5xl">
      <router-link to="/login" class="text-primary hover:underline font-medium">
        Ir al Login
      </router-link>
    </div>
    <h1>Hola</h1>
    <MiTarjeta />
  </div>
</template>
<script setup>
import MiTarjeta from '../components/MiTarjeta.vue'
</script>