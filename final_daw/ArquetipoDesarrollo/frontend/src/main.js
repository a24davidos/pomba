import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import './api/api.js'
import router from './router.js'

import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura'; // Asegúrate de haber hecho: npm install @primeuix/themes
import Button from "primevue/button"

// Importante para los iconos de los Blocks
import 'primeicons/primeicons.css' 

const app = createApp(App)

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            prefix: 'p',
            darkModeSelector: 'system',
            // ESTO ES CLAVE:
            cssLayer: {
                name: 'primevue',
                order: 'theme, base, primevue, utilities' 
            }
        }
    }
});

app.component('Button', Button); // Nota: PrimeBlocks ya suelen traer sus propios imports, pero esto está bien.
app.use(router)
app.mount('#app')