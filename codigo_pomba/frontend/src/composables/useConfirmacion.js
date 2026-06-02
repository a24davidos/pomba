import { reactive } from 'vue'

const estado = reactive({
  abierto: false,
  header: '',
  mensaje: '',
  labelAceptar: 'Confirmar',
  labelCancelar: 'Cancelar',
  peligro: false,
  // Guardamos la función resolve de la promesa activa para poder llamarla desde aceptar/cancelar (Esto me dio problemas cuando lo diseñe para entenderlo)
  _resolve: null,
})

export function useConfirmacion() {
  // Abre el modal y devuelve una promesa que se resuelve cuando el usuario pulsa un botón. Await en la llamada lo uso para que quede pausado hasta que el usuario acepte o cancele
  // Uso:
  //   const resultado = await confirmar({ header: '¿Eliminar?', peligro: true })
  //   if (resultado) { ... } true = acepto, false = cancelo
  function confirmar({ header, mensaje, labelAceptar = 'Confirmar', labelCancelar = 'Cancelar', peligro = false }) {
    return new Promise((resolve) => {
      Object.assign(estado, { abierto: true, header, mensaje, labelAceptar, labelCancelar, peligro, _resolve: resolve })
    })
  }

  //Resuelve la promesa con true
  function aceptar() {
    estado.abierto = false
    estado._resolve?.(true)
  }

  // Resuelve la promesa con false
  function cancelar() {
    estado.abierto = false
    estado._resolve?.(false)
  }

  return { estado, confirmar, aceptar, cancelar }
}
