<template>
  <aside class="w-64 h-full bg-surface-0 dark:bg-surface-900 border-r border-surface-200 dark:border-surface-800 flex flex-col p-3">
    <nav class="flex flex-col gap-1">
      
      <button
        v-for="item in items"
        :key="item.key"
        @click="setActive(item.key)"

        :class="[
          'flex items-center gap-5 px-3 py-2 rounded-lg transition-all duration-200 cursor-pointer border-none outline-none',
          active === item.key 
            ? 'bg-primary text-primary-contrast shadow-sm' 
            : 'text-surface-700 dark:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-800'
        ]"
      >
        <i :class="[item.icon, 'text-lg']"></i>
        <span class="font-medium">{{ item.label }}</span>
      </button>

    </nav>
  </aside>
</template>

<script setup>
import { ref } from "vue";

const active = ref("home");

const items = [
  { key: "home", label: "Página principal", icon: "pi pi-home" },
  { key: "drive", label: "Mi unidad", icon: "pi pi-folder" },
  { key: "starred", label: "Favoritos", icon: "pi pi-star" },
  { key: "recent", label: "Reciente", icon: "pi pi-clock" },
];

const setActive = (key) => active.value = key;
</script>