import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router.js'

import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import { definePreset } from '@primeuix/themes'
import 'primeicons/primeicons.css'

const app = createApp(App)

// Paleta Clara
const stoneSurface = {
    0: '#ffffff',
    50: '#fafaf9',
    100: '#f5f5f4',
    200: '#e7e5e4',
    300: '#d6d3d1',
    400: '#a8a29e',
    500: '#78716c',
    600: '#57534e',
    700: '#44403c',
    800: '#292524',
    900: '#1c1917',
    950: '#0c0a09'
};
// Paleta Oscura
const vivaSurface = {
    0: '#ffffff',
    50: '#f3f3f3',
    100: '#e7e7e8',
    200: '#cfd0d0',
    300: '#b7b8b9',
    400: '#9fa1a1',
    500: '#87898a',
    600: '#6e7173',
    700: '#565a5b',
    800: '#3e4244',
    900: '#262b2c',
    950: '#0e1315'
};


const MyCustomPreset = definePreset(Aura, {
    semantic: {
        colorScheme: {
            light: {
                surface: stoneSurface
            },
            dark: {
                surface: vivaSurface
            }
        }
    }
});

app.use(PrimeVue, {
    theme: {
        preset: MyCustomPreset,
        options: {
            darkModeSelector: '.dark',
            cssLayer: {
                name: 'primevue',
                order: 'theme, base, primevue, utilities'
            }
        }
    }
});

app.use(router)
app.mount('#app')