<script setup>
import { ref, watch } from 'vue'
import { useGestorItems } from '@/stores/items'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

const gestor = useGestorItems()

const inputRenombrar = ref('')

watch(() => gestor.modal, (modal) => {
  if (modal.open && modal.name === 'renombrar') {
    inputRenombrar.value = modal.payload?.nombre || ''
  }
}, { deep: true })

async function renombrar() {
  const id = gestor.modal.payload.id
  const exito = await gestor.renombrarItem(id, inputRenombrar.value)
  if (exito) {
    gestor.cerrarModal()
    inputRenombrar.value = ''
  }
}
</script>

<template>
  <Dialog
    v-if="gestor.modal.name === 'renombrar'"
    v-model:visible="gestor.modal.open"
    header="Renombrar"
    :style="{ width: '25rem' }"
    modal :draggable="false" :closable="false"
  >
    <div class="flex flex-col gap-2 mb-4">
      <InputText
        v-model="inputRenombrar"
        class="flex-auto"
        autocomplete="off"
        placeholder="Nuevo nombre"
        @keyup.enter="renombrar"
        autofocus
      />
    </div>
    <template #footer>
      <Button label="Cancelar" text severity="secondary" @click="gestor.cerrarModal" />
      <Button label="Confirmar" @click="renombrar" :disabled="!inputRenombrar.trim()" />
    </template>
  </Dialog>
</template>
