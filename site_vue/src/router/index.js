import { createRouter, createWebHistory } from 'vue-router'

import Authorization from '../views/Authorization.vue'
import Registration from '../views/Registration.vue'
import Main from '../views/Main.vue'
import Profile from '../views/Profile.vue'
import Archive from '../views/Archive.vue'

const routes = [
  { path: '/', name: 'auth', component: Authorization },
  { path: '/register', name: 'register', component: Registration },
  { path: '/main', name: 'main', component: Main },
  { path: '/profile', name: 'profile', component: Profile },
  { path: '/archive', name: 'archive', component: Archive },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router