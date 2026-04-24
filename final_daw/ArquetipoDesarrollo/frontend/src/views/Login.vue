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
          <a class="text-primary font-medium ml-1 cursor-pointer hover:text-primary-emphasis">
            Registrate!
          </a>
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
        <small v-if="error" class="text-red-500">
          Credenciales incorrectas
        </small>

        <!-- REMEMBER + FORGOT -->
        <div class="flex justify-end">
          <a class="text-primary font-medium cursor-pointer hover:text-primary-emphasis">
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
const remember = ref(true)
const error = ref(false)
const loading = ref(false)

const router = useRouter()

// LOGIN
const login = async () => {
  error.value = false
  loading.value = true

  try {
    await authService.login(email.value, password.value)

    if (remember.value) {
      // opcional: guardar token o flag
    }

    router.push('/home')
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}
</script>