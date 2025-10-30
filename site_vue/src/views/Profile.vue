<template>
  <div class="profile-page">
    <div class="profile-header">
      <h1 class="title">Личный кабинет</h1>
      <p class="subtitle">Управляйте данными своего аккаунта</p>
    </div>

    <section class="profile-card">
      <div class="avatar-block">
        <img :src="avatarPreview" class="avatar-img" alt="Аватар" @error="onAvatarError" />
        <div class="avatar-actions">
          <label class="file-input">
            <input type="file" accept="image/*" @change="onAvatarSelected" />
            <span>Выбрать фото</span>
          </label>
          <button class="btn btn-primary" :disabled="!selectedAvatar" @click="uploadAvatar">Загрузить</button>
        </div>
      </div>

      <div class="info-block">
        <div class="field-row">
          <label>Имя пользователя</label>
          <input v-model="username" type="text" placeholder="Ваш ник" />
          <div class="field-actions">
            <button class="btn btn-primary" @click="saveUsername">Сохранить</button>
          </div>
        </div>

        <div class="field-row">
          <label>Почта</label>
          <input v-model="newEmail" type="email" placeholder="Новая почта" readonly />
          <div class="field-actions">
            <button class="btn" @click="openEmailModal">Сменить</button>
          </div>
        </div>

        <div class="field-row">
          <label>Telegram</label>
          <input v-model="tgUsername" type="text" placeholder="Ваш tg юзернейм (без @)" />
          <div class="field-actions">
            <button class="btn btn-primary" @click="saveTelegramUsername">Подключить</button>
            <button class="btn" v-if="tgUsername" @click="disconnectTelegram">Отключить</button>
          </div>
          <p class="muted" style="color: white">Бот авторизует вас по этому юзернейму.</p>
        </div>

        <div class="field-row">
          <label>Пароль</label>
          <div class="field-actions">
            <button class="btn" @click="openPasswordModal">Сменить пароль</button>
          </div>
        </div>
      </div>
    </section>

    <div v-if="showEmailModal" class="modal-backdrop" @click.self="closeEmailModal">
      <div class="modal">
        <h2>Смена почты</h2>
        <p class="muted">Отправим код подтверждения на новую почту</p>
        <div class="modal-row">
          <label>Новая почта</label>
          <input v-model="emailForm.email" type="email" placeholder="user@example.com" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" @click="sendEmailChange">Отправить код</button>
          <button class="btn" @click="closeEmailModal">Отмена</button>
        </div>
        <div v-if="emailForm.sent" class="modal-row">
          <label>Код из письма</label>
          <input v-model="emailForm.token" type="text" placeholder="Вставьте код/токен" />
          <div class="modal-actions">
            <button class="btn btn-primary" @click="verifyEmailChange">Подтвердить</button>
          </div>
          <p class="muted">Можно также перейти по ссылке из письма.</p>
        </div>
        <p v-if="emailForm.message" class="status">{{ emailForm.message }}</p>
      </div>
    </div>

    <div v-if="showPasswordModal" class="modal-backdrop" @click.self="closePasswordModal">
      <div class="modal">
        <h2>Смена пароля</h2>
        <p class="muted">Отправим письмо для смены пароля. Перейдите по ссылке из письма.</p>
        <div class="modal-row">
          <label>Текущая почта</label>
          <input v-model="passwordForm.email" type="email" placeholder="user@example.com" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" @click="sendPasswordRecovery">Отправить письмо</button>
          <button class="btn" @click="closePasswordModal">Отмена</button>
        </div>
        <div v-if="passwordForm.sent" class="modal-row">
          <label>Текущая почта</label>
          <input v-model="passwordForm.email" type="email" readonly />
          <label>Новый пароль</label>
          <input v-model="passwordForm.newPassword" type="password" placeholder="Новый пароль" />
          <div class="modal-actions">
            <button class="btn btn-primary" @click="updatePassword">Сохранить пароль</button>
          </div>
          <p class="muted">После перехода по ссылке из письма установите новый пароль.</p>
        </div>
        <p v-if="passwordForm.message" class="status">{{ passwordForm.message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { supabase } from '../lib/supabase.js'
import { auth } from '../js/auth.js'

const username = ref('')
const newEmail = ref('')
const selectedAvatar = ref(null)
let avatarsDirHandle = null
const tgUsername = ref('')

const showEmailModal = ref(false)
const showPasswordModal = ref(false)

const emailForm = ref({ email: '', token: '', sent: false, message: '' })
const passwordForm = ref({ email: '', newPassword: '', sent: false, message: '' })

const DEV_EMAIL_BYPASS = String(import.meta?.env?.VITE_DEV_EMAIL_BYPASS || '').toLowerCase() === 'true'

const avatarPreview = computed(() => {
  return selectedAvatar.value ? URL.createObjectURL(selectedAvatar.value) : (auth.avatarUrl.value || auth.PLACEHOLDER_AVATAR)
})

function onAvatarError(e) {
  e.target.src = auth.PLACEHOLDER_AVATAR
}

function onAvatarSelected(e) {
  const file = e.target.files?.[0]
  selectedAvatar.value = file || null
}

async function uploadAvatar() {
  if (!selectedAvatar.value) return
  const { data: userData, error: userErr } = await supabase.auth.getUser()
  if (userErr) { alert('Ошибка авторизации'); return }
  const uid = userData?.user?.id
  const email = userData?.user?.email
  const file = selectedAvatar.value
  const ext = (file.name.split('.').pop() || 'jpg').toLowerCase()
  const fileName = `${uid}_${Date.now()}.${ext}`
  const relativePath = `resources/avatars/${fileName}`

  if (!('showDirectoryPicker' in window)) {
    alert('Ваш браузер не поддерживает прямое сохранение. Положите файл вручную в public/resources/avatars.')
    return
  }

  try {
    if (!avatarsDirHandle) {
       alert('Выберите папку: site_vue/public/resources/avatars')
       avatarsDirHandle = await window.showDirectoryPicker()
       if ((avatarsDirHandle.name || '').toLowerCase() !== 'avatars') {
         alert('Выберите именно папку avatars внутри public/resources')
         avatarsDirHandle = null
         return
       }
     }
     const fileHandle = await avatarsDirHandle.getFileHandle(fileName, { create: true })
    const writable = await fileHandle.createWritable()
    await writable.write(file)
    await writable.close()
  } catch (err) {
    alert('Не удалось сохранить файл: ' + (err?.message || err))
    return
  }

  const publicUrl = '/' + relativePath

  const { data: updatedById, error: updErr1 } = await supabase
    .from('users')
    .update({ avatar_url: publicUrl })
    .eq('id', uid)
    .select()

  if (updErr1) { alert('Ошибка сохранения аватара: ' + updErr1.message); return }

  if (!updatedById || updatedById.length === 0) {
    const { error: updErr2 } = await supabase
      .from('users')
      .update({ avatar_url: publicUrl })
      .eq('email', email)
    if (updErr2) { alert('Ошибка сохранения аватара: ' + updErr2.message); return }
  }

  auth.avatarUrl.value = publicUrl
  try { localStorage.setItem('avatar_url', publicUrl) } catch {}
  selectedAvatar.value = null
  alert('Аватар сохранен: ' + publicUrl)
}

async function loadProfile() {
  try {
    const { data: userData, error: authError } = await supabase.auth.getUser()
    if (authError) {
      console.error('[Profile] Auth error:', authError)
      return
    }
    
    const uid = userData?.user?.id
    const email = userData?.user?.email
    
    console.log('[Profile] Loading profile for user:', uid)
    
    if (!uid) {
      console.error('[Profile] No user ID found')
      return
    }

    newEmail.value = email || ''

    let row = null
    let dbError = null
    {
      const res = await supabase
        .from('users')
        .select('id, email, username, avatar_url')
        .eq('id', uid)
        .maybeSingle()
      row = res.data
      dbError = res.error
    }

    if (dbError) {
      console.error('[Profile] Database error (by id):', dbError)
      return
    }

    if (!row) {
      const { data: byEmailRow, error: byEmailErr } = await supabase
        .from('users')
        .select('id, email, username, avatar_url')
        .eq('email', email)
        .maybeSingle()
      if (byEmailErr) {
        console.error('[Profile] Database error (by email):', byEmailErr)
        return
      }
      row = byEmailRow
    }

    if (!row) {
      console.log('[Profile] User not found, creating with id=auth uid')
      const { error: insertError } = await supabase
        .from('users')
        .insert({ 
          id: uid,
          email: email,
          username: email?.split('@')[0] || 'user',
          password_hash: `auth:${uid}`
        })
      if (insertError) {
        console.error('[Profile] Error creating user:', insertError)
        return
      }

      const { data: createdRow, error: loadErr } = await supabase
        .from('users')
        .select('id, email, username, avatar_url')
        .eq('id', uid)
        .maybeSingle()
      if (loadErr) {
        console.error('[Profile] Error reloading user:', loadErr)
        return
      }
      row = createdRow
    }

    console.log('[Profile] Loaded user data:', row)
    username.value = row?.username || ''
    tgUsername.value = row?.tg_username || ''

    if (row?.avatar_url) {
      auth.avatarUrl.value = row.avatar_url
    }
    
  } catch (err) {
    console.error('[Profile] Unexpected error:', err)
  }
}

async function saveUsername() {
  const { data: userData, error } = await supabase.auth.getUser()
  if (error) { alert('Ошибка авторизации'); return }
  const uid = userData?.user?.id
  const email = userData?.user?.email

  const { data: updatedById, error: updErr1 } = await supabase
    .from('users')
    .update({ username: username.value })
    .eq('id', uid)
    .select()
  if (updErr1) { alert('Ошибка: ' + updErr1.message); return }

  if (!updatedById || updatedById.length === 0) {
    const { error: updErr2 } = await supabase
      .from('users')
      .update({ username: username.value })
      .eq('email', email)
    if (updErr2) { alert('Ошибка: ' + updErr2.message); return }
  }

  alert('Имя пользователя сохранено')
}

function openEmailModal() {
  emailForm.value.email = newEmail.value
  emailForm.value.token = ''
  emailForm.value.sent = false
  emailForm.value.message = ''
  showEmailModal.value = true
}
function closeEmailModal() { showEmailModal.value = false }

async function saveTelegramUsername() {
  const { data: userData, error } = await supabase.auth.getUser()
  if (error) { alert('Ошибка авторизации'); return }
  const uid = userData?.user?.id
  const email = userData?.user?.email

  const next = (tgUsername.value || '').trim().replace(/^@+/, '').toLowerCase()

  const { data: updatedById, error: updErr1 } = await supabase
    .from('users')
    .update({ tg_username: next })
    .eq('id', uid)
    .select()
  if (updErr1) { alert('Ошибка: ' + updErr1.message); return }

  if (!updatedById || updatedById.length === 0) {
    const { error: updErr2 } = await supabase
      .from('users')
      .update({ tg_username: next })
      .eq('email', email)
    if (updErr2) { alert('Ошибка: ' + updErr2.message); return }
  }

  alert('Telegram подключён')
}

async function disconnectTelegram() {
  const { data: userData, error } = await supabase.auth.getUser()
  if (error) { alert('Ошибка авторизации'); return }
  const uid = userData?.user?.id
  const email = userData?.user?.email

  const { data: updatedById, error: updErr1 } = await supabase
    .from('users')
    .update({ tg_username: '' })
    .eq('id', uid)
    .select()
  if (updErr1) { alert('Ошибка: ' + updErr1.message); return }

  if (!updatedById || updatedById.length === 0) {
    const { error: updErr2 } = await supabase
      .from('users')
      .update({ tg_username: '' })
      .eq('email', email)
    if (updErr2) { alert('Ошибка: ' + updErr2.message); return }
  }
  tgUsername.value = ''
  alert('Telegram отключён')
}

async function sendEmailChange() {
  const nextEmail = (emailForm.value.email || '').trim()
  if (DEV_EMAIL_BYPASS) {
    emailForm.value.sent = true
    emailForm.value.message = 'Режим разработки: письмо не отправлялось. Введите любой код (например 000000).'
    return
  }
  const { error } = await supabase.auth.updateUser({ email: nextEmail })
  if (error) { emailForm.value.message = 'Ошибка: ' + error.message; return }
  emailForm.value.sent = true
  emailForm.value.message = 'Письмо отправлено. Введите код/токен из письма или перейдите по ссылке.'
}

async function verifyEmailChange() {
  const { data: userData } = await supabase.auth.getUser()
  const uid = userData?.user?.id
  const currentEmail = userData?.user?.email
  const token = (emailForm.value.token || '').trim()
  const targetEmail = (emailForm.value.email || currentEmail || '').trim()

  if (DEV_EMAIL_BYPASS) {
    if (uid && targetEmail) {
      await supabase.from('users').update({ email: targetEmail }).eq('id', uid)
    }
    newEmail.value = targetEmail
    emailForm.value.message = 'Почта обновлена (режим разработки)'
    return
  }

  const { error } = await supabase.auth.verifyOtp({ email: targetEmail, token, type: 'email_change' })
  if (error) { emailForm.value.message = 'Ошибка подтверждения: ' + error.message; return }
  newEmail.value = targetEmail
  emailForm.value.message = 'Почта подтверждена и обновлена'
}

function openPasswordModal() {
  passwordForm.value.email = newEmail.value
  passwordForm.value.newPassword = ''
  passwordForm.value.sent = false
  passwordForm.value.message = ''
  showPasswordModal.value = true
}
function closePasswordModal() { showPasswordModal.value = false }

async function sendPasswordRecovery() {
  const { error } = await supabase.auth.resetPasswordForEmail(passwordForm.value.email, { redirectTo: window.location.origin + '/profile' })
  if (error) { passwordForm.value.message = 'Ошибка: ' + error.message; return }
  passwordForm.value.sent = false
  passwordForm.value.message = 'Письмо отправлено. Перейдите по ссылке из письма для установки нового пароля.'
}

async function updatePassword() {
  const { error: uErr } = await supabase.auth.updateUser({ password: passwordForm.value.newPassword })
  if (uErr) { passwordForm.value.message = 'Ошибка смены пароля: ' + uErr.message; return }
  passwordForm.value.message = 'Пароль обновлен'
  showPasswordModal.value = false
}

const RECOVERY_KEY = 'profile_password_recovery_trigger'
let authSubscription
function onStorage(e) {
  if (e.key === RECOVERY_KEY && e.newValue) {
    showPasswordModal.value = true
    passwordForm.value.sent = true
    supabase.auth.getUser().then(({ data }) => {
      passwordForm.value.email = data?.user?.email || ''
    })
    passwordForm.value.message = 'Ссылка подтверждена. Установите новый пароль.'
  }
}

onMounted(() => {
  loadProfile()
  window.addEventListener('storage', onStorage)
  const { data } = supabase.auth.onAuthStateChange((event, session) => {
    if (event === 'PASSWORD_RECOVERY') {
      showPasswordModal.value = true
      passwordForm.value.sent = true
      passwordForm.value.email = session?.user?.email || passwordForm.value.email
      if (!passwordForm.value.email) {
        supabase.auth.getUser().then(({ data }) => {
          passwordForm.value.email = data?.user?.email || ''
        })
      }
      passwordForm.value.message = 'Введите новый пароль и нажмите Сохранить пароль.'
      try { localStorage.setItem(RECOVERY_KEY, String(Date.now())) } catch {}
    }
  })
  authSubscription = data?.subscription
})

onUnmounted(() => {
  try { authSubscription?.unsubscribe() } catch {}
  window.removeEventListener('storage', onStorage)
})
</script>