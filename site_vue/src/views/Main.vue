<template>
  <div class="container">
    <div class="left-sidebar">
      <button class="menu-item active-tab" data-page="all-projects">
        <svg width="47" height="43" viewBox="0 0 47 43" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M45.5 0H1.5C1.10218 0 0.720644 0.158035 0.43934 0.43934C0.158035 0.720644 0 1.10218 0 1.5V39.5C0 40.4283 0.368749 41.3185 1.02513 41.9749C1.6815 42.6312 2.57174 43 3.5 43H13.5C14.4283 43 15.3185 42.6312 15.9749 41.9749C16.6313 41.3185 17 40.4283 17 39.5V27H30V31.5C30 32.4283 30.3687 33.3185 31.0251 33.9749C31.6815 34.6312 32.5717 35 33.5 35H43.5C44.4283 35 45.3185 34.6312 45.9749 33.9749C46.6312 33.3185 47 32.4283 47 31.5V1.5C47 1.10218 46.842 0.720644 46.5607 0.43934C46.2794 0.158035 45.8978 0 45.5 0ZM44 16H33V3H44V16ZM14 3V16H3V3H14ZM14 39.5C14 39.6326 13.9473 39.7598 13.8536 39.8536C13.7598 39.9473 13.6326 40 13.5 40H3.5C3.36739 40 3.24021 39.9473 3.14645 39.8536C3.05268 39.7598 3 39.6326 3 39.5V19H14V39.5ZM17 24V3H30V24H17ZM43.5 32H33.5C33.3674 32 33.2402 31.9473 33.1464 31.8536C33.0527 31.7598 33 31.6326 33 31.5V19H44V31.5C44 31.6326 43.9473 31.7598 43.8536 31.8536C43.7598 31.9473 43.6326 32 43.5 32Z" fill="#E6D1A4"/>
        </svg>
      </button>
      <button class="menu-item" data-page="active-projects">
        <svg width="46" height="46" viewBox="0 0 46 46" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M23.8797 3.1826C23.6247 2.98373 23.3105 2.87573 22.9871 2.87573C22.6636 2.87573 22.3495 2.98373 22.0944 3.1826L1.4375 19.2898L3.22431 21.5495L5.75 19.5802V37.375C5.75152 38.137 6.05491 38.8674 6.59375 39.4062C7.13258 39.9451 7.86297 40.2485 8.625 40.25H37.375C38.137 40.2485 38.8674 39.9451 39.4063 39.4062C39.9451 38.8674 40.2485 38.137 40.25 37.375V19.5931L42.7757 21.5625L44.5625 19.3027L23.8797 3.1826ZM25.875 37.375H20.125V25.875H25.875V37.375ZM28.75 37.375В25.875C28.75 25.1125 28.4471 24.3812 27.9079 23.842C27.3688 23.3029 26.6375 23 25.875 23H20.125C19.3625 23 18.6312 23.3029 18.0921 23.842C17.5529 24.3812 17.25 25.1125 17.25 25.875В37.375Н8.625В17.3391Л23 6.14097Л37.375 17.3535В37.375Н28.75З" fill="#E6D1A4"/>
        </svg>
      </button>
    </div>

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