<template>
  <div class="bg-surface-50 dark:bg-surface-950 px-6 py-20 md:px-20 lg:px-80">
    <div class="bg-surface-0 dark:bg-surface-900 p-8 md:p-12 shadow-sm rounded-2xl w-full max-w-md mx-auto flex flex-col gap-8">
      
      <div class="flex flex-col items-center gap-4">
        <h1 class="text-2xl font-semibold text-center text-surface-900 dark:text-surface-0">
          Crea tu cuenta
        </h1>
        <p class="text-center text-surface-600 dark:text-surface-300">
          ¿Ya tienes una cuenta?
          <router-link to="/" class="text-primary font-medium ml-1 cursor-pointer hover:text-primary-emphasis">
            Inicia sesión
          </router-link>
        </p>
      </div>

      <!-- FORMULARIO -->
      <Form 
        v-slot="$form" 
        :resolver="resolver" 
        :initialValues="initialValues" 
        @submit="onFormSubmit"
        class="flex flex-col gap-6 w-full"
      >

        <!-- NOMBRE -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nombre</label>
            <InputText name="nombre" type="text" placeholder="Tu nombre" class="w-full px-3 py-2 shadow-sm rounded-lg" />
            <Message v-if="$form.nombre?.invalid" severity="error" variant="simple" size="small">
              {{ $form.nombre.error.message }}
            </Message>
          </div>
          <!-- APELLIDOS -->
          <div class="flex flex-col gap-2">
            <label class="font-medium">Apellidos</label>
            <InputText name="apellidos" type="text" placeholder="Tus apellidos" class="w-full px-3 py-2 shadow-sm rounded-lg" />
          </div>
        </div>

        <!-- EMAIL -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Correo electrónico</label>
          <InputText name="email" type="email" placeholder="correo@ejemplo.com" class="w-full px-3 py-2 shadow-sm rounded-lg" />
          <Message v-if="$form.email?.invalid" severity="error" variant="simple" size="small">
            {{ $form.email.error.message }}
          </Message>
        </div>

        <!-- CONTRASEÑA -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Contraseña</label>
          <Password name="password" placeholder="Mínimo 8 caracteres" :toggleMask="true" :feedback="true" input-class="w-full!" fluid>
            <template #header>
              <div class="font-semibold text-sm mb-4">Elige una contraseña</div>
            </template>
            <template #footer>
              <ul class="pl-2 ml-2 my-0 leading-6 text-sm">
                <li>Mínimo 8 caracteres</li>
              </ul>
            </template>
          </Password>
          <Message v-if="$form.password?.invalid" severity="error" variant="simple" size="small">
            {{ $form.password.error.message }}
          </Message>
        </div>

        <!-- CONFIRMAR CONTRASEÑA -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Repetir contraseña</label>
          <Password name="confirmPassword" placeholder="Confirma tu contraseña" :toggleMask="true" :feedback="false" input-class="w-full!" fluid />
          <Message v-if="$form.confirmPassword?.invalid" severity="error" variant="simple" size="small">
            {{ $form.confirmPassword.error.message }}
          </Message>
        </div>

        <!-- MENSAJE DE ERROR -->
        <div v-if="apiError" class="flex items-center gap-2 text-red-500 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800/30">
          <i class="pi pi-exclamation-triangle text-lg"></i>
          <span class="text-sm md:text-base font-medium">{{ apiErrorMessage }}</span>
        </div>


        <Button type="submit" label="Registrarse" icon="pi pi-user-plus" class="w-full py-2 rounded-lg" :loading="loading" />
      </Form>

    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Form } from "@primevue/forms";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Button from "primevue/button";
import Message from "primevue/message";
import { authService } from "@/api/auth";
import { getErrorMessage } from "@/utils/errors";
import router from '@/router'

const loading = ref(false);
const apiError = ref(false);
const apiErrorMessage = ref("");

const initialValues = ref({
  nombre: "",
  apellidos: "",
  email: "",
  password: "",
  confirmPassword: "",
});

// VALIDACIONES (RESOLVER)
const resolver = ({ values }) => {
  const errors = {};

  if (!values.nombre) {
    errors.nombre = [{ message: "El nombre es obligatorio." }];
  }

  if (!values.email) {
    errors.email = [{ message: "El correo es obligatorio." }];
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = [{ message: "Formato de correo inválido." }];
  }

  if (!values.password) {
    errors.password = [{ message: "La contraseña es obligatoria." }];
  } else if (values.password.length < 8) {
    errors.password = [{ message: "Mínimo 8 caracteres." }];
  }

  if (!values.confirmPassword) {
    errors.confirmPassword = [{ message: "Debes repetir la contraseña." }];
  } else if (values.confirmPassword !== values.password) {
    errors.confirmPassword = [{ message: "Las contraseñas no coinciden." }];
  }

  return { errors };
};

// Envío Form
const onFormSubmit = async (event) => {
  if (!event.valid) return;

  loading.value = true;
  apiError.value = false;
  apiErrorMessage.value = "";

  const { states } = event;

  const values = {
    nombre: states.nombre.value,
    apellidos: states.apellidos.value,
    email: states.email.value,
    password: states.password.value,
  };

  try {
    await authService.register(
      values.email.trim(),
      values.password,
      values.nombre,
      values.apellidos || ""
    );
    console.log("Cuenta creada correctamente!");
    router.push('/home');

  } catch (error) {
    apiError.value = true;
    apiErrorMessage.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
};

</script>