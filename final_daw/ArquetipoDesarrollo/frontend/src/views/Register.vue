<template>
  <div class="bg-surface-50 dark:bg-surface-950 px-6 py-20 md:px-20 lg:px-80">
    <div
      class="bg-surface-0 dark:bg-surface-900 p-8 md:p-12 shadow-sm rounded-2xl w-full max-w-md mx-auto flex flex-col gap-8">

      <div class="flex flex-col items-center gap-4">
        <div class="text-2xl font-semibold text-center text-surface-900 dark:text-surface-0">
          Crea tu cuenta
        </div>
        <div class="text-center text-surface-600 dark:text-surface-300">
          ¿Ya tienes una cuenta?
          <router-link to="/" class="text-primary font-medium ml-1 cursor-pointer hover:text-primary-emphasis">
            Inicia sesión
          </router-link>
        </div>
      </div>

      <div class="flex flex-col gap-6 w-full">
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nombre</label>
            <InputText v-model="nombre" type="text" placeholder="Tu nombre"
              class="w-full px-3 py-2 shadow-sm rounded-lg" @input="error = false" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Apellidos</label>
            <InputText v-model="apellidos" type="text" placeholder="Tus apellidos"
              class="w-full px-3 py-2 shadow-sm rounded-lg" @input="error = false" />
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium">Correo electrónico</label>
          <InputText v-model="email" type="email" placeholder="Correo electrónico"
            class="w-full px-3 py-2 shadow-sm rounded-lg" @input="error = false" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium">Contraseña</label>
          <Password v-model="password" placeholder="Contraseña" :toggleMask="true" :feedback="true"
            input-class="w-full!" @input="error = false">
            <template #header>
              <div class="font-semibold text-sm mb-4">Elige una contraseña</div>
            </template>
            <template #footer>
              <ul class="pl-2 ml-2 my-0 leading-6 text-sm">
                <li>Mínimo 8 caracteres</li>
              </ul>
            </template>
          </Password>
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium">Repetir contraseña</label>
          <Password v-model="confirmPassword" placeholder="Repite tu contraseña" :toggleMask="true" :feedback="false"
            input-class="w-full!" @input="error = false" />
        </div>

        <div v-if="error"
          class="flex items-center gap-2 text-red-500 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800/30">
          <i class="pi pi-exclamation-triangle text-lg"></i>
          <span class="text-sm md:text-base font-medium">
            {{ errorMessage || 'Revisa los datos introducidos.' }}
          </span>
        </div>
      </div>

      <Button label="Registrarse" icon="pi pi-user-plus" class="w-full py-2 rounded-lg flex justify-center items-center gap-2"
        :loading="loading" @click="register" />
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

const nombre = ref('')

</script>