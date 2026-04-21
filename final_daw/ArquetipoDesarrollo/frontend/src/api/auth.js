import api from '../api';


const setTokens = (data) => {
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
};

export const authService = {

    async login(username, password) {
        const { data } = await api.post('auth/obtain_token/', { username, password });

        setTokens(data);
        return data;
    }, 

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        //Redirigimos al usuario para que no se quede en una zona privada
        window.location.href = '/login';
    },

    // Para comprobar si el usuario está dentro (útil para mostrar/ocultar botones)
    isLoggedIn() {
        const token = localStorage.getItem('access_token');
        if (!token) return false;

        try {
            // Decodificamos la parte central del JWT (el payload)
            const base64Url = token.split('.')[1];
            const payload = JSON.parse(window.atob(base64Url));
            
            // Comprobamos si el tiempo actual es menor a la expiración
            const now = Math.floor(Date.now() / 1000);
            return payload.exp > now;
        } catch (e) {
            return false; // Si el token está corrupto
        }
    }
};

