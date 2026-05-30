<template>
  <div class="min-h-dvh bg-surface-50 dark:bg-surface-950 flex flex-col items-center justify-center px-6 py-8">

    <div class="fixed top-4 right-4 z-10">
      <ThemeToggle />
    </div>

    <div class="bg-surface-0 dark:bg-surface-900 p-8 md:p-12 shadow-sm rounded-2xl w-full max-w-sm flex flex-col gap-8">

      <!-- Logo + título -->
      <div class="flex flex-col items-center gap-4">
        <div class="flex items-center">
          <div class="w-20 h-20 text-surface-900 dark:text-surface-0 shrink-0">
            <svg viewBox="0 0 358 316" class="w-full h-full" fill="currentColor" aria-hidden="true">
              <path d="m309.01 239.53c-2.52-6.63-5.75-11.31-12.32-17.86-13.38-13.34-25.8-18.61-45.69-19.39-9.73-0.39-13.94-0.12-19 1.19-6.65 1.72-17.69 7.24-19.97 9.99-1.5 1.81-0.75 1.91 3.98 0.51 13.57-4.02 27.08-4.9 39.15-2.54 17.29 3.39 29.62 9.87 47.12 24.79 3.72 3.18 6.97 5.78 7.22 5.78 0.25 0 0.03-1.11-0.49-2.47zm-232.51-13.97c1.1-0.74 8.19-3.47 15.75-6.08l13.75-4.73 8.39 4.25c9.18 4.66 9.07 4.65 21.07 1.08q22.84-6.79 43.33 2.9l6.2 2.93 3.34-5.2c7.09-11.08 21.96-21.09 37.67-25.36 10.38-2.82 25.16-2.38 37.4 1.12l9.9 2.84 2.86-3.41c4.5-5.35 10.65-18.6 12.94-27.9 1.89-7.65 2.03-10.26 1.45-26-0.36-9.62-0.57-19.3-0.47-21.5 0.32-7.11 0.11-12.91-0.61-16.79-0.63-3.4-0.25-4.43 3.56-9.86l4.25-6.07-3.82-7.43c-6.1-11.84-15.23-18.78-28.27-21.47-10.75-2.22-23.19 1.41-31.78 9.28-6.7 6.14-11.58 14.16-15.86 26.05-2.03 5.66-5.23 14.33-7.11 19.27l-3.41 8.98 3.88 4.02c5.28 5.46 8.99 13.28 9.75 20.52 0.34 3.3 0.38 6 0.08 6-0.3 0-1.69-1.94-3.08-4.32-3.64-6.21-14.87-16.37-24.69-22.32-18.17-11.03-50.88-25.74-78.97-35.51-18.8-6.55-47.57-15.85-48.99-15.85-3.27 0 2.8 19.79 8.67 28.26 4.78 6.91 13.81 13.5 27.96 20.4 11.84 5.78 15.96 8.11 12.11 6.88-0.69-0.23-6.9-1.77-13.81-3.43-6.9-1.66-13.83-3.5-15.39-4.09l-2.84-1.08 0.6 5.03c1.96 16.52 12.92 25.81 37.65 31.89 6.01 1.48 11.25 3.01 11.65 3.41 1.12 1.13-17.53 0.86-24.02-0.34-3.18-0.59-6.01-0.85-6.28-0.58-0.27 0.28 0.73 3.22 2.23 6.56 8.14 18.13 34.53 28.36 64.71 25.08 11.79-1.29 25.03-5.37 34.43-10.63 3.54-1.97 6.64-3.37 6.91-3.11 0.71 0.72-6.6 9.63-11.85 14.45-5.83 5.34-16.22 10.57-25.45 12.8-11.22 2.72-33.97 1.74-44.79-1.92-4.4-1.49-10.54-4.25-13.64-6.14-6.05-3.68-7.14-3.88-52.36-9.46-8.8-1.09-17.01-2.21-18.25-2.5-2.96-0.68-2.96 1.72 0.02 6.93 3.6 6.29 5.93 7.39 18.59 8.78 11.82 1.29 12.13 1.84 2.14 3.79-7.6 1.48-8.67 2.26-7.27 5.33 1.67 3.66 7.04 9.43 11.86 12.75 4.8 3.3 5.12 3.36 7.91 1.5zm181.9-127.96c-2.9-2.9-3.4-4.09-3.4-8.1 0-10.89 12.1-17.5 18.72-10.23 6.03 6.62 5.51 14.25-1.33 19.64-4.27 3.36-9.85 2.83-13.99-1.31zm49.08 5.27c4.39-1.06 8.35-2.3 8.79-2.74 0.99-0.99-9.45-5.13-12.92-5.13-3.81 0-6.21 1.73-7.85 5.66-0.83 1.97-1.5 3.75-1.5 3.96 0 0.84 5.94 0.07 13.48-1.75z"/>
            </svg>
          </div>
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
