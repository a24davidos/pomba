import axios from 'axios'
import api from './axios'

export const apiItems = {

  async listar(params = {}) {
    const { data } = await api.get('items/', { params })
    return data
  },

  async buscar(q) {
    const { data } = await api.get('items/buscar/', { params: { q } })
    return data
  },

  async crearCarpeta(datos) {
    const { data } = await api.post('items/', datos)
    return data
  },

  async renombrar(id, nombre) {
    await api.post(`items/${id}/renombrar/`, { nombre })
  },

  async solicitarSubida(nombre, mimeType) {
    const { data } = await api.post('items/solicitar_subida/', { nombre, mime_type: mimeType })
    return data
  },

  async subirDirecto(urlSubida, file, mimeType) {
    await axios.put(urlSubida, file, { headers: { 'Content-Type': mimeType } })
  },

  async confirmarSubida(nombre, key, padreId, tamanoBytes, mimeType) {
    await api.post('items/confirmar_subida/', {
      nombre,
      key,
      padre: padreId,
      tamano_bytes: tamanoBytes,
      mime_type: mimeType,
    })
  },

  async crearArbolCarpetas(rutas, padreId) {
    const { data } = await api.post('items/crear_arbol_carpetas/', { rutas, padre: padreId })
    return data
  },

  async mover(ids, destinoId) {
    await api.post('items/mover/', { ids, destino: destinoId })
  },

  async marcarFavorito(ids) {
    const { data } = await api.post('items/favorito/', { ids })
    return data
  },

  async moverAPapelera(ids) {
    await api.post('items/trash/', { ids })
  },

  async restaurar(ids) {
    await api.post('items/restaurar/', { ids })
  },

  async restaurarTodo() {
    await api.post('items/restaurar_papelera/')
  },

  async vaciarPapelera() {
    await api.post('items/vaciar_papelera/')
  },

  async eliminarDefinitivo(ids) {
    await api.delete('items/eliminar_definitivo/', { data: { ids } })
  },

  async descargarArchivo(id) {
    const { data } = await api.get(`items/${id}/descargar_archivo/`)
    return data
  },

  async previsualizar(id) {
    const { data } = await api.get(`items/${id}/previsualizar/`)
    return data
  },

  async descargarZip(ids) {
    const { data } = await api.post('items/descargar/', { ids }, { responseType: 'blob' })
    return data
  },

  // ── Versiones (solo audio) ------------------------------------------------

  async listarVersiones(itemId) {
    const { data } = await api.get(`items/${itemId}/versiones/`)
    return data  // { versiones: [...], numero_actual: N }
  },

  async solicitarSubidaVersion(itemId) {
    const { data } = await api.post(`items/${itemId}/versiones/solicitar_subida/`)
    return data  // { url_subida, key }
  },

  async confirmarSubidaVersion(itemId, key, tamanoBytes, mimeType) {
    const { data } = await api.post(`items/${itemId}/versiones/confirmar_subida/`, {
      key,
      tamano_bytes: tamanoBytes,
      mime_type: mimeType,
    })
    return data  // Item serializado actualizado
  },

  async descargarVersion(itemId, numero) {
    const { data } = await api.get(`items/${itemId}/versiones/${numero}/descargar/`)
    return data  // { url }
  },

  async restaurarVersion(itemId, numero) {
    const { data } = await api.post(`items/${itemId}/versiones/${numero}/restaurar/`)
    return data  // Item serializado actualizado
  },

  async eliminarVersion(itemId, numero) {
    await api.delete(`items/${itemId}/versiones/${numero}/`)
  },

  async previsualizarVersion(itemId, numero) {
    const { data } = await api.get(`items/${itemId}/versiones/${numero}/previsualizar/`)
    return data  // { url }
  },
}
