<template>
  <div>
    <!-- Toggle global -->
    <div class="fixed top-4 right-4 z-50">
      <ThemeToggle />
    </div>

    <router-view />
  </div>
</template>

<script setup>
import ThemeToggle from '@/components/ThemeToggle.vue'
</script>