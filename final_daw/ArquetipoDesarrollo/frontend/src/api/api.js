import axios from 'axios';
import router from '@/router'

const api = axios.create({
  baseURL: 'http://localhost/api/',
  headers: { 'Content-Type': 'application/json' },
});

// 1. INTERCEPTOR DE PETICIÓN: Añadir el token automáticamente
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 2. INTERCEPTOR DE RESPUESTA: Manejar el refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si es 401 y no es un reintento
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error("No hay refresh token");

        // Usamos una instancia limpia de axios
        // para evitar bucles infinitos si esta petición también falla
        const { data } = await axios.post('http://localhost/api/auth/refresh_token/', {
          refresh: refreshToken
        });

        localStorage.setItem('access_token', data.access);
        
        // Reintentamos la petición original con el nuevo token
        originalRequest.headers['Authorization'] = `Bearer ${data.access}`;
        return api(originalRequest);

      } catch (refreshError) {
        //Borrar prod
        console.error("Sesión expirada. Redirigiendo...");
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/login')
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);


export default api;