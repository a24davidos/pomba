import { errorMessages } from "./errorMessages";

export function getErrorMessage(error) {
  // CASO 1: Respuesta de la API (400, 401, etc.)
  if (error.response) {
    const data = error.response.data;

    // Buscamos en el array de errores
    if (data.errors && Array.isArray(data.errors) && data.errors.length > 0) {
      const err = data.errors[0]; // Tomamos el primero para el mensaje
      const attr = err.attr;
      const code = err.code;

      // 1. Intentamos buscar en 'fields' (específico): ej. fields.email.unique
      if (attr && errorMessages.fields[attr] && errorMessages.fields[attr][code]) {
        return errorMessages.fields[attr][code];
      }

      // 2. Si no hay nada específico, buscamos en 'codes' y devolvemos un mensaje genérico
      if (errorMessages.codes[code]) {
        return errorMessages.codes[code];
      }

      //Si no hay traducción, devolvemos el detalle que nos devuelve Dango Django
      return err.detail;
    }

    // Errores simples de DRF (ej. { detail: "..." })
    return data?.detail || errorMessages.fallback;
  }

  // CASO 2: Error de red (Servidor apagado o sin internet)
  if (error.request) {
    return errorMessages.network;
  }

  // CASO 3: Error de código JS (Bugs)
  console.error("Critical Client Error:", error);
  const isDev = import.meta?.env?.DEV;
  
  return isDev
    ? `Error interno: ${error.message}`
    : errorMessages.fallback;
}