<template>
  <aside class="w-55 h-full  flex flex-col p-3">
    <nav class="flex flex-col gap-1">
      <ContextMenu ref="menu" :model="trashMenuItems" />
      <button
        v-for="item in items"
        :key="item.key"
        @click="setActive(item.key)"
        @contextmenu.prevent="item.key === 'trash' && onTrashRightClick($event)"
        :class="[
          'flex items-center gap-5 px-3 py-2 rounded-lg transition-all duration-200 cursor-pointer border-none outline-none text-sm',
          active === item.key 
            ? 'bg-primary text-primary-contrast shadow-sm' 
            : 'text-surface-700 dark:text-surface-200 hover:bg-surface-200 dark:hover:bg-surface-800'
        ]"
      >
        <i :class="[item.icon, 'text-base']"></i>
        <span class="font-medium">{{ item.label }}</span>
      </button>

    </nav>
  </aside>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import ContextMenu from "primevue/contextmenu";
import api from '@/api/api'


const route = useRoute();
const router = useRouter();

const menu = ref(null);

const trashMenuItems = [
  {
    label: "Vaciar papelera",
    icon: "pi pi-trash",
    command: async () => {
      try {
        const response = await api.post("items/vaciar_papelera/")
      } catch (error){
        console.log("Error vaciando la papelera:", error);
      }
    }
  },
  {
    label: "Restaurar todo",
    icon: "pi pi-replay",
    command: () => {
      console.log("Restaurar todo");
    }
  }
];

const active = computed(() => route.params.view || 'drive');

const items = [
  { key: "drive", label: "Mi unidad", icon: "pi pi-folder" },
  { key: "fav", label: "Favoritos", icon: "pi pi-star" },
  { key: "recent", label: "Reciente", icon: "pi pi-clock" },
  { key: "trash", label: "Papelera", icon: "pi pi-trash" },
];


const setActive = (key) => {
  router.push({name: 'home', params: {view: key}})
}

const onTrashRightClick = (event) => {
  menu.value.show(event);
};

</script>