const ETIQUETAS = {
  artista    : 'Artista',
  album      : 'Álbum',
  genero     : 'Género',
  duracion   : 'Duración',
  bitrate    : 'Bitrate',
  ancho      : 'Ancho',
  alto       : 'Alto',
  camara     : 'Cámara',
  paginas    : 'Páginas',
  idioma     : 'Idioma',
  autor      : 'Autor',
  titulo     : 'Título',
  descripcion: 'Descripción',
  resolucion : 'Resolución',
  codec      : 'Codec',
  fps        : 'FPS',
  fecha      : 'Fecha',
}

export function etiquetaAmigable(clave) {
  return ETIQUETAS[clave] ?? clave.charAt(0).toUpperCase() + clave.slice(1).replace(/_/g, ' ')
}
