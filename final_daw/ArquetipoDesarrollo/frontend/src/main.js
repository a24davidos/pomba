import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import './api/api.js'
import router from './router.js'

const app = createApp(App)

app.use(router)
app.mount('#app')
