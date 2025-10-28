import { ref } from 'vue'

// Глобальный store для Pomodoro таймера
class PomodoroStore {
  constructor() {
    this.timeLeft = ref(25 * 60)
    this.isRunning = ref(false)
    this.isBreak = ref(false)
    this.sessionTime = ref(25)
    this.breakTime = ref(5)
    this.timerInterval = null
  }

  startTimer() {
    if (this.timerInterval) clearInterval(this.timerInterval)
    
    this.timerInterval = setInterval(() => {
      if (this.timeLeft.value > 0) {
        this.timeLeft.value--
      } else {
        clearInterval(this.timerInterval)
        this.isRunning.value = false
        this.isBreak.value = !this.isBreak.value
        this.timeLeft.value = (this.isBreak.value ? this.breakTime.value : this.sessionTime.value) * 60
        
        // Уведомление
        if (Notification.permission === 'granted') {
          new Notification(this.isBreak.value ? 'Время перерыва!' : 'Время работать!')
        }
      }
    }, 1000)
  }

  toggleTimer() {
    if (this.isRunning.value) {
      clearInterval(this.timerInterval)
      this.isRunning.value = false
    } else {
      this.isRunning.value = true
      this.startTimer()
    }
  }

  resetTimer() {
    clearInterval(this.timerInterval)
    this.isRunning.value = false
    this.isBreak.value = false
    this.timeLeft.value = this.sessionTime.value * 60
  }

  incrementSession() {
    if (this.sessionTime.value < 60) {
      this.sessionTime.value++
      if (!this.isRunning.value && !this.isBreak.value) {
        this.timeLeft.value = this.sessionTime.value * 60
      }
    }
  }

  decrementSession() {
    if (this.sessionTime.value > 1) {
      this.sessionTime.value--
      if (!this.isRunning.value && !this.isBreak.value) {
        this.timeLeft.value = this.sessionTime.value * 60
      }
    }
  }

  incrementBreak() {
    if (this.breakTime.value < 60) {
      this.breakTime.value++
      if (!this.isRunning.value && this.isBreak.value) {
        this.timeLeft.value = this.breakTime.value * 60
      }
    }
  }

  decrementBreak() {
    if (this.breakTime.value > 1) {
      this.breakTime.value--
      if (!this.isRunning.value && this.isBreak.value) {
        this.timeLeft.value = this.breakTime.value * 60
      }
    }
  }

  requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }
}

export const pomodoroStore = new PomodoroStore()