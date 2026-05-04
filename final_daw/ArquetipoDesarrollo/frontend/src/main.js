import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import './api/api.js'
import router from './router.js'


import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura'; 
import 'primeicons/primeicons.css' 
import Button from "primevue/button"


const app = createApp(App)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark', // 👈 CLAVE
      // cssLayer: {
      //   name: 'primevue',
      //   // order: 'theme, base, primevue, utilities'
      // }
    }
  }
})

app.use(router)
app.mount('#app')