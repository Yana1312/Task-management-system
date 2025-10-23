<template>
  <div class="auth-page">
    <div class="auth-block">
      <div class="welcome-text">
        <h1>Регистрация</h1>
        <h4>Зарегистрируйтесь, чтобы получить доступ к управлению проектами.</h4>
      </div>
      
      <div class="auth-form">
        <form @submit.prevent="onRegister">
          <input v-model="email" type="email" class="input-auth" placeholder="Введите вашу почту" required>
          <input v-model="username" type="text" class="input-auth" placeholder="Введите имя пользователя" required>
          <div class="password-input-wrapper">
            <input v-model="password1" :type="showPassword1 ? 'text' : 'password'" class="input-auth input-password" placeholder="Введите ваш пароль" minlength="8" required>
            <button type="button" class="toggle-password-btn" @click="togglePassword1" :aria-label="showPassword1 ? 'Скрыть пароль' : 'Показать пароль'">
              <img src="/resources/password_check_icon.svg" alt="Показать пароль" class="toggle-password-icon" />
            </button>
          </div>
          <div class="password-input-wrapper">
            <input v-model="password2" :type="showPassword2 ? 'text' : 'password'" class="input-auth input-password" placeholder="Подтвердите ваш пароль" minlength="8" required>
            <button type="button" class="toggle-password-btn" @click="togglePassword2" :aria-label="showPassword2 ? 'Скрыть пароль' : 'Показать пароль'">
              <img src="/resources/password_check_icon.svg" alt="Показать пароль" class="toggle-password-icon" />
            </button>
          </div>
          <div class="btn-reg-block">
            <button type="submit" class="btn-reg">Зарегистрироваться</button>
          </div>
        </form>
      </div>
  
      <div class="register-block">
        <router-link to="/" class="register-link">Уже есть аккаунт? Войти!</router-link>
      </div>
  
      <div class="block-alternative-entrance">
        <img src="/resources/gmail.svg" alt="Войти с помощью gmail" class="alternative-entrance-img"/>
        <img src="/resources/yandex.svg" alt="Войти с помощью yandex" class="alternative-entrance-img"/>
        <img src="/resources/telegram.svg" alt="Войти с помощью telegram" class="alternative-entrance-img"/>
      </div>

      <div v-if="toast.visible" :class="['toast', toast.type === 'success' ? 'toast-success' : 'toast-error']">{{ toast.message }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '../lib/supabase'
import bcrypt from 'bcryptjs'

const router = useRouter()
const email = ref('')
const username = ref('')
const password1 = ref('')
const password2 = ref('')
const showPassword1 = ref(false)
const showPassword2 = ref(false)
const loading = ref(false)
const toast = ref({ visible: false, type: 'success', message: '' })

const showToast = (message, type = 'success') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => { toast.value.visible = false }, 4000)
}

const togglePassword1 = () => { showPassword1.value = !showPassword1.value }
const togglePassword2 = () => { showPassword2.value = !showPassword2.value }

const onRegister = async () => {
  if (password1.value !== password2.value) {
    showToast('Пароли не совпадают', 'error')
    return
  }
  loading.value = true
  const { data, error: signUpError } = await supabase.auth.signUp({
    email: email.value,
    password: password1.value,
    options: {
      data: { username: username.value }
    }
  })
  loading.value = false
  if (signUpError) {
    const msg = signUpError.message.includes('Database error')
      ? 'Не удалось зарегистрировать. Попробуйте позже или проверьте данные.'
      : signUpError.message.includes('already registered')
        ? 'Пользователь с такой почтой уже существует.'
        : 'Ошибка при регистрации. Попробуйте ещё раз.'
    showToast(msg, 'error')
    return
  }

  // Берём UID из ответа signUp — он должен совпадать с auth.users.id
  const uid = data?.user?.id || null

  let passwordHash = ''
  try {
    passwordHash = await bcrypt.hash(password1.value, 10)
  } catch (e) {
    console.warn('Password hash error:', e)
  }

  try {
    if (uid) {
      const { error: profileError } = await supabase
        .from('users')
        .insert({
          id: uid,
          username: username.value,
          email: email.value,
          password_hash: passwordHash,
          avatar_url: null,
          created_at: new Date().toISOString(),
        })
      if (profileError) {
        console.warn('Profile insert error:', profileError)
        showToast('Профиль не сохранён, попробуйте позже.', 'error')
      }
    } else {
      console.warn('Registration: no user.id returned; skipping profile insert now')
      // Профиль будет создан при первом заходе на страницу Профиля, где мы жёстко вставляем id = auth.uid
    }
  } catch (e) {
    console.warn('Profile insert exception:', e)
  }

  showToast('Регистрация выполнена.', 'success')
  router.push({ path: '/', query: { registered: '1' } })
}
</script>