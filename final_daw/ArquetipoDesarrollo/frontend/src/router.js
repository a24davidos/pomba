import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/api/auth'
import Login from './views/Login.vue'
import Home from './views/Home.vue'
import Register from './views/Register.vue'
import AppLayout from './layout/AppLayout.vue'


const routes = [
  // --- Autenticación ---
  { path: '/', component: Login },
  { path: '/register', component: Register },
  
  // --- App General ---
  {
    path: '/home',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {path: '', redirec: {name: 'home', params: {view: 'drive'}} },
      {
        path: '/home/:view/:folderId?',
        name: 'home',
        component: Home
      }
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})


router.beforeEach((to, from, next) => {
  const loggedIn = authService.isLoggedIn()

  const isAuthRoute = to.meta.requiresAuth

  // No logueado intentando entrar a zona privada
  if (isAuthRoute && !loggedIn) {
    return next('/')
  }

  // Logueado intentando ir a login/register
  if (loggedIn && (to.path === '/' || to.path === '/register')) {
    return next('/home')
  }

  next()
})

export default router