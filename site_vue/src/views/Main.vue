<template>
  <div class="container">
    <div class="main">
      <div class="page-content active" id="active-projects">
        <div class="projects-header">АКТИВНЫЕ ПРОЕКТЫ</div>

        <!-- Отладочная информация -->
        <div v-if="projectsLoading" class="loading-info">
          Загрузка проектов...
        </div>
        <div v-else class="debug-info">
          Найдено проектов: {{ projects.length }} | 
          Личных: {{ personalProjects.length }} | 
          Командных: {{ teamProjects.length }}
        </div>

        <div class="boards-sections">
          <div class="boards-section">
            <h3 class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</h3>
            <div v-if="projectsLoading" class="loading">Загрузка проектов...</div>
            <div v-else class="boards-row">
              <div
                v-for="project in personalProjects"
                :key="project.id"
                class="boards-card"
                :style="{ backgroundColor: project.background || cardBg }"
                @click="openProject(project)"
              >
                <div class="boards-card-header">
                  <div class="boards-pill">{{ project.title }}</div>
                </div>
                <div class="boards-card-list">
                  <div class="boards-card-item">
                    <span class="item-title">{{ project.description || 'Без описания' }}</span>
                  </div>
                  <div class="boards-card-item muted">Создано: {{ formatDate(project.created_at) }}</div>
                  <div class="boards-card-item muted">
                    Участников: {{ project.members.length }}
                  </div>
                  
                  <!-- Прогресс выполнения -->
                  <div class="project-progress-section">
                    <div class="progress-info">
                      <span class="progress-text">Прогресс выполнения:</span>
                      <span class="progress-percentage">{{ project.completionRate }}%</span>
                    </div>
                    <div class="progress-bar">
                      <div 
                        class="progress-fill" 
                        :style="{ width: project.completionRate + '%' }"
                        :class="getProgressClass(project.completionRate)"
                      ></div>
                    </div>
                    <div class="progress-stats">
                      <span>Завершено: {{ project.completedTasks }}/{{ project.totalTasks }} задач</span>
                    </div>
                  </div>
                </div>
                <div class="boards-card-footer">
                  <button class="boards-btn boards-btn-secondary" @click.stop="openProject(project)">Открыть проект</button>
                </div>
              </div>
              <div v-if="personalProjects.length === 0" class="boards-empty">
                Нет личных проектов
              </div>
            </div>
          </div>

          <div class="boards-section">
            <h3 class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</h3>
            <div v-if="projectsLoading" class="loading">Загрузка проектов...</div>
            <div v-else class="boards-row">
              <div
                v-for="project in teamProjects"
                :key="project.id"
                class="boards-card"
                :style="{ backgroundColor: project.background || cardBg }"
                @click="openProject(project)"
              >
                <div class="boards-card-header">
                  <div class="boards-pill">{{ project.title }}</div>
                </div>
                <div class="boards-card-list">
                  <div class="boards-card-item">
                    <span class="item-title">{{ project.description || 'Без описания' }}</span>
                  </div>
                  <div class="boards-card-item muted">Создано: {{ formatDate(project.created_at) }}</div>
                  <div class="boards-card-item muted">
                    Участников: {{ project.members.length }}
                  </div>
                  <div class="boards-card-item muted">
                    Админ: {{ getBoardAdmin(project.id)?.email || 'Вы' }}
                  </div>
                  
                  <!-- Прогресс выполнения -->
                  <div class="project-progress-section">
                    <div class="progress-info">
                      <span class="progress-text">Прогресс выполнения:</span>
                      <span class="progress-percentage">{{ project.completionRate }}%</span>
                    </div>
                    <div class="progress-bar">
                      <div 
                        class="progress-fill" 
                        :style="{ width: project.completionRate + '%' }"
                        :class="getProgressClass(project.completionRate)"
                      ></div>
                    </div>
                    <div class="progress-stats">
                      <span>Завершено: {{ project.completedTasks }}/{{ project.totalTasks }} задач</span>
                    </div>
                  </div>
                </div>
                <div class="boards-card-footer">
                  <button class="boards-btn boards-btn-secondary" @click.stop="openProject(project)">Открыть проект</button>
                </div>
              </div>
              <div v-if="teamProjects.length === 0" class="boards-empty">
                Нет командных проектов
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
          <span class="tasks-count" v-if="filteredTasks.length > 0">{{ filteredTasks.length }}</span>
        </div>
        <div class="section-section tasks-container">
          <div v-if="loading" class="loading-tasks">Загрузка задач...</div>
          <div v-else-if="filteredTasks.length === 0" class="no-tasks">
            Нет активных задач
          </div>
          <div v-else class="tasks-scrollable">
            <div 
              v-for="task in filteredTasks" 
              :key="task.id" 
              class="task-item"
              :class="{ 
                completed: task.is_completed && task.approval_status === 'approved',
                rejected: task.approval_status === 'rejected'
              }"
            >
              <label :for="'task' + task.id">
                <span class="task-title">{{ task.title }}</span>
                <div class="task-meta">
                  <span v-if="task.due_date" class="task-due-date" :class="getDueDateClass(task.due_date)">
                    {{ formatDueDate(task.due_date) }}
                  </span>
                  <span v-if="task.priority" class="priority-badge" :class="task.priority">
                    {{ getPriorityLabel(task.priority) }}
                  </span>
                  <span v-if="task.approval_status === 'rejected'" class="approval-badge rejected">
                    ❌ Требует доработки
                  </span>
                </div>
                <div class="task-project" v-if="getProjectInfo(task)">
                  <span class="project-badge" :style="{ backgroundColor: getProjectColor(task) }">
                    {{ getProjectInfo(task) }}
                  </span>
                </div>
              </label>
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
import { useRouter } from 'vue-router'
import { supabase } from '../lib/supabase.js'
import { auth } from '../js/auth.js'
import PomodoroTimer from '../components/PomodoroTimer.vue'

const router = useRouter()
const tasks = ref([])
const projects = ref([])
const loading = ref(true)
const projectsLoading = ref(true)
const cardBg = ref('#B54B11')
const isAdmin = ref(false)

// ФИЛЬТРАЦИЯ ЗАДАЧ: 
// - Обычный пользователь видит только свои НЕ выполненные задачи
// - Админ видит только задачи на проверке (готовые, но не подтвержденные)
const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    if (isAdmin.value) {
      // Админ видит только задачи на проверке (только выполненные задачи со статусом pending)
      return task.is_completed && task.approval_status === 'pending'
    } else {
      // Обычный пользователь видит только свои НЕ выполненные задачи
      // ИЛИ выполненные, но требующие доработки (rejected)
      const isMyTask = task.assignee_id === auth.userId.value
      
      // Показываем:
      // 1. Не выполненные задачи
      // 2. Выполненные задачи, но требующие доработки
      return isMyTask && (
        !task.is_completed || 
        (task.is_completed && task.approval_status === 'rejected')
      )
    }
  })
})

const personalProjects = computed(() => {
  return projects.value.filter(project => project.isPersonal)
})

const teamProjects = computed(() => {
  return projects.value.filter(project => !project.isPersonal)
})

const checkAdminStatus = async () => {
  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      isAdmin.value = false
      return
    }

    // Проверяем, есть ли у пользователя роль админа в любом проекте
    const { data: userRoles, error } = await supabase
      .from('user_roles')
      .select(`
        role_id,
        roles:role_id (name_role)
      `)
      .eq('user_id', user.id)

    if (error) {
      console.log('Ошибка проверки прав админа:', error)
      isAdmin.value = false
      return
    }

    // Если есть хотя бы одна роль админа - считаем пользователя админом
    isAdmin.value = userRoles?.some(role => role.roles?.name_role === 'admin') || false
    
  } catch (error) {
    console.error('Ошибка проверки прав админа:', error)
    isAdmin.value = false
  }
}

const loadProjectsWithProgress = async () => {
  projectsLoading.value = true
  
  try {
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError) {
      console.error('Ошибка аутентификации:', authError)
      projectsLoading.value = false
      return
    }

    if (!user) {
      console.log('Пользователь не авторизован')
      projectsLoading.value = false
      return
    }

    const userId = user.id
    console.log('🔄 Начинаем загрузку проектов для пользователя:', userId)

    // Получаем все доски, в которых состоит пользователь (как в boards.vue)
    const { data: userRoles, error: rolesError } = await supabase
      .from('user_roles')
      .select('board_id')
      .eq('user_id', userId)

    if (rolesError) {
      console.error('❌ Ошибка загрузки user_roles:', rolesError)
      projects.value = []
      projectsLoading.value = false
      return
    }

    const assignedIds = (userRoles || []).map(r => r.board_id).filter(Boolean)

    if (assignedIds.length === 0) {
      console.log('ℹ️ У пользователя нет проектов')
      projects.value = []
      projectsLoading.value = false
      return
    }

    // Получаем все доски пользователя
    const { data: boardsData, error: boardsError } = await supabase
      .from('boards')
      .select('*')
      .in('id', assignedIds)
    
    if (boardsError) {
      console.error('❌ Ошибка загрузки досок:', boardsError)
      projects.value = []
      projectsLoading.value = false
      return
    }

    console.log('📋 Найдено досок:', boardsData?.length || 0)

    const projectsWithProgress = []

    // Для каждой доски считаем прогресс
    for (const board of boardsData) {
      console.log(`🔄 Обрабатываем доску: ${board.title} (ID: ${board.id})`)
      
      try {
        // Получаем участников доски
        const { data: membersData, error: membersError } = await supabase
          .from('user_roles')
          .select(`
            user_id,
            users:user_id (email, id),
            roles:role_id (name_role)
          `)
          .eq('board_id', board.id)

        if (membersError) {
          console.error(`❌ Ошибка загрузки участников для доски ${board.id}:`, membersError)
        }

        // Получаем колонки доски
        const { data: columnsData, error: columnsError } = await supabase
          .from('columns')
          .select('id, title')
          .eq('board_id', board.id)

        if (columnsError) {
          console.error(`❌ Ошибка загрузки колонок для доски ${board.id}:`, columnsError)
        }

        console.log(`📊 Колонки для доски ${board.title}:`, columnsData?.length || 0)

        const columnIds = columnsData?.map(col => col.id) || []
        let totalTasks = 0
        let completedTasks = 0

        // Получаем задачи доски если есть колонки
        if (columnIds.length > 0) {
          const { data: tasksData, error: tasksError } = await supabase
            .from('tasks')
            .select('id, is_completed, column_id')
            .in('column_id', columnIds)

          if (tasksError) {
            console.error(`❌ Ошибка загрузки задач для доски ${board.id}:`, tasksError)
          } else {
            totalTasks = tasksData?.length || 0
            
            // Считаем завершенные задачи (в колонке "Готово" или is_completed = true)
            completedTasks = tasksData?.filter(task => {
              const taskColumn = columnsData?.find(col => col.id === task.column_id)
              const columnTitle = taskColumn?.title?.toLowerCase() || ''
              
              return (
                columnTitle.includes('готов') || 
                columnTitle.includes('выполн') || 
                columnTitle.includes('done') || 
                columnTitle.includes('complete') ||
                task.is_completed === true
              )
            }).length || 0
          }
        }

        console.log(`📝 Задачи для доски ${board.title}: всего ${totalTasks}, завершено ${completedTasks}`)

        // Расчет прогресса: (completedTasks / totalTasks) * 100
        const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

        const members = membersData?.map(item => ({
          id: item.user_id,
          email: item.users?.email,
          role: item.roles?.name_role,
          isCurrentUser: item.user_id === userId
        })) || []

        console.log(`👥 Участники доски ${board.title}:`, members.length)

        projectsWithProgress.push({
          id: board.id,
          title: board.title,
          description: board.description,
          background: board.background,
          creator_id: board.creator_id,
          created_at: board.created_at,
          updated_at: board.updated_at,
          totalTasks,
          completedTasks,
          completionRate,
          members,
          isPersonal: members.length === 1 && board.creator_id === userId
        })

        console.log(`✅ Доска ${board.title} успешно обработана`)

      } catch (error) {
        console.error(`❌ Ошибка обработки доски ${board.id}:`, error)
        // Продолжаем обработку других досок
      }
    }

    projects.value = projectsWithProgress.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    console.log('🎉 Все проекты загружены:', projects.value.length)

  } catch (error) {
    console.error('💥 Общая ошибка загрузки проектов:', error)
    projects.value = []
  } finally {
    projectsLoading.value = false
    console.log('🏁 Загрузка проектов завершена')
  }
}

const getBoardAdmin = (boardId) => {
  const project = projects.value.find(p => p.id === boardId)
  if (!project) return null
  
  const adminMember = project.members.find(m => m.role === 'admin')
  return adminMember || null
}

const getProgressClass = (completionRate) => {
  if (completionRate >= 80) return 'progress-high'
  if (completionRate >= 50) return 'progress-medium'
  return 'progress-low'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleDateString('ru-RU')
  } catch {
    return ''
  }
}

const openProject = (project) => {
  router.push({ name: 'board', params: { id: project.id } })
}

const loadTasks = async () => {
  loading.value = true
  try {
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      console.error('Ошибка аутентификации при загрузке задач:', authError)
      loading.value = false
      return
    }

    const userId = user.id

    // Получаем ВСЕ задачи пользователя (и выполненные и не выполненные)
    const { data, error } = await supabase
      .from('tasks')
      .select(`
        *,
        columns!inner (
          id,
          title,
          boards!inner (
            id,
            title,
            background,
            description
          )
        )
      `)
      .or(`creator_id.eq.${userId},assignee_id.eq.${userId}`)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Ошибка загрузки задач:', error)
      tasks.value = []
    } else {
      tasks.value = data || []
      console.log('✅ Задачи загружены:', tasks.value.length)
    }
  } catch (error) {
    console.error('Общая ошибка загрузки задач:', error)
    tasks.value = []
  } finally {
    loading.value = false
  }
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
  console.log('🚀 Компонент Main.vue загружен')
  checkAdminStatus()
  loadTasks()
  loadProjectsWithProgress()
})
</script>

<style scoped>
.container {
  display: flex;
  min-height: 100vh;
}

.main {
  flex: 1;
  background: #480902;
  color: #E6D1A4;
}

.right-sidebar {
  width: 350px;
  background: #E6D1A4;
  color: #480902;
  padding: 20px;
  border-left: 2px solid #B54B11;
}

.page-content {
  padding: 20px;
}

.projects-header {
  font-size: 24px;
  font-weight: bold;
  color: #E6D1A4;
  margin-bottom: 20px;
  text-align: center;
}

.loading-info {
  text-align: center;
  padding: 10px;
  background: #B54B11;
  color: #E6D1A4;
  border-radius: 8px;
  margin-bottom: 15px;
}

.debug-info {
  text-align: center;
  padding: 8px;
  background: #CE7939;
  color: #480902;
  border-radius: 8px;
  margin-bottom: 15px;
  font-size: 0.9em;
}

.boards-sections {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.boards-section {
  display: flex;
  flex-direction: column;
}

.section-title {
  color: #E6D1A4;
  font-size: 18px;
  margin-bottom: 15px;
  border-bottom: 2px solid #B54B11;
  padding-bottom: 5px;
}

.boards-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.boards-card {
  background: #B54B11;
  color: #E6D1A4;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.boards-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

.boards-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.boards-pill {
  background: rgba(230, 209, 164, 0.18);
  color: #E6D1A4;
  border-radius: 14px;
  padding: 8px 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.boards-card-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
  flex-grow: 1;
}

.boards-card-item {
  background: #480902;
  color: #E6D1A4;
  border-radius: 10px;
  padding: 10px 12px;
}

.boards-card-item.muted {
  background: transparent;
  opacity: 0.8;
  padding: 0;
  font-size: 0.9em;
}

.item-title {
  font-weight: 500;
}

.boards-empty {
  color: #E6D1A4;
  opacity: 0.8;
  text-align: center;
  padding: 40px 20px;
  grid-column: 1 / -1;
}

.boards-card-footer {
  margin-top: auto;
}

.boards-btn {
  width: 100%;
  padding: 10px;
  background: #CE7939;
  color: #480902;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.boards-btn:hover {
  background: #E6D1A4;
}

/* Стили для прогресса */
.project-progress-section {
  background: rgba(72, 9, 2, 0.4);
  border-radius: 8px;
  padding: 12px;
  margin: 12px 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-text {
  font-size: 0.9em;
  color: #E6D1A4;
}

.progress-percentage {
  font-weight: bold;
  color: #CE7939;
  font-size: 1.1em;
}

.progress-bar {
  height: 8px;
  background: rgba(72, 9, 2, 0.6);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-high {
  background: #10b981;
}

.progress-medium {
  background: #f59e0b;
}

.progress-low {
  background: #ef4444;
}

.progress-stats {
  font-size: 0.8em;
  color: rgba(230, 209, 164, 0.8);
  text-align: center;
}

/* Стили для задач */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.tasks-count {
  background: #B54B11;
  color: #E6D1A4;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  font-weight: bold;
}

.tasks-container {
  max-height: 300px;
  overflow-y: auto;
}

.tasks-scrollable {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.task-item:hover {
  border-color: #B54B11;
}

.task-item.completed {
  background: #f0f9ff;
  border-color: #bae6fd;
  opacity: 0.8;
}

.task-item.rejected {
  background: #fef2f2;
  border-color: #fecaca;
}

.task-item label {
  flex: 1;
  cursor: pointer;
}

.task-title {
  font-weight: 500;
  color: #374151;
  display: block;
  margin-bottom: 6px;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}

.task-due-date {
  font-size: 0.8em;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.task-due-date.overdue {
  background: #fee2e2;
  color: #dc2626;
}

.task-due-date.today {
  background: #fed7aa;
  color: #c2410c;
}

.task-due-date.urgent {
  background: #fef3c7;
  color: #92400e;
}

.priority-badge {
  font-size: 0.7em;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  text-transform: uppercase;
}

.priority-badge.low {
  background: #d1fae5;
  color: #065f46;
}

.priority-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.priority-badge.high {
  background: #fee2e2;
  color: #991b1b;
}

.priority-badge.critical {
  background: #fecaca;
  color: #7f1d1d;
}

.approval-badge {
  font-size: 0.7em;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.approval-badge.rejected {
  background: #fee2e2;
  color: #dc2626;
}

.task-project {
  margin-top: 4px;
}

.project-badge {
  font-size: 0.7em;
  padding: 2px 8px;
  border-radius: 12px;
  color: white;
  font-weight: 500;
}

.loading-tasks {
  text-align: center;
  padding: 20px;
  color: #6b7280;
}

.no-tasks {
  text-align: center;
  padding: 30px;
  color: #9ca3af;
  font-style: italic;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #E6D1A4;
}
</style>