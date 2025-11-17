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
                  <div class="boards-card-item muted">Окончание: {{ project.end_date ? formatDate(project.end_date) : 'Не указана' }}</div>
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
                  <div class="boards-card-item muted">Окончание: {{ project.end_date ? formatDate(project.end_date) : 'Не указана' }}</div>
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
import { useRouter } from 'vue-router'
import { supabase } from '../lib/supabase.js'
import { auth } from '../js/auth.js'
import PomodoroTimer from '../components/PomodoroTimer.vue'
import demoDataRaw from '../assets/demo_data.json'

const router = useRouter()
const tasks = ref([])
const projects = ref([])
const loading = ref(true)
const projectsLoading = ref(true)
const cardBg = ref('#B54B11')
const isAdmin = ref(false)
const demoData = ref(null)

function loadDemoData() {
  const persisted = (() => { try { return JSON.parse(localStorage.getItem('demo_data') || 'null') } catch { return null } })()
  demoData.value = persisted || demoDataRaw
}

function saveDemoData() {
  try { localStorage.setItem('demo_data', JSON.stringify(demoData.value)) } catch {}
}

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

const sortedTasks = computed(() => {
  return [...tasks.value].sort((a, b) => {
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
    const priorityA = priorityOrder[a.priority] || 4
    const priorityB = priorityOrder[b.priority] || 4
    
    return priorityA - priorityB
  })
})

const personalProjects = computed(() => {
  return projects.value.filter(project => project.isPersonal)
})

const teamProjects = computed(() => {
  return projects.value.filter(project => !project.isPersonal)
})

const checkAdminStatus = async () => {
  if (auth.isDemo.value) { isAdmin.value = true; return }
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
  
  if (auth.isDemo.value) {
    try {
      loadDemoData()
      const boards = demoData.value.projects || []
      const columns = demoData.value.columns || []
      const tasksAll = demoData.value.tasks || []
      const userId = auth.userId.value || 'demo-user-id'
      const projectsWithProgress = boards.map((board) => {
        const columnIds = columns.filter(c => c.board_id === board.id).map(c => c.id)
        const tasksData = tasksAll.filter(t => columnIds.includes(t.column_id))
        const totalTasks = tasksData.length
        const completedTasks = tasksData.filter(task => {
          const taskColumn = columns.find(col => col.id === task.column_id)
          const columnTitle = taskColumn?.title?.toLowerCase() || ''
          return (
            columnTitle.includes('готов') || columnTitle.includes('выполн') || columnTitle.includes('done') || columnTitle.includes('complete') || task.is_completed === true
          )
        }).length
        const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
        const members = board.members || []
        return {
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
        }
      })
      projects.value = projectsWithProgress.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    } catch (e) {
      console.error('Ошибка демо загрузки проектов:', e)
      projects.value = []
    } finally {
      projectsLoading.value = false
    }
    return
  }

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

    // === Оптимизация загрузки: объединяем запросы ===
    const projectsWithProgress = []

    // Загружаем участников для всех досок одним запросом
    const { data: allMembers, error: allMembersError } = await supabase
      .from('user_roles')
      .select(`
        board_id,
        user_id,
        users:user_id (email, id),
        roles:role_id (name_role)
      `)
      .in('board_id', assignedIds)

    if (allMembersError) {
      console.error('❌ Ошибка загрузки участников для всех досок:', allMembersError)
    }

    // Загружаем колонки для всех досок одним запросом
    const { data: allColumns, error: allColumnsError } = await supabase
      .from('columns')
      .select('id, title, board_id')
      .in('board_id', assignedIds)

    if (allColumnsError) {
      console.error('❌ Ошибка загрузки колонок для всех досок:', allColumnsError)
    }

    console.log('📊 Всего колонок загружено:', allColumns?.length || 0)

    // Готовим мапы для быстрых доступов
    const membersByBoard = new Map()
    ;(allMembers || []).forEach(item => {
      if (!membersByBoard.has(item.board_id)) membersByBoard.set(item.board_id, [])
      membersByBoard.get(item.board_id).push(item)
    })

    const columnsByBoard = new Map()
    ;(allColumns || []).forEach(col => {
      if (!columnsByBoard.has(col.board_id)) columnsByBoard.set(col.board_id, [])
      columnsByBoard.get(col.board_id).push(col)
    })

    const allColumnIds = (allColumns || []).map(c => c.id)

    let allTasksData = []
    if (allColumnIds.length > 0) {
      const { data: tasksData, error: tasksError } = await supabase
        .from('tasks')
        .select('id, is_completed, column_id')
        .in('column_id', allColumnIds)
      if (tasksError) {
        console.error('❌ Ошибка загрузки задач для всех досок:', tasksError)
      } else {
        allTasksData = tasksData || []
      }
    }

    // Группировка задач по колонке
    const tasksByColumn = new Map()
    allTasksData.forEach(task => {
      if (!tasksByColumn.has(task.column_id)) tasksByColumn.set(task.column_id, [])
      tasksByColumn.get(task.column_id).push(task)
    })

    // Сборка проектов с прогрессом
    for (const board of boardsData) {
      try {
        const columnsData = columnsByBoard.get(board.id) || []
        const columnIds = columnsData.map(c => c.id)
        const boardTasks = columnIds.flatMap(cid => tasksByColumn.get(cid) || [])

        const totalTasks = boardTasks.length
        const completedTasks = boardTasks.filter(task => {
          const taskColumn = columnsData.find(col => col.id === task.column_id)
          const columnTitle = taskColumn?.title?.toLowerCase() || ''

          return (
            columnTitle.includes('готов') ||
            columnTitle.includes('выполн') ||
            columnTitle.includes('done') ||
            columnTitle.includes('complete') ||
            task.is_completed === true
          )
        }).length

        

        const membersRaw = membersByBoard.get(board.id) || []
        const members = membersRaw.map(item => ({
          id: item.user_id,
          email: item.users?.email,
          role: item.roles?.name_role,
          isCurrentUser: item.user_id === userId
        }))

        projectsWithProgress.push({
          id: board.id,
          title: board.title,
          description: board.description,
          background: board.background,
          creator_id: board.creator_id,
          created_at: board.created_at,
          updated_at: board.updated_at,
          end_date: board.end_date,
          
          totalTasks,
          completedTasks,
          completionRate: totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0,
          members,
          isPersonal: members.length === 1 && board.creator_id === userId
        })
      } catch (error) {
        console.error(`❌ Ошибка обработки доски ${board.id}:`, error)
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

// === ФУНКЦИИ ИЗ ВЕРСИИ ДРУГОГО СОТРУДНИКА ДЛЯ "МОИХ ЗАДАЧ" ===

const loadTasks = async () => {
  if (auth.isDemo.value) {
    try {
      loadDemoData()
      const userId = auth.userId.value || 'demo-user-id'
      const columnsById = Object.fromEntries((demoData.value.columns || []).map(c => [c.id, c]))
      const boardsById = Object.fromEntries((demoData.value.projects || []).map(b => [b.id, b]))
      const all = (demoData.value.tasks || []).map(t => {
        const col = columnsById[t.column_id]
        const board = col ? boardsById[col.board_id] : null
        return {
          ...t,
          columns: {
            title: col?.title || 'Без колонки',
            boards: board ? { id: board.id, title: board.title, background: board.background, description: board.description } : null
          }
        }
      })
      tasks.value = all.filter(t => (t.assignee_id === userId || t.creator_id === userId) && t.is_completed === false)
    } catch (e) {
      console.error('Ошибка демо загрузки задач:', e)
      tasks.value = []
    } finally {
      loading.value = false
    }
    return
  }

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
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: 20px;
  margin-top: 15px;
  padding-bottom: 8px; /* место под горизонтальную полосу прокрутки */
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
  /* фиксируем высоту карточки, чтобы размер не менялся */
  height: 340px;
  /* для горизонтального скролла карточек */
  flex: 0 0 320px;
  min-width: 320px;
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
  overflow: hidden; /* предотвращаем рост карточки из-за контента */
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
  /* обрезаем длинные описания и добавляем многоточие */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}

.boards-empty {
  color: #E6D1A4;
  opacity: 0.8;
  text-align: center;
  padding: 40px 20px;
  /* растягиваем на всю ширину контейнера при flex */
  flex: 1 1 100%;
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

/* === СТИЛИ ДЛЯ ЗАДАЧ ИЗ ВЕРСИИ ДРУГОГО СОТРУДНИКА === */
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
  height: auto;
  background:transparent;
}

.tasks-scrollable {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
  max-height: 310px;
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
  /* фиксируем минимальную высоту одной карточки задачи */
  min-height: 80px;
}

.task-title {
  display: flex;
  font-weight: 500;
  margin-bottom: 4px;
  word-break: break-word;
}

.task-content {
  flex:1;
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

.loading {
  text-align: center;
  padding: 20px;
  color: #E6D1A4;
}

/* горизонтальная полоса прокрутки для карточек проектов */
.boards-row::-webkit-scrollbar {
  height: 8px;
}

.boards-row::-webkit-scrollbar-track {
  background: rgba(181, 75, 17, 0.1);
  border-radius: 4px;
}

.boards-row::-webkit-scrollbar-thumb {
  background: #CE7939;
  border-radius: 4px;
}

.boards-row::-webkit-scrollbar-thumb:hover {
  background: #B54B11;
}
</style>