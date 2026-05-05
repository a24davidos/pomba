<script setup>
import { ref, onMounted } from "vue";
import Button from "primevue/button";

const isDark = ref(false);

const applyTheme = (dark) => {
  document.documentElement.classList.toggle("dark", dark);
  localStorage.setItem("theme", dark ? "dark" : "light");
};

const toggleDark = () => {
  isDark.value = !isDark.value;
  applyTheme(isDark.value);
};

onMounted(() => {
  const saved = localStorage.getItem("theme");

  // si hay guardado, lo usamos
  if (saved === "dark") {
    isDark.value = true;
    applyTheme(true);
  }
});
</script>

<template>
<Button
  :icon="isDark ? 'pi pi-moon' : 'pi pi-sun'"
  rounded
  text
  class="hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors duration-300"
  @click="toggleDark"
/>
</template>
