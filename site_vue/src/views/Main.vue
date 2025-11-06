<template>
  <div class="container">
    <div class="main">
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
        <div class="section-header">
          <p>Мои задачи</p>
          <span class="tasks-count" v-if="tasks.length > 0">{{ tasks.length }}</span>
        </div>
        <div class="section-section tasks-container">
          <div v-if="loading" class="loading-tasks">Загрузка задач...</div>
          <div v-else-if="tasks.length === 0" class="no-tasks">
            Нет активных задач
          </div>
          <div v-else class="tasks-scrollable">
            <div 
              v-for="task in sortedTasks" 
              :key="task.id" 
              class="task-item"
              :class="{ 
                urgent: isTaskUrgent(task.due_date),
                'high-priority': task.priority === 'high'
              }"
            >
              <div class="task-content">
                <span class="task-title">{{ task.title }}</span>
                <div class="task-meta">
                  <span v-if="task.due_date" class="task-due-date" :class="getDueDateClass(task.due_date)">
                    {{ formatDueDate(task.due_date) }}
                  </span>
                  <span v-if="task.priority" class="priority-badge" :class="task.priority">
                    {{ getPriorityLabel(task.priority) }}
                  </span>
                </div>
                <div class="task-project" v-if="getProjectInfo(task)">
                  <span class="project-badge" :style="{ backgroundColor: getProjectColor(task) }">
                    {{ getProjectInfo(task) }}
                  </span>
                </div>
              </div>
            </div>
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
import { ref, onMounted, computed } from 'vue'
import { supabase } from '../lib/supabase.js'
import { auth } from '../js/auth.js'
import PomodoroTimer from '../components/PomodoroTimer.vue'

const tasks = ref([])
const loading = ref(true)

const sortedTasks = computed(() => {
  return [...tasks.value].sort((a, b) => {
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
    const priorityA = priorityOrder[a.priority] || 4
    const priorityB = priorityOrder[b.priority] || 4
    
    return priorityA - priorityB
  })
})

const loadTasks = async () => {
  const userId = await getCurrentUserId()
  if (!userId) {
    loading.value = false
    return
  }

  try {
    const { data, error } = await supabase
      .from('tasks')
      .select(`
        *,
        columns:column_id (
          title,
          boards:board_id (
            id,
            title,
            background,
            description
          )
        )
      `)
      .or(`creator_id.eq.${userId},assignee_id.eq.${userId}`)
      .eq('is_completed', false) 
      .order('created_at', { ascending: false })

    if (error) throw error
    tasks.value = data || []
  } catch (error) {
    console.error('Ошибка загрузки задач:', error)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const getCurrentUserId = async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.user?.id || null
  } catch (error) {
    console.error('Ошибка получения пользователя:', error)
    return null
  }
}

const isTaskUrgent = (dueDate) => {
  if (!dueDate) return false
  const now = new Date()
  const due = new Date(dueDate)
  const diffTime = due.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays <= 3
}

const getDueDateClass = (dueDate) => {
  if (!dueDate) return ''
  const now = new Date()
  const due = new Date(dueDate)
  const diffTime = due.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'overdue'
  if (diffDays === 0) return 'today'
  if (diffDays <= 3) return 'urgent'
  return ''
}

const formatDueDate = (dueDate) => {
  if (!dueDate) return ''
  
  const now = new Date()
  const due = new Date(dueDate)
  const diffTime = due.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) {
    return `Просрочено ${Math.abs(diffDays)} дн.`
  } else if (diffDays === 0) {
    return 'Сегодня'
  } else if (diffDays === 1) {
    return 'Завтра'
  } else {
    return `${diffDays} дн.`
  }
}

const getPriorityLabel = (priority) => {
  const labels = {
    low: 'Низкий',
    medium: 'Средний',
    high: 'Высокий',
    critical: 'Критический'
  }
  return labels[priority] || priority
}

const getProjectInfo = (task) => {
  if (!task.columns || !task.columns.boards) return null
  return task.columns.boards.title || 'Без проекта'
}

const getProjectColor = (task) => {
  if (!task.columns || !task.columns.boards || !task.columns.boards.background) {
    return '#B54B11'
  }
  return task.columns.boards.background
}

onMounted(() => {
  loadTasks()
  
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

<style scoped>
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tasks-count {
  background: #B54B11;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.5em;
  font-weight: bold;
}

.tasks-container {
  display: flex;
  flex-direction: column;
  height: 300px; 
  background:transparent;
}

.tasks-scrollable {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
}

.tasks-scrollable::-webkit-scrollbar {
  width: 6px;
}

.tasks-scrollable::-webkit-scrollbar-track {
  background: rgba(181, 75, 17, 0.1);
  border-radius: 3px;
}

.tasks-scrollable::-webkit-scrollbar-thumb {
  background: #CE7939;
  border-radius: 3px;
}

.tasks-scrollable::-webkit-scrollbar-thumb:hover {
  background: #B54B11;
}

.task-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 16px;
  color: #e6d1a4;
  background: #b54b11;
  border-left: 3px solid #B54B11;
  transition: all 0.2s ease;
}

.task-content {
  flex: 1;
}

.task-title {
  display: flex;
  font-weight: 500;
  margin-bottom: 4px;
  word-break: break-word;
}

.task-meta {
  display: flex;
  gap: 8px;
  font-size: 0.75em;
  margin-bottom: 4px;
  align-items: center;
  flex-wrap: wrap;
}

.task-due-date {
  font-size: 0.75em;
  padding: 1px 4px;
  border-radius: 2px;
}

.task-due-date.overdue {
  background: #ff4444;
  color: white;
  font-weight: bold;
}

.task-due-date.today {
  background: #ff6b35;
  color: white;
  font-weight: bold;
}

.task-due-date.urgent {
  background: #ffaa00;
  color: black;
  font-weight: bold;
}

.priority-badge {
  padding: 1px 4px;
  border-radius: 2px;
  font-size: 0.7em;
  font-weight: bold;
}

.priority-badge.high {
  background: #ff4444;
  color: white;
}

.priority-badge.medium {
  background: #ffaa00;
  color: black;
}

.priority-badge.low {
  background: #44ff44;
  color: black;
}

.priority-badge.critical {
  background: #ff00ff;
  color: white;
}

.task-project {
  margin-top: 2px;
  display:flex;
}

.project-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.7em;
  color: white;
  font-weight: 500;
  background: #B54B11;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loading-tasks, .no-tasks {
  text-align: center;
  color: #E6D1A4;
  font-style: italic;
  padding: 10px;
  font-size: 0.9em;
}

.task-item label {
  word-break: break-word;
}
</style>