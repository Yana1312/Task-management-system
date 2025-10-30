<template>
  <div class="container">
    <div class="main">
      <div class="page-content active" id="board-page">
        <div class="board-header">{{ board?.title || 'Доска' }}</div>

        <div v-if="loading" class="board-loading">Загрузка...</div>
        <div v-else class="kanban-wrap">
          <div v-for="col in columns" :key="col.id" class="kanban-column">
            <div class="kanban-col-title">{{ col.title }}</div>
            <div class="kanban-items">
              <div 
                v-for="t in tasksByColumn[col.id] || []" 
                :key="t.id" 
                class="kanban-item"
                @click="openTaskDetails(t)"
              >
                <div class="item-title">{{ t.title }}</div>
                <div class="item-desc" v-if="t.description">{{ t.description }}</div>
                
                <!-- Добавлено: отображение срока выполнения -->
                <div v-if="t.due_date" class="item-due-date" :class="getDueDateClass(t.due_date)">
                  <span class="due-date-icon">📅</span>
                  {{ formatDueDate(t.due_date) }}
                </div>
                
                <div class="item-meta">
                  <span v-if="t.priority" :class="['priority-badge', `priority-${t.priority}`]">
                    {{ getPriorityText(t.priority) }}
                  </span>
                  <span v-if="getTaskMembers(t.id).length > 0" class="member-count">
                    {{ getTaskMembers(t.id).length }} участников
                  </span>
                </div>
              </div>
              <div v-if="(tasksByColumn[col.id] || []).length === 0" class="kanban-empty">Нет задач</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Кнопка создания -->
      <button class="boards-create-btn" @click="openModal" aria-label="Создать задачу">+</button>
    </div>

    <!-- Модальное окно создания задачи -->
    <div v-if="showModal" class="boards-modal-overlay" @click="closeModal">
      <div class="boards-modal boards-modal-large" @click.stop>
        <div class="boards-modal-header">
          <h2 class="boards-modal-title">Создание задачи</h2>
          <button class="boards-modal-close" @click="closeModal">×</button>
        </div>
        
        <div class="boards-modal-body">
          <div class="boards-modal-section">
            <div class="boards-modal-field">
              <label class="boards-modal-label">Название задачи *</label>
              <input 
                v-model="newTask.title" 
                class="boards-modal-input" 
                placeholder="Введите название задачи"
              />
            </div>
            
            <div class="boards-modal-field">
              <label class="boards-modal-label">Описание</label>
              <textarea 
                v-model="newTask.description" 
                class="boards-modal-textarea" 
                placeholder="Описание задачи"
              ></textarea>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Колонка</label>
              <select v-model="newTask.column_id" class="boards-modal-input">
                <option v-for="col in columns" :key="col.id" :value="col.id">
                  {{ col.title }}
                </option>
              </select>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Приоритет</label>
              <select v-model="newTask.priority" class="boards-modal-input">
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
                <option value="critical">Критический</option>
              </select>
            </div>

            <!-- Добавлено: поле выбора срока выполнения -->
            <div class="boards-modal-field">
              <label class="boards-modal-label">Срок выполнения</label>
              <input 
                type="date" 
                v-model="newTask.due_date" 
                class="boards-modal-input" 
                :min="new Date().toISOString().split('T')[0]"
              />
              <div class="boards-modal-hint">
                Оставьте пустым, если срок не установлен
              </div>
            </div>
          </div>

          <!-- Секция добавления участников -->
          <div class="boards-modal-section">
            <div class="boards-modal-field">
              <label class="boards-modal-label">Добавить участников</label>
              <div class="boards-members-add">
                <input 
                  v-model="newMemberEmail" 
                  class="boards-modal-input" 
                  placeholder="Email участника"
                  @keyup.enter="addMember"
                />
                <button class="boards-add-member-btn" @click="addMember">Добавить</button>
              </div>
            </div>

            <div v-if="currentTaskMembers.length > 0" class="boards-members-list">
              <div class="boards-members-title">Участники задачи:</div>
              <div 
                v-for="(member, index) in currentTaskMembers" 
                :key="index"
                class="boards-member-item"
              >
                <div class="boards-member-info">
                  <span class="boards-member-email">{{ member }}</span>
                </div>
                <div class="boards-member-actions">
                  <button 
                    class="boards-member-btn boards-member-btn-remove"
                    @click="removeMember(index)"
                    title="Удалить"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="boards-modal-actions">
          <button class="boards-modal-btn boards-modal-btn-cancel" @click="closeModal">
            Отменить
          </button>
          <button 
            class="boards-modal-btn boards-modal-btn-create" 
            @click="createTask"
            :disabled="!newTask.title.trim() || creating"
          >
            {{ creating ? 'Создание...' : 'Создать задачу' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно просмотра задачи -->
    <div v-if="showTaskModal" class="boards-modal-overlay" @click="closeTaskModal">
      <div class="boards-modal boards-modal-large" @click.stop>
        <div class="boards-modal-header">
          <h2 class="boards-modal-title">Редактирование задачи</h2>
          <button class="boards-modal-close" @click="closeTaskModal">×</button>
        </div>
        
        <div class="boards-modal-body">
          <div class="boards-modal-section">
            <!-- Изменено: поле названия стало редактируемым -->
            <div class="boards-modal-field">
              <label class="boards-modal-label">Название задачи *</label>
              <input 
                v-model="selectedTask.title" 
                class="boards-modal-input" 
                placeholder="Введите название задачи"
                @input="debouncedUpdateTitle"
                :disabled="updating"
              />
            </div>
            
            <!-- Изменено: поле описания стало редактируемым -->
            <div class="boards-modal-field">
              <label class="boards-modal-label">Описание</label>
              <textarea 
                v-model="selectedTask.description" 
                class="boards-modal-textarea" 
                placeholder="Описание задачи"
                @input="debouncedUpdateDescription"
                :disabled="updating"
              ></textarea>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Статус</label>
              <select 
                v-model="selectedTask.column_id" 
                class="boards-modal-input"
                @change="updateTaskStatus"
              >
                <option v-for="col in columns" :key="col.id" :value="col.id">
                  {{ col.title }}
                </option>
              </select>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Приоритет</label>
              <select 
                v-model="selectedTask.priority" 
                class="boards-modal-input"
                @change="updateTaskPriority"
              >
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
                <option value="critical">Критический</option>
              </select>
            </div>

            <!-- Добавлено: редактирование срока выполнения -->
            <div class="boards-modal-field">
              <label class="boards-modal-label">Срок выполнения</label>
              <input 
                type="date" 
                v-model="selectedTask.due_date" 
                class="boards-modal-input"
                @change="updateTaskDueDate"
              />
              <div class="boards-modal-hint">
                <span v-if="selectedTask?.due_date" :class="getDueDateClass(selectedTask.due_date)">
                  {{ getDueDateText(selectedTask.due_date) }}
                </span>
                <span v-else>Срок не установлен</span>
              </div>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Дата создания</label>
              <div class="task-created-date">
                {{ formatDate(selectedTask.created_at) }}
              </div>
            </div>
          </div>

          <div class="boards-modal-section" v-if="selectedTaskMembers.length > 0">
            <div class="boards-modal-field">
              <label class="boards-modal-label">Участники задачи</label>
              <div class="boards-members-list">
                <div 
                  v-for="member in selectedTaskMembers" 
                  :key="member.id"
                  class="boards-member-item"
                >
                  <div class="boards-member-info">
                    <span class="boards-member-email">{{ member.user_email }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Кнопки действий -->
          <div class="boards-modal-section">
            <div class="boards-modal-actions">
              <button 
                class="boards-modal-btn boards-modal-btn-danger" 
                @click="deleteTask"
                :disabled="deleting"
              >
                {{ deleting ? 'Удаление...' : 'Удалить задачу' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast уведомления -->
    <div v-if="toast.visible" :class="['toast', `toast-${toast.type}`]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { supabase } from '../lib/supabase.js'

const route = useRoute()
const boardId = ref(route.params.id)
const board = ref(null)
const columns = ref([])
const tasks = ref([])
const taskMembers = ref([])
const loading = ref(true)
const currentUser = ref(null)

// Модальные окна
const showModal = ref(false)
const showTaskModal = ref(false)
const creating = ref(false)
const deleting = ref(false)
const updating = ref(false)

// Данные для форм
const newTask = ref({
  title: '',
  description: '',
  column_id: null,
  priority: 'medium',
  due_date: null
})
const newMemberEmail = ref('')
const currentTaskMembers = ref([])
const selectedTask = ref(null)
const selectedTaskMembers = ref([])

// Таймеры для дебаунса
let titleUpdateTimeout = null
let descriptionUpdateTimeout = null

// Уведомления
const toast = ref({ visible: false, type: 'success', message: '' })

// Computed
const tasksByColumn = computed(() => {
  const grouped = {}
  columns.value.forEach(col => {
    grouped[col.id] = tasks.value.filter(task => task.column_id === col.id)
  })
  return grouped
})

// Получаем текущего пользователя
const getCurrentUser = async () => {
  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (user) {
      currentUser.value = user
      console.log('Текущий пользователь:', user)
      
      const { data: userData, error } = await supabase
        .from('users')
        .select('id')
        .eq('id', user.id)
        .single()
      
      if (error) {
        console.log('Пользователь не найден в таблице users, создаем...')
        const { data: newUser, error: createError } = await supabase
          .from('users')
          .insert({
            id: user.id,
            email: user.email,
            username: user.email.split('@')[0],
            password_hash: 'auth_user_no_password',
            created_at: new Date().toISOString()
          })
          .select()
          .single()
        
        if (createError) {
          console.error('Ошибка создания пользователя:', createError)
        } else {
          console.log('Пользователь создан в таблице users:', newUser)
        }
      } else {
        console.log('Пользователь найден в таблице users:', userData)
      }
    }
  } catch (error) {
    console.error('Ошибка получения пользователя:', error)
  }
}

// Методы для участников
const addMember = () => {
  const email = newMemberEmail.value.trim().toLowerCase()
  
  if (!email) {
    showToast('Введите email участника', 'error')
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    showToast('Введите корректный email', 'error')
    return
  }
  
  if (currentTaskMembers.value.includes(email)) {
    showToast('Этот участник уже добавлен', 'error')
    return
  }
  
  currentTaskMembers.value.push(email)
  newMemberEmail.value = ''
  showToast('Участник добавлен', 'success')
}

const removeMember = (index) => {
  currentTaskMembers.value.splice(index, 1)
}

// Методы для работы со сроками
const formatDueDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short'
  })
}

const getDueDateClass = (dateString) => {
  if (!dateString) return ''
  
  const dueDate = new Date(dateString)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const timeDiff = dueDate.getTime() - today.getTime()
  const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24))
  
  if (daysDiff < 0) {
    return 'due-date-overdue'
  } else if (daysDiff === 0) {
    return 'due-date-today'
  } else if (daysDiff <= 3) {
    return 'due-date-soon'
  }
  return 'due-date-normal'
}

const getDueDateText = (dateString) => {
  if (!dateString) return ''
  
  const dueDate = new Date(dateString)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const timeDiff = dueDate.getTime() - today.getTime()
  const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24))
  
  if (daysDiff < 0) {
    return `Просрочено на ${Math.abs(daysDiff)} дн.`
  } else if (daysDiff === 0) {
    return 'Сегодня'
  } else if (daysDiff === 1) {
    return 'Завтра'
  } else if (daysDiff <= 3) {
    return `Через ${daysDiff} дн.`
  }
  return `Осталось ${daysDiff} дн.`
}

// Дебаунс функции для обновления
const debouncedUpdateTitle = () => {
  clearTimeout(titleUpdateTimeout)
  titleUpdateTimeout = setTimeout(() => {
    updateTaskTitle()
  }, 1000)
}

const debouncedUpdateDescription = () => {
  clearTimeout(descriptionUpdateTimeout)
  descriptionUpdateTimeout = setTimeout(() => {
    updateTaskDescription()
  }, 1000)
}

// Методы модальных окон
const openModal = () => {
  showModal.value = true
  if (columns.value.length > 0 && !newTask.value.column_id) {
    newTask.value.column_id = columns.value[0].id
  }
}

const closeModal = () => {
  showModal.value = false
  newTask.value = {
    title: '',
    description: '',
    column_id: columns.value.length > 0 ? columns.value[0].id : null,
    priority: 'medium',
    due_date: null
  }
  currentTaskMembers.value = []
  newMemberEmail.value = ''
}

const openTaskDetails = async (task) => {
  selectedTask.value = { ...task }
  await loadTaskMembers(task.id)
  showTaskModal.value = true
}

const closeTaskModal = () => {
  showTaskModal.value = false
  selectedTask.value = null
  selectedTaskMembers.value = []
  // Очищаем таймеры при закрытии модалки
  clearTimeout(titleUpdateTimeout)
  clearTimeout(descriptionUpdateTimeout)
}

// Вспомогательные методы
const getColumnTitle = (columnId) => {
  const column = columns.value.find(col => col.id === columnId)
  return column ? column.title : 'Неизвестно'
}

const getTaskMembers = (taskId) => {
  return taskMembers.value.filter(member => member.task_id === taskId)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('ru-RU')
}

const getPriorityText = (priority) => {
  const priorities = {
    low: 'Низкий',
    medium: 'Средний',
    high: 'Высокий',
    critical: 'Критический'
  }
  return priorities[priority] || priority
}

// Основные методы
const createTask = async () => {
  if (!newTask.value.title.trim()) return
  
  creating.value = true
  try {
    console.log('Создание задачи для доски:', boardId.value)
    console.log('Данные задачи:', newTask.value)
    
    if (!newTask.value.column_id) {
      throw new Error('Не выбрана колонка для задачи')
    }

    if (!currentUser.value) {
      throw new Error('Пользователь не авторизован')
    }

    const taskData = {
      title: newTask.value.title,
      description: newTask.value.description || null,
      column_id: newTask.value.column_id,
      position: tasks.value.length,
      creator_id: currentUser.value.id,
      assignee_id: currentUser.value.id,
      priority: newTask.value.priority || 'medium',
      due_date: newTask.value.due_date || null,
      created_at: new Date().toISOString()
    }

    console.log('Отправляемые данные задачи:', taskData)

    const { data: taskDataResult, error: taskError } = await supabase
      .from('tasks')
      .insert(taskData)
      .select()
      .single()

    if (taskError) {
      console.error('Ошибка создания задачи:', taskError)
      throw taskError
    }

    console.log('Задача создана:', taskDataResult)

    if (currentTaskMembers.value.length > 0) {
      console.log('Добавление участников:', currentTaskMembers.value)
      
      const { data: users, error: usersError } = await supabase
        .from('users')
        .select('id, email')
        .in('email', currentTaskMembers.value)

      if (usersError) {
        console.error('Ошибка поиска пользователей:', usersError)
        showToast('Ошибка при поиске пользователей', 'error')
      } else if (users && users.length > 0) {
        const membersToInsert = users.map(user => ({
          task_id: taskDataResult.id,
          user_id: user.id,
          role: 'member',
          added_at: new Date().toISOString()
        }))

        const { error: membersError } = await supabase
          .from('task_members')
          .insert(membersToInsert)

        if (membersError) {
          console.error('Ошибка добавления участников:', membersError)
          showToast('Задача создана, но участники не добавлены', 'error')
        } else {
          taskMembers.value.push(...membersToInsert)
          console.log('Участники добавлены')
        }
      } else {
        console.log('Участники не найдены в системе')
        showToast('Задача создана, но участники не найдены в системе', 'warning')
      }
    }

    tasks.value.push(taskDataResult)
    
    closeModal()
    showToast('Задача успешно создана в колонке "' + getColumnTitle(newTask.value.column_id) + '"!', 'success')
    
  } catch (error) {
    console.error('Error creating task:', error)
    
    let errorMessage = 'Ошибка при создании задачи'
    if (error.message.includes('creator_id') || error.message.includes('assignee_id')) {
      errorMessage = 'Проблема с привязкой пользователя. Убедитесь, что вы авторизованы.'
    } else if (error.message.includes('Не выбрана колонка')) {
      errorMessage = 'Выберите колонку для задачи'
    } else if (error.message.includes('Пользователь не авторизован')) {
      errorMessage = 'Вы не авторизованы'
    }
    
    showToast(errorMessage, 'error')
  } finally {
    creating.value = false
  }
}

// Обновление названия задачи
const updateTaskTitle = async () => {
  if (!selectedTask.value || !selectedTask.value.title.trim()) {
    showToast('Название задачи не может быть пустым', 'error')
    return
  }
  
  updating.value = true
  try {
    console.log('Обновление названия задачи:', selectedTask.value.title)
    
    const { error } = await supabase
      .from('tasks')
      .update({ 
        title: selectedTask.value.title,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedTask.value.id)

    if (error) {
      console.error('Ошибка обновления названия:', error)
      throw error
    }

    // Обновляем локальные данные
    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].title = selectedTask.value.title
    }

    console.log('Название задачи успешно обновлено')
    showToast('Название задачи обновлено!', 'success')
  } catch (error) {
    console.error('Ошибка обновления названия:', error)
    showToast('Ошибка при обновлении названия', 'error')
  } finally {
    updating.value = false
  }
}

// Обновление описания задачи
const updateTaskDescription = async () => {
  if (!selectedTask.value) return
  
  updating.value = true
  try {
    console.log('Обновление описания задачи')
    
    const { error } = await supabase
      .from('tasks')
      .update({ 
        description: selectedTask.value.description || null,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedTask.value.id)

    if (error) {
      console.error('Ошибка обновления описания:', error)
      throw error
    }

    // Обновляем локальные данные
    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].description = selectedTask.value.description
    }

    console.log('Описание задачи успешно обновлено')
    showToast('Описание задачи обновлено!', 'success')
  } catch (error) {
    console.error('Ошибка обновления описания:', error)
    showToast('Ошибка при обновлении описания', 'error')
  } finally {
    updating.value = false
  }
}

// Обновление статуса задачи
const updateTaskStatus = async () => {
  if (!selectedTask.value) return
  
  try {
    const { error } = await supabase
      .from('tasks')
      .update({ 
        column_id: selectedTask.value.column_id,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedTask.value.id)

    if (error) throw error

    // Обновляем локальные данные
    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].column_id = selectedTask.value.column_id
    }

    showToast('Статус задачи обновлен!', 'success')
  } catch (error) {
    console.error('Ошибка обновления статуса:', error)
    showToast('Ошибка при обновлении статуса', 'error')
  }
}

// Обновление приоритета задачи
const updateTaskPriority = async () => {
  if (!selectedTask.value) return
  
  try {
    const { error } = await supabase
      .from('tasks')
      .update({ 
        priority: selectedTask.value.priority,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedTask.value.id)

    if (error) throw error

    // Обновляем локальные данные
    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].priority = selectedTask.value.priority
    }

    showToast('Приоритет задачи обновлен!', 'success')
  } catch (error) {
    console.error('Ошибка обновления приоритета:', error)
    showToast('Ошибка при обновлении приоритета', 'error')
  }
}

// Обновление срока выполнения
const updateTaskDueDate = async () => {
  if (!selectedTask.value) return
  
  try {
    const { error } = await supabase
      .from('tasks')
      .update({ 
        due_date: selectedTask.value.due_date,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedTask.value.id)

    if (error) throw error

    // Обновляем локальные данные
    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].due_date = selectedTask.value.due_date
    }

    showToast('Срок выполнения обновлен!', 'success')
  } catch (error) {
    console.error('Ошибка обновления срока:', error)
    showToast('Ошибка при обновлении срока', 'error')
  }
}

// Удаление задачи
const deleteTask = async () => {
  if (!selectedTask.value) return
  
  deleting.value = true
  try {
    const { error } = await supabase
      .from('tasks')
      .delete()
      .eq('id', selectedTask.value.id)

    if (error) throw error

    // Удаляем из локального списка
    tasks.value = tasks.value.filter(t => t.id !== selectedTask.value.id)

    closeTaskModal()
    showToast('Задача удалена!', 'success')
  } catch (error) {
    console.error('Ошибка удаления задачи:', error)
    showToast('Ошибка при удалении задачи', 'error')
  } finally {
    deleting.value = false
  }
}

const showToast = (message, type = 'success') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

// Загрузка данных
const loadBoard = async () => {
  try {
    const { data, error } = await supabase
      .from('boards')
      .select('*')
      .eq('id', boardId.value)
      .single()
    
    if (error) throw error
    board.value = data
    console.log('Доска загружена:', board.value)
  } catch (error) {
    console.error('Error loading board:', error)
    showToast('Ошибка загрузки доски', 'error')
  }
}

const loadColumns = async () => {
  try {
    const { data, error } = await supabase
      .from('columns')
      .select('*')
      .eq('board_id', boardId.value)
      .order('position', { ascending: true })
    
    if (error) throw error
    columns.value = data || []
    console.log('Колонки загружены:', columns.value)
    
    if (columns.value.length > 0 && !newTask.value.column_id) {
      newTask.value.column_id = columns.value[0].id
    }
  } catch (error) {
    console.error('Error loading columns:', error)
    columns.value = []
  }
}

const loadTasks = async () => {
  try {
    if (columns.value.length > 0) {
      const columnIds = columns.value.map(col => col.id)
      
      const { data, error } = await supabase
        .from('tasks')
        .select('*')
        .in('column_id', columnIds)
        .order('position', { ascending: true })
      
      if (error) throw error
      tasks.value = data || []
      console.log('Задачи загружены:', tasks.value)
    } else {
      tasks.value = []
    }
  } catch (error) {
    console.error('Error loading tasks:', error)
    tasks.value = []
  }
}

const loadTaskMembers = async (taskId = null) => {
  try {
    let query = supabase.from('task_members').select('*')
    
    if (taskId) {
      query = query.eq('task_id', taskId)
      const { data, error } = await query
      if (error) throw error
      selectedTaskMembers.value = data || []
    } else {
      if (tasks.value.length > 0) {
        query = query.in('task_id', tasks.value.map(t => t.id))
        const { data, error } = await query
        if (error) throw error
        taskMembers.value = data || []
      }
    }
  } catch (error) {
    console.error('Error loading task members:', error)
    if (taskId) {
      selectedTaskMembers.value = []
    } else {
      taskMembers.value = []
    }
  }
}

const loadData = async () => {
  loading.value = true
  try {
    await getCurrentUser()
    await loadBoard()
    await loadColumns()
    await loadTasks()
    await loadTaskMembers()
  } catch (error) {
    console.error('Error loading data:', error)
    showToast('Ошибка загрузки данных', 'error')
  } finally {
    loading.value = false
  }
}

// Обновляем задачи при изменении колонок
watch(columns, () => {
  if (columns.value.length > 0) {
    loadTasks()
  }
})

onMounted(() => {
  loadData()
})
</script>