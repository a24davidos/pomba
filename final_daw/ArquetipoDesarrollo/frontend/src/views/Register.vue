<template>
  <div class="min-h-dvh bg-surface-50 dark:bg-surface-950 flex flex-col items-center justify-center px-6 py-8">

    <div class="fixed top-4 right-4 z-10">
      <ThemeToggle />
    </div>

    <div class="bg-surface-0 dark:bg-surface-900 p-8 md:p-12 shadow-sm rounded-2xl w-full max-w-sm flex flex-col gap-8">

      <!-- Logo + título -->
      <div class="flex flex-col items-center gap-4">
        <div class="flex items-center">
          <PombaLogo class="w-20 h-20 text-surface-900 dark:text-surface-0 shrink-0" />
        </div>

        <div class="flex flex-col items-center gap-2 w-full">
          <div class="text-surface-900 dark:text-surface-0 text-2xl font-semibold leading-tight text-center w-full">Crear cuenta</div>
          <div class="text-center w-full">
            <span class="text-surface-700 dark:text-surface-200 leading-normal">¿Ya tienes cuenta?</span>
            <router-link to="/" class="text-primary font-medium ml-1 cursor-pointer hover:underline">Inicia sesión</router-link>
          </div>
        </div>
      </div>

      <!-- Campos -->
      <Form v-slot="$form" :resolver="resolver" :initialValues="initialValues" @submit="onFormSubmit" class="flex flex-col gap-6 w-full">

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
          <div class="flex flex-col gap-2">
            <label class="text-surface-900 dark:text-surface-0 font-medium leading-normal">Nombre</label>
            <InputText name="nombre" placeholder="Tu nombre" class="w-full" />
            <Message v-if="$form.nombre?.invalid" severity="error" variant="simple" size="small">
              {{ $form.nombre.error.message }}
            </Message>
          </div>
          <div class="flex flex-col gap-2">
            <label class="text-surface-900 dark:text-surface-0 font-medium leading-normal">Apellidos</label>
            <InputText name="apellidos" placeholder="Tus apellidos" class="w-full" />
          </div>
        </div>

        <div class="flex flex-col gap-2 w-full">
          <label class="text-surface-900 dark:text-surface-0 font-medium leading-normal">Correo electrónico</label>
          <InputText name="email" type="email" placeholder="correo@ejemplo.com" class="w-full" />
          <Message v-if="$form.email?.invalid" severity="error" variant="simple" size="small">
            {{ $form.email.error.message }}
          </Message>
        </div>

        <div class="flex flex-col gap-2 w-full">
          <label class="text-surface-900 dark:text-surface-0 font-medium leading-normal">Contraseña</label>
          <Password name="password" placeholder="Mínimo 8 caracteres" :toggleMask="true" :feedback="false" input-class="w-full!" fluid />
          <Message v-if="$form.password?.invalid" severity="error" variant="simple" size="small">
            {{ $form.password.error.message }}
          </Message>
        </div>

        <div class="flex flex-col gap-2 w-full">
          <label class="text-surface-900 dark:text-surface-0 font-medium leading-normal">Repetir contraseña</label>
          <Password name="confirmPassword" placeholder="Confirma tu contraseña" :toggleMask="true" :feedback="false" input-class="w-full!" fluid />
          <Message v-if="$form.confirmPassword?.invalid" severity="error" variant="simple" size="small">
            {{ $form.confirmPassword.error.message }}
          </Message>
        </div>

        <div v-if="registroExitoso" class="flex items-center gap-2 text-green-600 bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-200 dark:border-green-800/30 text-sm">
          <i class="pi pi-check-circle shrink-0" />
          <span>¡Cuenta creada! Entrando...</span>
        </div>

        <div v-if="apiError" class="flex items-center gap-2 text-red-500 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800/30 text-sm">
          <i class="pi pi-exclamation-triangle shrink-0" />
          <span>{{ apiErrorMessage }}</span>
        </div>

        <Button type="submit" label="Crear cuenta" icon="pi pi-user-plus" class="w-full mt-4" :loading="loading" :disabled="registroExitoso" />
      </Form>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Form } from '@primevue/forms'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ThemeToggle from '@/components/ThemeToggle.vue'
import PombaLogo from '@/components/PombaLogo.vue'
import { authService } from '@/api/auth'
import { getErrorMessage } from '@/utils/errors'
import router from '@/router'

const loading = ref(false)
const registroExitoso = ref(false)
const apiError = ref(false)
const apiErrorMessage = ref('')

const initialValues = ref({ nombre: '', apellidos: '', email: '', password: '', confirmPassword: '' })

const resolver = ({ values }) => {
  const errors = {}
  if (!values.nombre) errors.nombre = [{ message: 'El nombre es obligatorio.' }]
  if (!values.email) {
    errors.email = [{ message: 'El correo es obligatorio.' }]
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = [{ message: 'Formato de correo inválido.' }]
  }
  if (!values.password) {
    errors.password = [{ message: 'La contraseña es obligatoria.' }]
  } else if (values.password.length < 8) {
    errors.password = [{ message: 'Mínimo 8 caracteres.' }]
  }
  if (!values.confirmPassword) {
    errors.confirmPassword = [{ message: 'Debes repetir la contraseña.' }]
  } else if (values.confirmPassword !== values.password) {
    errors.confirmPassword = [{ message: 'Las contraseñas no coinciden.' }]
  }
  return { errors }
}

const onFormSubmit = async (event) => {
  if (!event.valid) return
  loading.value = true
  apiError.value = false
  apiErrorMessage.value = ''
  const { states } = event
  try {
    await authService.register(
      states.email.value.trim(),
      states.password.value,
      states.nombre.value,
      states.apellidos.value || ''
    )
    registroExitoso.value = true
    setTimeout(async () => {
      await authService.login(states.email.value.trim(), states.password.value)
      router.push('/home')
    }, 1500)
  } catch (error) {
    apiError.value = true
    apiErrorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}
</script>
