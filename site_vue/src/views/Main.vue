<template>
  <div class="container">
    <div class="main">
      <!-- Страница активных проектов -->
      <div class="page-content active" id="active-projects">
        <div class="active-projects-main">
          <div class="projects-header">АКТИВНЫЕ ПРОЕКТЫ</div>
          <h3 class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</h3>
          <div class="project-row"><span class="project-name">КУРС МАТЕМАТИКИ</span><span class="project-progress">52%</span></div>
          <div class="project-row"><span class="project-name">ИЗУЧЕНИЕ PYTHON</span><span class="project-progress">75%</span></div>

          <h3 class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</h3>
          <div class="project-row"><span class="project-name">ВЕБ-РАЗРАБОТКА</span><span class="project-progress">30%</span></div>
          <div class="project-row"><span class="project-name">МОБИЛЬНОЕ ПРИЛОЖЕНИЕ</span><span class="project-progress">15%</span></div>
          <div class="project-row"><span class="project-name">ДИЗАЙН ИНТЕРФЕЙСА</span><span class="project-progress">90%</span></div>

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
            <div class="timer-display">25:00</div>
            <div class="session-type">РАБОЧЕЕ ВРЕМЯ</div>
            <div class="timer-controls">
              <button class="timer-btn">Старт</button>
              <button class="timer-btn">Пауза</button>
              <button class="timer-btn">Сброс</button>
            </div>
            <div class="timer-settings">
              <div class="setting">
                <div class="setting-label">Перерыв</div>
                <div class="setting-controls">
                  <button class="setting-btn">-</button>
                  <div class="setting-value">5</div>
                  <button class="setting-btn">+</button>
                </div>
              </div>
              <div class="setting">
                <div class="setting-label">Сессия</div>
                <div class="setting-controls">
                  <button class="setting-btn">-</button>
                  <div class="setting-value">25</div>
                  <button class="setting-btn">+</button>
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
import { onMounted } from 'vue'

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

  let timerInterval
  let timeLeft = 25 * 60
  let isRunning = false
  let isBreak = false

  const timerDisplay = document.querySelector('.timer-display')
  const sessionType = document.querySelector('.session-type')
  const startBtn = document.querySelectorAll('.timer-btn')[0]
  const pauseBtn = document.querySelectorAll('.timer-btn')[1]
  const resetBtn = document.querySelectorAll('.timer-btn')[2]
  const breakValue = document.querySelectorAll('.setting-value')[0]
  const sessionValue = document.querySelectorAll('.setting-value')[1]
  const breakMinus = document.querySelectorAll('.setting-btn')[0]
  const breakPlus = document.querySelectorAll('.setting-btn')[1]
  const sessionMinus = document.querySelectorAll('.setting-btn')[2]
  const sessionPlus = document.querySelectorAll('.setting-btn')[3]

  function updateDisplay() {
    const minutes = Math.floor(timeLeft / 60)
    const seconds = timeLeft % 60
    timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  function startTimer() {
    if (!isRunning) {
      isRunning = true
      timerInterval = setInterval(() => {
        timeLeft--
        updateDisplay()
        if (timeLeft === 0) {
          clearInterval(timerInterval)
          isRunning = false
          isBreak = !isBreak
          if (isBreak) {
            timeLeft = parseInt(breakValue.textContent) * 60
            sessionType.textContent = 'ВРЕМЯ ПЕРЕРЫВА'
          } else {
            timeLeft = parseInt(sessionValue.textContent) * 60
            sessionType.textContent = 'РАБОЧЕЕ ВРЕМЯ'
          }
          updateDisplay()
        }
      }, 1000)
    }
  }

  function pauseTimer() {
    if (isRunning) {
      clearInterval(timerInterval)
      isRunning = false
    }
  }

  function resetTimer() {
    clearInterval(timerInterval)
    isRunning = false
    isBreak = false
    timeLeft = parseInt(sessionValue.textContent) * 60
    sessionType.textContent = 'РАБОЧЕЕ ВРЕМЯ'
    updateDisplay()
  }

  startBtn.addEventListener('click', startTimer)
  pauseBtn.addEventListener('click', pauseTimer)
  resetBtn.addEventListener('click', resetTimer)

  breakMinus.addEventListener('click', () => {
    let value = parseInt(breakValue.textContent)
    if (value > 1) {
      breakValue.textContent = value - 1
    }
  })

  breakPlus.addEventListener('click', () => {
    let value = parseInt(breakValue.textContent)
    if (value < 60) {
      breakValue.textContent = value + 1
    }
  })

  sessionMinus.addEventListener('click', () => {
    let value = parseInt(sessionValue.textContent)
    if (value > 1) {
      sessionValue.textContent = value - 1
      if (!isRunning && !isBreak) {
        timeLeft = value * 60
        updateDisplay()
      }
    }
  })

  sessionPlus.addEventListener('click', () => {
    let value = parseInt(sessionValue.textContent)
    if (value < 60) {
      sessionValue.textContent = value + 1
      if (!isRunning && !isBreak) {
        timeLeft = value * 60
        updateDisplay()
      }
    }
  })

  updateDisplay()
})
</script>