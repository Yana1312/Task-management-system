<template>
  <div class="pomodoro-container" :class="{ compact: compact }">
    <div class="timer-display">{{ formatTime(pomodoro.timeLeft.value) }}</div>
    <div class="session-type">{{ pomodoro.isBreak.value ? 'ВРЕМЯ ПЕРЕРЫВА' : 'РАБОЧЕЕ ВРЕМЯ' }}</div>
    
    <div class="timer-controls">
      <button class="timer-btn" @click="pomodoro.toggleTimer">
        {{ pomodoro.isRunning.value ? 'Пауза' : 'Старт' }}
      </button>
      <button class="timer-btn" @click="pomodoro.resetTimer">Сброс</button>
    </div>

    <div v-if="!compact" class="timer-settings">
      <div class="setting">
        <div class="setting-label">Работа (мин)</div>
        <div class="setting-controls">
          <button class="setting-btn" @click="pomodoro.decrementSession">-</button>
          <div class="setting-value">{{ pomodoro.sessionTime.value }}</div>
          <button class="setting-btn" @click="pomodoro.incrementSession">+</button>
        </div>
      </div>
      <div class="setting">
        <div class="setting-label">Отдых (мин)</div>
        <div class="setting-controls">
          <button class="setting-btn" @click="pomodoro.decrementBreak">-</button>
          <div class="setting-value">{{ pomodoro.breakTime.value }}</div>
          <button class="setting-btn" @click="pomodoro.incrementBreak">+</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { pomodoroStore } from '../js/pomodoro.js'

defineProps({
  compact: {
    type: Boolean,
    default: false
  }
})

const pomodoro = pomodoroStore

const formatTime = (seconds) => {
  if (isNaN(seconds) || seconds < 0) return '00:00'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}
</script>