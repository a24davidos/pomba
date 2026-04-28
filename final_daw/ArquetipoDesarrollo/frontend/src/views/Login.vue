<template>
  <div class="bg-surface-50 dark:bg-surface-950 px-6 py-20 md:px-20 lg:px-80">
    <div class="bg-surface-0 dark:bg-surface-900 p-8 md:p-12 shadow-sm rounded-2xl w-full max-w-md mx-auto flex flex-col gap-8">
      
      <!-- HEADER -->
      <div class="flex flex-col items-center gap-4">
        <h1 class="text-2xl font-semibold text-center text-surface-900 dark:text-surface-0">
          Bienvenido
        </h1>
        <p class="text-center text-surface-600 dark:text-surface-300">
          ¿No tienes cuenta?
          <router-link to="/register" class="text-primary font-medium ml-1 cursor-pointer hover:text-primary-emphasis">
            Regístrate
          </router-link>
        </p>
      </div>

      <!-- FORM -->
      <Form 
        v-slot="$form" 
        :resolver="resolver" 
        :initialValues="initialValues" 
        @submit="onFormSubmit"
        class="flex flex-col gap-6 w-full"
      >

        <!-- EMAIL -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Correo electrónico</label>
          <InputText 
            name="email" 
            type="email" 
            placeholder="Tu correo electrónico"
            class="w-full px-3 py-2 shadow-sm rounded-lg" 
          />
          <Message v-if="$form.email?.invalid" severity="error" variant="simple" size="small">
            {{ $form.email.error.message }}
          </Message>
        </div>

        <!-- PASSWORD -->
        <div class="flex flex-col gap-2">
          <label class="font-medium">Contraseña</label>
          <Password 
            name="password" 
            placeholder="Tu contraseña" 
            :toggleMask="true" 
            :feedback="false" 
            input-class="w-full!" 
            fluid
          />
          <Message v-if="$form.password?.invalid" severity="error" variant="simple" size="small">
            {{ $form.password.error.message }}
          </Message>
        </div>

        <!-- ERROR API -->
        <div v-if="apiError" class="flex items-center gap-2 text-red-500 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800/30">
          <i class="pi pi-exclamation-triangle text-lg"></i>
          <span class="text-sm md:text-base font-medium">
            {{ apiErrorMessage }}
          </span>
        </div>

        <!-- FORGOT -->
        <div class="flex justify-center md:justify-end">
          <a class="text-primary font-medium cursor-pointer hover:text-primary-emphasis text-center md:text-right">
            ¿Has olvidado tu contraseña?
          </a>
        </div>

        <!-- SUBMIT -->
        <Button 
          type="submit" 
          label="Entrar" 
          icon="pi pi-user" 
          class="w-full py-2 rounded-lg"
          :loading="loading" 
        />
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
import { useRouter } from "vue-router";

const router = useRouter();

const loading = ref(false);
const apiError = ref(false);
const apiErrorMessage = ref("");

const initialValues = ref({
  email: "",
  password: "",
});

// VALIDACIÓN
const resolver = ({ values }) => {
  const errors = {};

  if (!values.email) {
    errors.email = [{ message: "El correo es obligatorio." }];
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = [{ message: "Formato de correo inválido." }];
  }

  if (!values.password) {
    errors.password = [{ message: "La contraseña es obligatoria." }];
  }

  return { errors };
};

// SUBMIT
const onFormSubmit = async (event) => {
  if (!event.valid) return;

  loading.value = true;
  apiError.value = false;
  apiErrorMessage.value = "";

  const { states } = event;

  try {
    await authService.login(
      states.email.value.trim(),
      states.password.value
    );

    router.push("/home");

  } catch (error) {
    apiError.value = true;
    apiErrorMessage.value = getErrorMessage(error) || 
      "El correo o la contraseña no son correctos.";
  } finally {
    loading.value = false;
  }
};
</script>