<template>
  <div class="container">
    <div class="main">
      <!-- Страница активных проектов -->
      <div class="page-content active" id="active-projects">
        <div class="active-projects-main">
          <div class="projects-header">ЗАВЕРШЕННЫЕ ПРОЕКТЫ</div>
          <h3 class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</h3>
          <div class="project-row"><span class="project-name">КУРС ПО ПРОГРАММИРОВАНИЮ</span><span class="project-progress">100%</span></div>
          <div class="project-row"><span class="project-name">ИЗУЧЕНИЕ JAVA</span><span class="project-progress">100%</span></div>
          <div class="project-row"><span class="project-name">ПРОЕКТИРОВАНИЕ БАЗЫ ДАННЫХ</span><span class="project-progress">100%</span></div>

          <h3 class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</h3>
          <div class="project-row"><span class="project-name">ВЕБ-РАЗРАБОТКА САЙТА</span><span class="project-progress">100%</span></div>
          <div class="project-row"><span class="project-name">МОБИЛЬНОЕ ПРИЛОЖЕНИЕ</span><span class="project-progress">100%</span></div>
          <div class="project-row"><span class="project-name">ДИЗАЙН ИНТЕРФЕЙСА</span><span class="project-progress">100%</span></div>

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
  </div>
</template>