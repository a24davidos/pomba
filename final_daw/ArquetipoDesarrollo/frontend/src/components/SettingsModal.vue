<template>
  <Dialog
    v-model:visible="visible"
    modal
    :style="{ width: '560px' }"
    :breakpoints="{ '640px': '95vw' }"
    :draggable="false"
    class="settings-dialog"
  >
    <template #header>
      <span class="font-semibold text-lg">Configuración de cuenta</span>
    </template>

    <!-- PESTAÑAS DE NAVEGACIÓN -->
    <div class="flex gap-1 mb-6 border-b border-surface-200 dark:border-surface-700 pb-0">
      <button
        v-for="pestana in pestanas"
        :key="pestana.clave"
        @click="tabActiva = pestana.clave"
        class="px-4 py-2 text-sm rounded-t-lg transition-colors duration-150"
        :class="tabActiva === pestana.clave
          ? 'border-b-2 border-primary text-primary font-medium'
          : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-100'"
      >
        <i :class="pestana.icono" class="mr-2 text-xs" />{{ pestana.etiqueta }}
      </button>
    </div>

    <!-- PESTAÑA: FOTO DE PERFIL -->
    <div v-if="tabActiva === 'foto'" class="flex flex-col items-center gap-5">
      <div class="relative group cursor-pointer" @click="abrirSelector">
        <div class="w-24 h-24 rounded-full overflow-hidden border-2 border-surface-200 dark:border-surface-700 bg-surface-100 dark:bg-surface-800 flex items-center justify-center">
          <img
            v-if="urlPrevia || datosPerfil.foto_perfil_url"
            :src="urlPrevia || datosPerfil.foto_perfil_url"
            alt="Avatar"
            class="w-full h-full object-cover"
          />
          <i v-else class="pi pi-user text-4xl text-surface-400" />
        </div>
        <div class="absolute inset-0 rounded-full bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <i class="pi pi-camera text-white text-xl" />
        </div>
      </div>

      <input
        ref="inputArchivo"
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        class="hidden"
        @change="alSeleccionarArchivo"
      />

      <div v-if="archivoSeleccionado" class="text-sm text-surface-600 dark:text-surface-400">
        {{ archivoSeleccionado.name }}
      </div>

      <div class="flex gap-3">
        <Button
          label="Seleccionar imagen"
          icon="pi pi-upload"
          severity="secondary"
          size="small"
          @click="abrirSelector"
        />
        <Button
          v-if="archivoSeleccionado"
          label="Guardar foto"
          icon="pi pi-check"
          size="small"
          :loading="cargandoFoto"
          @click="guardarFoto"
        />
      </div>

      <Message v-if="exitoFoto" severity="success" :closable="false" class="w-full">
        Foto actualizada correctamente.
      </Message>
      <Message v-if="errorFoto" severity="error" :closable="false" class="w-full">
        {{ errorFoto }}
      </Message>
    </div>

    <!-- PESTAÑA: DATOS PERSONALES -->
    <div v-if="tabActiva === 'datos'" class="flex flex-col gap-4">
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-surface-700 dark:text-surface-300">Nombre</label>
        <InputText v-model="formularioDatos.nombre" placeholder="Tu nombre" />
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-surface-700 dark:text-surface-300">Apellidos</label>
        <InputText v-model="formularioDatos.apellidos" placeholder="Tus apellidos" />
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-surface-700 dark:text-surface-300">Correo electrónico</label>
        <InputText v-model="formularioDatos.email" placeholder="tu@email.com" type="email" />
      </div>

      <Message v-if="exitoDatos" severity="success" :closable="false">
        Datos actualizados correctamente.
      </Message>
      <Message v-if="errorDatos" severity="error" :closable="false">
        {{ errorDatos }}
      </Message>

      <div class="flex justify-end">
        <Button
          label="Guardar cambios"
          icon="pi pi-check"
          :loading="cargandoDatos"
          @click="guardarDatos"
        />
      </div>
    </div>

    <!-- PESTAÑA: CONTRASEÑA -->
    <div v-if="tabActiva === 'contrasena'" class="flex flex-col gap-4">
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-surface-700 dark:text-surface-300">Contraseña actual</label>
        <Password v-model="formularioContrasena.actual" :feedback="false" toggleMask fluid />
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-surface-700 dark:text-surface-300">Nueva contraseña</label>
        <Password v-model="formularioContrasena.nueva" :feedback="false" toggleMask fluid />
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-surface-700 dark:text-surface-300">Confirmar nueva contraseña</label>
        <Password v-model="formularioContrasena.confirmar" :feedback="false" toggleMask fluid />
      </div>

      <Message v-if="exitoContrasena" severity="success" :closable="false">
        Contraseña cambiada correctamente.
      </Message>
      <Message v-if="errorContrasena" severity="error" :closable="false">
        {{ errorContrasena }}
      </Message>

      <div class="flex justify-end">
        <Button
          label="Cambiar contraseña"
          icon="pi pi-lock"
          :loading="cargandoContrasena"
          @click="guardarContrasena"
        />
      </div>
    </div>

    <!-- PESTAÑA: ELIMINAR CUENTA -->
    <div v-if="tabActiva === 'eliminar'" class="flex flex-col gap-5">
      <Message severity="warn" :closable="false" class="w-full">
        Esta acción es <strong>irreversible</strong>. Se eliminarán todos tus archivos, carpetas y datos de forma permanente.
      </Message>

      <div v-if="!confirmarEliminar" class="flex justify-center">
        <Button
          label="Quiero eliminar mi cuenta"
          icon="pi pi-trash"
          severity="danger"
          @click="confirmarEliminar = true"
        />
      </div>

      <div v-else class="flex flex-col gap-4 border border-red-300 dark:border-red-800 rounded-xl p-4 bg-red-50 dark:bg-red-950/30">
        <p class="text-sm text-surface-700 dark:text-surface-300">
          Escribe <strong>ELIMINAR</strong> para confirmar:
        </p>
        <InputText v-model="textoConfirmacion" placeholder="ELIMINAR" />
        <div class="flex gap-3 justify-end">
          <Button label="Cancelar" severity="secondary" @click="confirmarEliminar = false; textoConfirmacion = ''" />
          <Button
            label="Eliminar cuenta"
            icon="pi pi-trash"
            severity="danger"
            :disabled="textoConfirmacion !== 'ELIMINAR'"
            :loading="cargandoEliminar"
            @click="eliminarCuenta"
          />
        </div>
      </div>

      <Message v-if="errorEliminar" severity="error" :closable="false">
        {{ errorEliminar }}
      </Message>
    </div>

  </Dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { servicioUsuario } from '@/api/users'
import { getErrorMessage } from '@/utils/errors'
import { authService } from '@/api/auth'

import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Message from 'primevue/message'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  profile: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue', 'profile-updated'])

const router = useRouter()

// visible es el puente entre v-model del padre y el Dialog de PrimeVue
const visible = computed({
  get: () => props.modelValue,
  set: (valor) => emit('update:modelValue', valor),
})

// Pestañas
const pestanas = [
  { clave: 'foto',      etiqueta: 'Foto',       icono: 'pi pi-image' },
  { clave: 'datos',     etiqueta: 'Datos',      icono: 'pi pi-id-card' },
  { clave: 'contrasena', etiqueta: 'Contraseña', icono: 'pi pi-lock' },
  { clave: 'eliminar',  etiqueta: 'Eliminar',   icono: 'pi pi-trash' },
]
const tabActiva = ref('foto')

// Datos del perfil recibidos del componente padre
const datosPerfil = ref({ ...props.profile })
watch(() => props.profile, (valor) => {
  datosPerfil.value = { ...valor }
  formularioDatos.value.nombre    = valor.nombre    || ''
  formularioDatos.value.apellidos = valor.apellidos || ''
  formularioDatos.value.email     = valor.email     || ''
})

// ----- FOTO -----
const inputArchivo       = ref(null)
const archivoSeleccionado = ref(null)
const urlPrevia          = ref(null)
const cargandoFoto       = ref(false)
const exitoFoto          = ref(false)
const errorFoto          = ref('')

const abrirSelector = () => inputArchivo.value?.click()

const alSeleccionarArchivo = (evento) => {
  const archivo = evento.target.files[0]
  if (!archivo) return
  archivoSeleccionado.value = archivo
  urlPrevia.value = URL.createObjectURL(archivo)
  exitoFoto.value = false
  errorFoto.value = ''
}

const guardarFoto = async () => {
  if (!archivoSeleccionado.value) return
  cargandoFoto.value = true
  errorFoto.value = ''
  exitoFoto.value = false
  try {
    const respuesta = await servicioUsuario.subirFotoPerfil(archivoSeleccionado.value)
    datosPerfil.value.foto_perfil_url = respuesta.foto_perfil_url
    exitoFoto.value = true
    archivoSeleccionado.value = null
    emit('profile-updated', { foto_perfil_url: respuesta.foto_perfil_url })
  } catch (e) {
    errorFoto.value = getErrorMessage(e)
  } finally {
    cargandoFoto.value = false
  }
}

// ----- DATOS PERSONALES -----
const formularioDatos = ref({
  nombre:    props.profile?.nombre    || '',
  apellidos: props.profile?.apellidos || '',
  email:     props.profile?.email     || '',
})
const cargandoDatos = ref(false)
const exitoDatos    = ref(false)
const errorDatos    = ref('')

const guardarDatos = async () => {
  cargandoDatos.value = true
  errorDatos.value = ''
  exitoDatos.value = false
  try {
    const actualizado = await servicioUsuario.actualizarPerfil(formularioDatos.value)
    exitoDatos.value = true
    emit('profile-updated', actualizado)
  } catch (e) {
    errorDatos.value = getErrorMessage(e)
  } finally {
    cargandoDatos.value = false
  }
}

// ----- CONTRASEÑA -----
const formularioContrasena = ref({ actual: '', nueva: '', confirmar: '' })
const cargandoContrasena   = ref(false)
const exitoContrasena      = ref(false)
const errorContrasena      = ref('')

const guardarContrasena = async () => {
  errorContrasena.value = ''
  exitoContrasena.value = false
  if (formularioContrasena.value.nueva !== formularioContrasena.value.confirmar) {
    errorContrasena.value = 'Las contraseñas nuevas no coinciden.'
    return
  }
  cargandoContrasena.value = true
  try {
    await servicioUsuario.cambiarContrasena(
      formularioContrasena.value.actual,
      formularioContrasena.value.nueva,
    )
    exitoContrasena.value = true
    formularioContrasena.value = { actual: '', nueva: '', confirmar: '' }
  } catch (e) {
    errorContrasena.value = getErrorMessage(e)
  } finally {
    cargandoContrasena.value = false
  }
}

// ----- ELIMINAR CUENTA -----
const confirmarEliminar  = ref(false)
const textoConfirmacion  = ref('')
const cargandoEliminar   = ref(false)
const errorEliminar      = ref('')

const eliminarCuenta = async () => {
  cargandoEliminar.value = true
  errorEliminar.value = ''
  try {
    await servicioUsuario.eliminarCuenta()
    authService.logout()
    router.push('/')
  } catch (e) {
    errorEliminar.value = getErrorMessage(e)
  } finally {
    cargandoEliminar.value = false
  }
}

// Resetear todo al cerrar el modal
watch(visible, (valor) => {
  if (!valor) {
    tabActiva.value = 'foto'
    archivoSeleccionado.value = null
    urlPrevia.value = null
    exitoFoto.value = false
    errorFoto.value = ''
    exitoDatos.value = false
    errorDatos.value = ''
    formularioContrasena.value = { actual: '', nueva: '', confirmar: '' }
    exitoContrasena.value = false
    errorContrasena.value = ''
    confirmarEliminar.value = false
    textoConfirmacion.value = ''
    errorEliminar.value = ''
  }
})
</script>
