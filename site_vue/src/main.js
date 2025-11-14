import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/style.css'

import { auth } from './js/auth.js'
import { supabase } from './lib/supabase.js'

auth.initFromStorage()
console.log('[main] initFromStorage userId:', auth.userId.value, 'avatarUrl:', auth.avatarUrl.value)
auth.initDemoFromEnv()

// Экспортируем для ручной проверки в консоли
if (typeof window !== 'undefined') {
  window.auth = auth
}

async function bootstrapAvatar() {
  try {
    if (auth.isDemo.value) {
      await auth.fetchAvatar()
      return
    }
    if (!auth.userId.value) {
      const { data, error } = await supabase.auth.getUser()
      if (error) console.warn('[main] supabase.getUser error:', error)
      const supaUserId = data?.user?.id || null
      console.log('[main] supabase.getUser userId:', supaUserId)
      if (supaUserId) {
        auth.setUser(supaUserId)
      }
    }
    const url = await auth.fetchAvatar()
    console.log('[main] bootstrap fetchAvatar url:', url)
  } catch (e) {
    console.warn('[main] bootstrapAvatar error:', e)
  }
}

bootstrapAvatar()

createApp(App).use(router).mount('#app')
