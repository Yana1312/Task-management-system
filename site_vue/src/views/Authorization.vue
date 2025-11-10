<template>
  <div class="auth-page">
    <div class="auth-block">
      <div class="welcome-text">
        <h1>Добро пожаловать, дорогой пользователь!</h1>
        <h4>Войдите в свою учетную запись, чтобы получить доступ к своим проектам.</h4>
      </div>
      
      <div class="auth-form">
        <form @submit.prevent="onLogin">
          <input v-model="email" type="email" class="input-auth" placeholder="Введите ваш email" required>
          <div class="password-input-wrapper">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" class="input-auth input-password" placeholder="Введите ваш пароль" required>
            <button type="button" class="toggle-password-btn" @click="togglePassword" :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'">
              <img src="/resources/password_check_icon.svg" alt="Показать пароль" class="toggle-password-icon" />
            </button>
          </div>
          
          <button type="submit" class="btn-enter">Войти</button>
        </form>
      </div>
  
      <div class="register-block">
        <router-link to="/register" class="register-link">Нет аккаунта? Зарегистрируйтесь!</router-link>
      </div>
  
      <div v-if="toast.visible" :class="['toast', toast.type === 'success' ? 'toast-success' : 'toast-error']">{{ toast.message }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { supabase } from '../lib/supabase'
import { auth } from '../js/auth.js'

const router = useRouter()
const showPassword = ref(false)
const email = ref('')
const password = ref('')
const loading = ref(false)

const togglePassword = () => { showPassword.value = !showPassword.value }

const onLogin = async () => {
  loading.value = true
  const { data, error: authError } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value,
  })
  loading.value = false
  if (authError) {
    const msg = authError.message && authError.message.includes('Invalid login credentials')
      ? 'Неверный email или пароль.'
      : 'Не удалось войти. Проверьте данные или попробуйте позже.'
    showToast(msg, 'error')
    return
  }

  try {
    const userId = data?.user?.id || null
    console.log('[authz] login success, supabase userId:', userId)
    if (userId) {
      auth.setUser(userId)
      await auth.fetchAvatar().then((url) => {
        console.log('[authz] fetchAvatar after login:', url)
      }).catch((e) => console.warn('[authz] fetchAvatar error:', e))
    } else {
      console.warn('[authz] login success but no user.id present')
    }
  } catch (e) {
    console.warn('[authz] post-login handling error:', e)
  }

  router.push('/main')
}

const route = useRoute()
const toast = ref({ visible: false, type: 'success', message: '' })
const showToast = (message, type = 'success') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => { toast.value.visible = false }, 4000)
}

onMounted(() => {
  if (route.query.registered === '1') {
    showToast('Аккаунт успешно зарегистрирован. Пожалуйста, войдите.', 'success')
  }
})
</script>