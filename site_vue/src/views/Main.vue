<template>
  <div class="container">
    <div class="main">
      <div class="page-content active" id="active-projects">
        <div class="projects-header">АКТИВНЫЕ ПРОЕКТЫ</div>

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
              <div v-if="personalProjects.length === 0" class="boards-empty">Нет личных проектов</div>
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
              <div v-if="teamProjects.length === 0" class="boards-empty">Нет командных проектов</div>
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
              v-for="task in tasks" 
              :key="task.id" 
              class="task-item"
              :class="{ 
                completed: task.is_completed && task.approval_status === 'approved',
                pending: task.approval_status === 'pending',
                rejected: task.approval_status === 'rejected'
              }"
            >
              <input 
                type="checkbox" 
                :id="'task' + task.id"
                :checked="task.is_completed && task.approval_status === 'approved'"
                @change="toggleTask(task)"
                :disabled="task.approval_status === 'pending'"
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
                  <span v-if="task.approval_status === 'pending'" class="approval-badge pending">
                    ⏳ На проверке
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

const personalProjects = computed(() => {
  return projects.value.filter(project => project.isPersonal)
})

const teamProjects = computed(() => {
  return projects.value.filter(project => !project.isPersonal)
})

const loadProjectsWithProgress = async () => {
  projectsLoading.value = true
  console.log('Начало загрузки проектов...')
  
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
    console.log('ID пользователя:', userId)

    // Получаем все доски пользователя через user_roles
    const { data: userRoles, error: rolesError } = await supabase
      .from('user_roles')
      .select(`
        board_id,
        boards (
          id,
          title,
          description,
          background,
          creator_id,
          created_at,
          updated_at
        )
      `)
      .eq('user_id', userId)

    if (rolesError) {
      console.error('Ошибка загрузки user_roles:', rolesError)
    }

    // Получаем доски, созданные пользователем
    const { data: createdBoards, error: createdError } = await supabase
      .from('boards')
      .select('*')
      .eq('creator_id', userId)

    if (createdError) {
      console.error('Ошибка загрузки созданных досок:', createdError)
    }

    console.log('Доски из user_roles:', userRoles)
    console.log('Созданные доски:', createdBoards)

    // Объединяем все доски
    const allBoards = []
    const boardIds = new Set()

    // Добавляем доски из user_roles
    if (userRoles) {
      userRoles.forEach(role => {
        if (role.boards && !boardIds.has(role.boards.id)) {
          boardIds.add(role.boards.id)
          allBoards.push(role.boards)
        }
      })
    }

    // Добавляем созданные доски
    if (createdBoards) {
      createdBoards.forEach(board => {
        if (!boardIds.has(board.id)) {
          boardIds.add(board.id)
          allBoards.push(board)
        }
      })
    }

    console.log('Все доски:', allBoards)

    const projectsWithProgress = []

    // Для каждой доски считаем прогресс
    for (const board of allBoards) {
      console.log('Обработка доски:', board.title)

      // Получаем участников доски
      const { data: boardMembers, error: membersError } = await supabase
        .from('user_roles')
        .select('user_id')
        .eq('board_id', board.id)

      if (membersError) {
        console.error('Ошибка загрузки участников:', membersError)
      }

      // Получаем колонки доски
      const { data: boardColumns, error: columnsError } = await supabase
        .from('columns')
        .select('id')
        .eq('board_id', board.id)

      if (columnsError) {
        console.error('Ошибка загрузки колонок:', columnsError)
      }

      const columnIds = boardColumns?.map(col => col.id) || []
      console.log('Колонки доски:', columnIds)

      // Получаем задачи доски
      let totalTasks = 0
      let completedTasks = 0

      if (columnIds.length > 0) {
        const { data: tasksData, error: tasksError } = await supabase
          .from('tasks')
          .select('id, is_completed, approval_status')
          .in('column_id', columnIds)

        if (tasksError) {
          console.error('Ошибка загрузки задач:', tasksError)
        } else {
          totalTasks = tasksData?.length || 0
          // Считаем задачу завершенной только если она выполнена И подтверждена
          completedTasks = tasksData?.filter(task => 
            task.is_completed && task.approval_status === 'approved'
          ).length || 0
          console.log(`Задачи доски ${board.title}: всего ${totalTasks}, выполнено ${completedTasks}`)
        }
      }

      // Правильный расчет процента завершенности
      const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

      // Получаем информацию об участниках
      const { data: membersData, error: membersDataError } = await supabase
        .from('user_roles')
        .select(`
          user_id,
          users:user_id (email, id),
          roles:role_id (name_role)
        `)
        .eq('board_id', board.id)

      const members = membersData?.map(item => ({
        id: item.user_id,
        email: item.users?.email,
        role: item.roles?.name_role,
        isCurrentUser: item.user_id === userId
      })) || []

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
    }

    projects.value = projectsWithProgress.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    console.log('Итоговые проекты:', projects.value)

  } catch (error) {
    console.error('Общая ошибка загрузки проектов:', error)
    projects.value = []
  } finally {
    projectsLoading.value = false
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

    // Получаем задачи пользователя с информацией о проектах
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
      console.log('Загруженные задачи:', tasks.value)
    }
  } catch (error) {
    console.error('Общая ошибка загрузки задач:', error)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const toggleTask = async (task) => {
  try {
    const { error } = await supabase
      .from('tasks')
      .update({ 
        is_completed: !task.is_completed,
        approval_status: task.is_completed ? 'pending' : 'pending',
        updated_at: new Date().toISOString()
      })
      .eq('id', task.id)

    if (error) throw error
    
    task.is_completed = !task.is_completed
    task.approval_status = 'pending'
    
    if (task.is_completed) {
      await loadProjectsWithProgress()
    }
  } catch (error) {
    console.error('Ошибка обновления задачи:', error)
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
  console.log('Компонент Main.vue загружен')
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

</style>