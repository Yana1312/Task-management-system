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
          
          <button class="show-more-button">ПОКАЗАТЬ БОЛЬШЕ...</button>
        </div>
      </div>

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
            <input type="checkbox" id="task3">
            <label for="task3">Создать дизайн</label>
          </div>
        </div>
      </div>
      <div class="section section-pomodoro">
        <p>Pomodoro</p>
        <div class="section-section">
          <PomodoroTimer />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import PomodoroTimer from '../components/PomodoroTimer.vue'

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
</script>