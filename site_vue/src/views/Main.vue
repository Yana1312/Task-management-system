<template>
  <div class="container">
    <div class="main">
      <!-- Страница активных проектов -->

      <div class="page-content active" id="active-projects">
          <div class="projects-header">АКТИВНЫЕ ПРОЕКТЫ</div>
          <div class="active-projects-main">
            <h3 class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</h3>
            <div class="project-row"><span class="project-name">КУРС МАТЕМАТИКИ</span><span class="project-progress">52%</span></div>
            <div class="project-row"><span class="project-name">ИЗУЧЕНИЕ PYTHON</span><span class="project-progress">75%</span></div>

            <h3 class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</h3>
              <div class="project-row"><span class="project-name">ВЕБ-РАЗРАБОТКА</span><span class="project-progress">30%</span></div>
              <div class="project-row"><span class="project-name">МОБИЛЬНОЕ ПРИЛОЖЕНИЕ</span><span class="project-progress">15%</span></div>
              <div class="project-row"><span class="project-name">ДИЗАЙН ИНТЕРФЕЙСА</span><span class="project-progress">90%</span></div>
              <div class="project-row"><span class="project-name">ПРОЕКТ 6</span><span class="project-progress">45%</span></div>
              <div class="project-row"><span class="project-name">ПРОЕКТ 7</span><span class="project-progress">60%</span></div>
              <div class="project-row"><span class="project-name">ПРОЕКТ 8</span><span class="project-progress">25%</span></div>
              <div class="project-row"><span class="project-name">ПРОЕКТ 9</span><span class="project-progress">85%</span></div>
              <div class="project-row"><span class="project-name">ПРОЕКТ 10</span><span class="project-progress">70%</span></div>

            <button class="show-more-button">ПОКАЗАТЬ БОЛЬШЕ...</button>
          </div>
      </div>

      <!-- Страница всех проектов -->
      <div class="page-content" id="all-projects">
        <div class="projects-container">
          <div class="main-header">СУЩЕСТВУЮЩИЕ ПРОЕКТЫ</div>
          <div class="project-sections">
            <div class="personal-projects">
              <h2 class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</h2>
              <div class="project-card">
                <div class="card-title">КУРС МАТЕМАТИКИ</div>
                <div class="lesson-item">
                  <div>
                    <div class="lesson-title">ПЕРВЫЙ УРОК</div>
                    <div class="lesson-time">ОСТАЛОСЬ ВРЕМЕНИ: 2 ДНЯ</div>
                  </div>
                  <i class="fas fa-pencil-alt edit-icon"></i>
                </div>
                <div class="lesson-item">
                  <div>
                    <div class="lesson-title">ВТОРОЙ УРОК</div>
                    <div class="lesson-time">ОСТАЛОСЬ ВРЕМЕНИ: 10 ДНЕЙ</div>
                  </div>
                  <i class="fas fa-pencil-alt edit-icon"></i>
                </div>
                <button class="edit-button">РЕДАКТИРОВАТЬ ПРОЕКТ</button>
              </div>
            </div>
            <div class="team-projects">
              <h2 class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</h2>
              <div class="project-card">
                <div class="card-title">ВЕБ-РАЗРАБОТКА</div>
                <div class="lesson-item">
                  <div class="team-avatars">
                    <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #CE7939;"></div>
                    <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #E6D1A4; margin-left: -5px;"></div>
                  </div>
                  <div><div class="lesson-title">ПЕРВЫЙ УРОК</div></div>
                  <i class="fas fa-pencil-alt edit-icon"></i>
                </div>
                <button class="edit-button">РЕДАКТИРОВАТЬ ПРОЕКТ</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="right-sidebar">
      <img style="width: 300px;" src="/resources/title_project.svg">
      <div class="section" style="margin-bottom: 10px;">
        <p>Задачи</p>
        <div class="section-section">
          <div class="task-item">
            <input type="checkbox" id="task1">
            <label for="task1">Изучить Python</label>
          </div>
          <div class="task-item">
            <input type="checkbox" id="task2">
            <label for="task2">Сделать канбан-доску</label>
          </div>
          <div class="task-item">
            <input type="checkbox" id="task3" checked>
            <label for="task3">Создать дизайн</label>
          </div>
          <div class="task-item">
            <input type="checkbox" id="task4">
            <label for="task4">Написать документацию</label>
          </div>
          <div class="task-item">
            <input type="checkbox" id="task5">
            <label for="task5">Протестировать функционал</label>
          </div>
        </div>
      </div>
      <div class="section section-pomodoro">
        <p>Pomodoro</p>
        <div class="section-section">
          <div class="pomodoro-container">
            <div class="timer-display">{{ formatTime(timeLeft) }}</div>
            <div class="session-type">{{ isBreak ? 'ВРЕМЯ ПЕРЕРЫВА' : 'РАБОЧЕЕ ВРЕМЯ' }}</div>
            <div class="timer-controls">
              <button class="timer-btn" @click="toggleTimer">{{ isRunning ? 'Пауза' : 'Старт' }}</button>
              <button class="timer-btn" @click="resetTimer">Сброс</button>
            </div>
            <div class="timer-settings">
              <div class="setting">
                <div class="setting-label">Перерыв</div>
                <div class="setting-controls">
                  <button class="setting-btn" @click="decrementBreak">-</button>
                  <div class="setting-value">{{ breakTime }}</div>
                  <button class="setting-btn"  @click="incrementBreak">+</button>
                </div>
              </div>
              <div class="setting">
                <div class="setting-label">Сессия</div>
                <div class="setting-controls">
                  <button class="setting-btn" @click="decrementSession">-</button>
                  <div class="setting-value">{{ sessionTime }}</div>
                  <button class="setting-btn" @click="incrementSession">+</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const timeLeft = ref(25 * 60)
const isRunning = ref(false)
const isBreak = ref(false)
const sessionTime = ref(25)
const breakTime = ref(5)
let timerInterval = null

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const toggleTimer = () => {
  if (isRunning.value) {
    clearInterval(timerInterval)
    isRunning.value = false
  } else {
    isRunning.value = true
    timerInterval = setInterval(() => {
      if (timeLeft.value > 0) {
        timeLeft.value--
      } else {
        clearInterval(timerInterval)
        isRunning.value = false
        isBreak.value = !isBreak.value
        timeLeft.value = (isBreak.value ? breakTime.value : sessionTime.value) * 60
      }
    }, 1000)
  }
}

const incrementSession = () => {
  if (sessionTime.value < 60) {
    sessionTime.value++
    if (!isRunning.value && !isBreak.value) {
      timeLeft.value = sessionTime.value * 60
    }
  }
}

const decrementSession = () => {
  if (sessionTime.value > 1) {
    sessionTime.value--
    if (!isRunning.value && !isBreak.value) {
      timeLeft.value = sessionTime.value * 60
    }
  }
}

const incrementBreak = () => {
  if (breakTime.value < 60) {
    breakTime.value++
    if (!isRunning.value && isBreak.value) {
      timeLeft.value = breakTime.value * 60
    }
  }
}

const decrementBreak = () => {
  if (breakTime.value > 1) {
    breakTime.value--
    if (!isRunning.value && isBreak.value) {
      timeLeft.value = breakTime.value * 60
    }
  }
}

const resetTimer = () => {
  clearInterval(timerInterval)
  isRunning.value = false
  isBreak.value = false
  timeLeft.value = sessionTime.value * 60
}

onMounted(() => {
  const menuItems = document.querySelectorAll('.menu-item')
  const pageContents = document.querySelectorAll('.page-content')

  menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault()
      menuItems.forEach(i => i.classList.remove('active-tab'))
      pageContents.forEach(content => content.classList.remove('active'))
      item.classList.add('active-tab')
      const targetPageId = item.getAttribute('data-page')
      const targetPage = document.getElementById(targetPageId)
      if (targetPage) targetPage.classList.add('active')
    })
  })
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>