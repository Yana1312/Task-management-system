<template>
  <nav class="vertical-navbar">
    <div class="nav-top">
      <router-link to="/profile" aria-label="Профиль">
        <img class="nav-avatar-img" :src="avatarSrc" alt="Профиль" @error="onAvatarError" />
      </router-link>
    </div>

    <div class="nav-items">
      <router-link to="/main" class="nav-item" :class="{ active: isActivePath('/main') }" aria-label="Домой">
        <img class="nav-icon-img" src="/resources/menu_icon.svg" alt="Домой"/>
      </router-link>

      <router-link to="/boards" class="nav-item" :class="{ active: isActivePath('/boards') }" aria-label="Задачи">
        <img class="nav-icon-img" src="/resources/zadachi_icon.svg" alt="Задачи"/>
      </router-link>

      <router-link to="/archive" class="nav-item" :class="{ active: isActivePath('/archive') }" aria-label="Архив">
        <img class="nav-icon-img" src="/resources/folder_icon.svg" alt="Архив"/>
      </router-link>

      <router-link to="/analitics" class="nav-item" :class="{ active: isActivePath('/analitics') }" aria-label="Аналитика">
        <img class="nav-icon-img" src="/resources/analitics_icon.svg" alt="Аналитика"/>
      </router-link>

      <div class="nav-item pomodoro-mini" :class="{ active: pomodoro.isRunning.value }" @click="togglePomodoroModal">
        <div class="pomodoro-mini-display">
          <div class="pomodoro-time">{{ formatTime(pomodoro.timeLeft.value) }}</div>
          <div class="pomodoro-status">{{ pomodoro.isBreak.value ? 'Отдых' : 'Работа' }}</div>
          <div class="pomodoro-controls-mini">
            <button class="pomodoro-btn-mini" @click.stop="pomodoro.toggleTimer">
              {{ pomodoro.isRunning.value ? '⏸️' : '▶️' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="nav-footer">
      <router-link to="/main#settings" class="nav-item" :class="{ active: isActiveHash('#settings') }" aria-label="Настройки">
        <img class="nav-icon-img" src="/resources/settings.svg" alt="Настройки"/>
      </router-link>
    </div>

    <div v-if="showPomodoroModal" class="pomodoro-modal-overlay" @click="closePomodoroModal">
      <div class="pomodoro-modal" @click.stop>
        <div class="pomodoro-modal-header">
          <h3>Pomodoro Таймер</h3>
          <button class="pomodoro-modal-close" @click="closePomodoroModal">×</button>
        </div>
        <div class="pomodoro-modal-content">
          <PomodoroTimer />
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { auth } from '../js/auth.js'
import { pomodoroStore } from '../js/pomodoro.js'
import PomodoroTimer from '../components/PomodoroTimer.vue'

const route = useRoute()
const showPomodoroModal = ref(false)

const isActivePath = (path) => route.path === path
const isActiveHash = (hash) => route.path === '/main' && route.hash === hash

const pomodoro = pomodoroStore

const formatTime = (seconds) => {
  if (isNaN(seconds) || seconds < 0) return '00:00'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const togglePomodoroModal = () => {
  showPomodoroModal.value = !showPomodoroModal.value
}

const closePomodoroModal = () => {
  showPomodoroModal.value = false
}

onMounted(() => {
  console.log('[navbar] mounted userId:', auth.userId.value, 'avatarUrl:', auth.avatarUrl.value)
  if (!auth.avatarUrl.value) {
    auth.fetchAvatar().then((url) => {
      console.log('[navbar] fetchAvatar resolved url:', url)
    }).catch((e) => console.warn('[navbar] fetchAvatar error:', e))
  }
  
  pomodoro.requestNotificationPermission()
})

const avatarSrc = computed(() => auth.avatarUrl.value || auth.PLACEHOLDER_AVATAR)

const onAvatarError = (e) => {
  console.warn('[navbar] img error, fallback to placeholder')
  e.target.src = auth.PLACEHOLDER_AVATAR
}
</script>