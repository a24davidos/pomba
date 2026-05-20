export function formatDate(dateString) {
  if (!dateString) return '-'

  const fecha = new Date(dateString)

  const ahora = new Date()

  const ayer = new Date()
  ayer.setDate(ayer.getDate() - 1)

  const hora = fecha.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  })

  // Hoy
  if (fecha.toDateString() === ahora.toDateString()) {
    return `Hoy, ${hora}`
  }

  // Ayer
  if (fecha.toDateString() === ayer.toDateString()) {
    return `Ayer, ${hora}`
  }

  // Mismo año
  if (fecha.getFullYear() === ahora.getFullYear()) {
    return fecha.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'long'
    })
  }

  // Año diferente
  return fecha.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}