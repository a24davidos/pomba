const ETIQUETAS = {
  artista: 'Artista',
  album: 'Álbum',
  genero: 'Género',
  duracion: 'Duración',
  bitrate: 'Bitrate',
  ancho: 'Ancho',
  alto: 'Alto',
  camara: 'Cámara',
  paginas: 'Páginas',
  idioma: 'Idioma',
  autor: 'Autor',
  titulo: 'Título',
  descripcion: 'Descripción',
  resolucion: 'Resolución',
  codec: 'Codec',
  fps: 'FPS',
  fecha: 'Fecha',
}

// Claves redundantes o que no aportan valor visible al usuario
export const CLAVES_OCULTAS = new Set(['tipo_medio'])

export function etiquetaAmigable(clave) {
  return ETIQUETAS[clave] ?? clave.charAt(0).toUpperCase() + clave.slice(1).replace(/_/g, ' ')
}
