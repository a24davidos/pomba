const mensajesCustom = {
  // Combinación específica: Campo + Código
  "email.unique": "Este email ya se encuentra en uso",
  "email.invalid": "El formato del correo no parece correcto.",
  
  // Mensajes por defecto si no hay uno específico para el campo
  "unique": "Este valor ya está en uso.",
  "required": "Este campo es obligatorio.",
  
  // Errores de sistema
  "server_error": "Hubo un problema en el servidor, inténtalo de nuevo más tarde."
};

export function getErrorMessage(error) {
  // El servidor respondió con un error (400, 403, 500, etc.)
  if (error.response) {
    const data = error.response.data;

    // Buscamos en el primer error del array
    if (data?.type === "validation_error" && data.errors?.length > 0) {
      const err = data.errors[0];
      return err.detail; 
    }

    // Errores genéricos de DRF (ej: "No tienes permisos")
    return data?.detail || "Error en el servidor.";
  }

  //Se intentó conectar pero no hubo respuesta (Error de Red real)
  if (error.request) {
    return "No se ha podido establecer conexión con el servidor. Revisa tu internet.";
  }

  // No hay response ni request, es un fallo interno de la App
  console.error("Critical Client Error:", error); // Esto te ayuda a debuguear en consola
  return `Error interno de la aplicación: ${error.message}`;
}