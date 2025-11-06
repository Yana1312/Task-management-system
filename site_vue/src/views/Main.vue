<template>
  <div class="container">
    <div class="main">
      <div class="page-content active" id="active-projects">
        <div class="projects-header">АКТИВНЫЕ ПРОЕКТЫ</div>
        <div class="active-projects-main">
          <h3 class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</h3>
          <div 
            v-for="project in personalProjects" 
            :key="project.id"
            class="project-row"
          >
            <span class="project-name">{{ project.title }}</span>
            <div class="project-progress-container">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: project.completionRate + '%' }"
                  :class="getProgressClass(project.completionRate)"
                ></div>
              </div>
              <span class="project-progress">{{ project.completionRate }}%</span>
            </div>
          </div>

          <h3 class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</h3>
          <div 
            v-for="project in teamProjects" 
            :key="project.id"
            class="project-row"
          >
            <span class="project-name">{{ project.title }}</span>
            <div class="project-progress-container">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: project.completionRate + '%' }"
                  :class="getProgressClass(project.completionRate)"
                ></div>
              </div>
              <span class="project-progress">{{ project.completionRate }}%</span>
            </div>
          </div>
          
          <button class="show-more-button" @click="loadMoreProjects">ПОКАЗАТЬ БОЛЬШЕ...</button>
        </div>
      </div>

      <div class="page-content" id="all-projects">
        <div class="projects-container">
          <div class="main-header">СУЩЕСТВУЮЩИЕ ПРОЕКТЫ</div>
          <div class="project-sections">
            <div class="personal-projects">
              <h2 class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</h2>
              <div 
                v-for="project in personalProjects" 
                :key="project.id"
                class="project-card"
              >
                <div class="card-title">{{ project.title }}</div>
                <div class="project-progress-info">
                  <div class="progress-stats">
                    <span>Завершено: {{ project.completedTasks }}/{{ project.totalTasks }} задач</span>
                    <span class="progress-percentage">{{ project.completionRate }}%</span>
                  </div>
                  <div class="progress-bar-mini">
                    <div 
                      class="progress-fill-mini" 
                      :style="{ width: project.completionRate + '%' }"
                      :class="getProgressClass(project.completionRate)"
                    ></div>
                  </div>
                </div>
                <div class="lesson-item">
                  <div>
                    <div class="lesson-title">ПОСЛЕДНЯЯ АКТИВНОСТЬ</div>
                    <div class="lesson-time">Обновлено: {{ formatDate(project.updated_at) }}</div>
                  </div>
                  <i class="fas fa-pencil-alt edit-icon"></i>
                </div>
                <button class="edit-button" @click="openProject(project)">ОТКРЫТЬ ПРОЕКТ</button>
              </div>
            </div>
            <div class="team-projects">
              <h2 class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</h2>
              <div 
                v-for="project in teamProjects" 
                :key="project.id"
                class="project-card"
              >
                <div class="card-title">{{ project.title }}</div>
                <div class="project-progress-info">
                  <div class="progress-stats">
                    <span>Завершено: {{ project.completedTasks }}/{{ project.totalTasks }} задач</span>
                    <span class="progress-percentage">{{ project.completionRate }}%</span>
                  </div>
                  <div class="progress-bar-mini">
                    <div 
                      class="progress-fill-mini" 
                      :style="{ width: project.completionRate + '%' }"
                      :class="getProgressClass(project.completionRate)"
                    ></div>
                  </div>
                </div>
                <div class="lesson-item">
                  <div class="team-avatars">
                    <div 
                      v-for="member in project.members" 
                      :key="member.id"
                      class="avatar"
                      :class="member.isCurrentUser ? 'avatar-alt' : ''"
                      :title="member.email"
                    ></div>
                  </div>
                  <div>
                    <div class="lesson-title">КОМАНДА: {{ project.members.length }} участников</div>
                  </div>
                  <i class="fas fa-pencil-alt edit-icon"></i>
                </div>
                <button class="edit-button" @click="openProject(project)">ОТКРЫТЬ ПРОЕКТ</button>
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

const personalProjects = computed(() => {
  return projects.value.filter(project => project.isPersonal)
})

const teamProjects = computed(() => {
  return projects.value.filter(project => !project.isPersonal)
})

const loadProjectsWithProgress = async () => {
  projectsLoading.value = true
  const userId = await getCurrentUserId()
  if (!userId) {
    projectsLoading.value = false
    return
  }

  try {
    const { data: userBoards, error: boardsError } = await supabase
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

    if (boardsError) throw boardsError

    const { data: createdBoards, error: createdError } = await supabase
      .from('boards')
      .select('*')
      .eq('creator_id', userId)

    if (createdError) throw createdError

    const allBoardIds = new Set()
    const allBoards = []

    userBoards?.forEach(role => {
      if (role.boards && !allBoardIds.has(role.boards.id)) {
        allBoardIds.add(role.boards.id)
        allBoards.push(role.boards)
      }
    })

    createdBoards?.forEach(board => {
      if (!allBoardIds.has(board.id)) {
        allBoardIds.add(board.id)
        allBoards.push(board)
      }
    })

    const projectsWithProgress = []

    for (const board of allBoards) {
      const { data: boardMembers, error: membersError } = await supabase
        .from('user_roles')
        .select('user_id')
        .eq('board_id', board.id)

      if (membersError) {
        console.error('Ошибка загрузки участников:', membersError)
        continue
      }

      const { data: boardTasks, error: tasksError } = await supabase
        .from('tasks')
        .select('id, is_completed, approval_status')
        .eq('column_id', 
          supabase.from('columns')
            .select('id')
            .eq('board_id', board.id)
        )

      if (tasksError) {
        console.error('Ошибка загрузки задач:', tasksError)
        continue
      }

      const totalTasks = boardTasks?.length || 0
      const completedTasks = boardTasks?.filter(task => 
        task.is_completed && task.approval_status === 'approved'
      ).length || 0

      const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

      const { data: membersData, error: membersDataError } = await supabase
        .from('user_roles')
        .select(`
          user_id,
          users:user_id (email, id)
        `)
        .eq('board_id', board.id)

      const members = membersData?.map(item => ({
        id: item.user_id,
        email: item.users?.email,
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

    projects.value = projectsWithProgress.sort((a, b) => b.updated_at.localeCompare(a.updated_at))

  } catch (error) {
    console.error('Ошибка загрузки проектов:', error)
    projects.value = []
  } finally {
    projectsLoading.value = false
  }
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

const loadMoreProjects = () => {
  // В реальном приложении здесь будет пагинация
  console.log('Загрузка дополнительных проектов...')
}

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
      // Обновляем прогресс проектов
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
  loadTasks()
  loadProjectsWithProgress()
  
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
.project-progress-container {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 120px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(72, 9, 2, 0.3);
  border-radius: 4px;
  overflow: hidden;
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

.project-progress-info {
  margin-bottom: 15px;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  font-size: 0.9em;
  color: #E6D1A4;
}

.progress-percentage {
  font-weight: bold;
  color: #CE7939;
}

.progress-bar-mini {
  height: 6px;
  background: rgba(72, 9, 2, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill-mini {
  height: 100%;
  transition: width 0.3s ease;
}

.approval-badge {
  font-size: 0.7em;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.approval-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.approval-badge.rejected {
  background: #fee2e2;
  color: #dc2626;
}

.task-item.pending {
  border-left-color: #f59e0b;
}

.task-item.rejected {
  border-left-color: #ef4444;
}

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
  border-radius: 4px;
  color: #480902;
  background: #E6D1A4;
  border-left: 3px solid #B54B11;
  transition: all 0.2s ease;
}

.task-item input[type="checkbox"] {
  margin-right: 8px;
  margin-top: 2px;
}

.task-item label {
  margin: 0;
  font-size: 0.9em;
  flex: 1;
}

.task-title {
  display: block;
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