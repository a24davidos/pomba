import { reactive } from 'vue'

const estado = reactive({
  abierto: false,
  header: '',
  mensaje: '',
  labelAceptar: 'Confirmar',
  labelCancelar: 'Cancelar',
  peligro: false,
  _resolve: null,
})

export function useConfirmacion() {
  function confirmar({ header, mensaje, labelAceptar = 'Confirmar', labelCancelar = 'Cancelar', peligro = false }) {
    return new Promise((resolve) => {
      Object.assign(estado, { abierto: true, header, mensaje, labelAceptar, labelCancelar, peligro, _resolve: resolve })
    })
  }

  function aceptar() {
    estado.abierto = false
    estado._resolve?.(true)
  }

  function cancelar() {
    estado.abierto = false
    estado._resolve?.(false)
  }

  return { estado, confirmar, aceptar, cancelar }
}
