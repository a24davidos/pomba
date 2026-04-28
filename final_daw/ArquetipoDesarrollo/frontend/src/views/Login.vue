<template>
  <div class="bg-surface-50 dark:bg-surface-950 px-6 py-20 md:px-20 lg:px-80">
    <div
      class="bg-surface-0 dark:bg-surface-900 p-8 md:p-12 shadow-sm rounded-2xl w-full max-w-sm mx-auto flex flex-col gap-8">

      <!-- HEADER -->
      <div class="flex flex-col items-center gap-4">
        <div class="text-2xl font-semibold text-center text-surface-900 dark:text-surface-0">
          Bienvenido!
        </div>
        <div class="text-center text-surface-600 dark:text-surface-300">
          ¿No tienes cuenta aún?
          <router-link to="/register" class="text-primary font-medium ml-1 cursor-pointer hover:text-primary-emphasis">
            Registrate!
          </router-link>
        </div>
      </div>

      <!-- FORM -->
      <div class="flex flex-col gap-6 w-full">

        <!-- EMAIL -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Correo electrónico</label>
          <InputText v-model="email" type="email" placeholder="Correo electrónico"
            class="w-full px-3 py-2 shadow-sm rounded-lg" @input="error = false" />
        </div>

        <!-- PASSWORD -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Contraseña</label>
          <Password v-model="password" placeholder="Contraseña" :toggleMask="true" :feedback="false"
            input-class="w-full!" @input="error = false" />
        </div>

        <!-- ERROR -->
        <div v-if="error"
          class="flex items-center gap-2 text-red-500 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800/30">
          <i class="pi pi-exclamation-triangle text-lg"></i>
          <span class="text-sm md:text-base font-medium">
            El correo o la contraseña no son correctos.
          </span>
        </div>

        <!-- FORGOT -->
        <div class="flex justify-center md:justify-end">
          <a class="text-primary font-medium cursor-pointer hover:text-primary-emphasis text-center md:text-right">
            ¿Has olvidado tu contraseña?
          </a>
        </div>
      </div>


      <Button label="Entrar" icon="pi pi-user" class="w-full py-2 rounded-lg flex justify-center items-center gap-2"
        :loading="loading" @click="login" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import { authService } from '@/api/auth'

// STATE
const email = ref('')
const password = ref('')
const error = ref(false)
const loading = ref(false)

const router = useRouter()

// LOGIN
const login = async () => {
  error.value = false
  loading.value = true

  try {
    await authService.login(email.value.trim(), password.value)
    router.push('/home')
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}
</script>