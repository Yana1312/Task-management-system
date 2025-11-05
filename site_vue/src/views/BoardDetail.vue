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
                
                <div v-if="t.due_date" class="item-due-date" :class="getDueDateClass(t.due_date)">
                  <span class="due-date-icon">📅</span>
                  {{ formatDueDate(t.due_date) }}
                </div>
                
                <div v-if="t.attachments && t.attachments.length > 0" class="item-attachments">
                  <div class="attachments-count">
                    📎 {{ t.attachments.length }} файл(ов)
                  </div>
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
      
      <button class="boards-create-btn" @click="openModal" aria-label="Создать задачу">+</button>
    </div>

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

    <div v-if="showTaskModal" class="boards-modal-overlay" @click="closeTaskModal">
      <div class="boards-modal boards-modal-large" @click.stop>
        <div class="boards-modal-header">
          <h2 class="boards-modal-title">Редактирование задачи</h2>
          <button class="boards-modal-close" @click="closeTaskModal">×</button>
        </div>
        
        <div class="boards-modal-body">
          <div class="boards-modal-section">
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

          <div class="boards-modal-section" v-if="isTaskCompleted">
            <div class="boards-modal-field">
              <label class="boards-modal-label">Прикрепленные файлы</label>
              <div class="file-upload-section">
                <div class="file-upload-area" 
                     @click="triggerFileInput"
                     @drop="handleFileDrop"
                     @dragover.prevent
                     @dragenter.prevent>
                  <input 
                    type="file" 
                    ref="fileInput"
                    @change="handleFileSelect"
                    multiple
                    style="display: none"
                  />
                  <div class="file-upload-content">
                    <div class="file-upload-icon">📎</div>
                    <div class="file-upload-text">
                      Перетащите файлы сюда или нажмите для выбора
                    </div>
                    <div class="file-upload-hint">
                      Максимальный размер: 10MB
                    </div>
                  </div>
                </div>
                
                <div v-if="selectedTask.attachments && selectedTask.attachments.length > 0" class="attachments-list">
                  <div class="attachments-title">Прикрепленные файлы:</div>
                  <div 
                    v-for="attachment in selectedTask.attachments" 
                    :key="attachment.id"
                    class="attachment-item"
                  >
                    <div class="attachment-info">
                      <span class="attachment-name">{{ attachment.filename }}</span>
                      <span class="attachment-size">{{ formatFileSize(attachment.file_size) }}</span>
                    </div>
                    <div class="attachment-actions">
                      <button 
                        class="attachment-btn attachment-download"
                        @click="downloadAttachment(attachment)"
                        title="Скачать"
                      >
                        ⬇️
                      </button>
                      <button 
                        class="attachment-btn attachment-delete"
                        @click="deleteAttachment(attachment.id)"
                        title="Удалить"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                </div>
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

const showModal = ref(false)
const showTaskModal = ref(false)
const creating = ref(false)
const deleting = ref(false)
const updating = ref(false)
const uploading = ref(false)

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

const fileInput = ref(null)

let titleUpdateTimeout = null
let descriptionUpdateTimeout = null

const toast = ref({ visible: false, type: 'success', message: '' })

const tasksByColumn = computed(() => {
  const grouped = {}
  columns.value.forEach(col => {
    grouped[col.id] = tasks.value.filter(task => task.column_id === col.id)
  })
  return grouped
})

const isTaskCompleted = computed(() => {
  if (!selectedTask.value) return false
  const doneColumn = columns.value.find(col => col.title.toLowerCase().includes('готово'))
  return doneColumn && selectedTask.value.column_id === doneColumn.id
})

const getCurrentUser = async () => {
  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (user) {
      currentUser.value = user
      
      const { data: userData, error } = await supabase
        .from('users')
        .select('id')
        .eq('id', user.id)
        .single()
      
      if (error) {
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
      }
    }
  } catch (error) {
    console.error('Ошибка получения пользователя:', error)
  }
}

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
  await loadTaskAttachments(task.id)
  showTaskModal.value = true
}

const closeTaskModal = () => {
  showTaskModal.value = false
  selectedTask.value = null
  selectedTaskMembers.value = []
  clearTimeout(titleUpdateTimeout)
  clearTimeout(descriptionUpdateTimeout)
}

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

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const createTask = async () => {
  if (!newTask.value.title.trim()) return
  
  creating.value = true
  try {
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

    const { data: taskDataResult, error: taskError } = await supabase
      .from('tasks')
      .insert(taskData)
      .select()
      .single()

    if (taskError) {
      throw taskError
    }

    if (currentTaskMembers.value.length > 0) {
      const { data: users, error: usersError } = await supabase
        .from('users')
        .select('id, email')
        .in('email', currentTaskMembers.value)

      if (!usersError && users && users.length > 0) {
        const membersToInsert = users.map(user => ({
          task_id: taskDataResult.id,
          user_id: user.id,
          role: 'member',
          added_at: new Date().toISOString()
        }))

        const { error: membersError } = await supabase
          .from('task_members')
          .insert(membersToInsert)

        if (!membersError) {
          taskMembers.value.push(...membersToInsert)
        }
      }
    }

    tasks.value.push(taskDataResult)
    
    closeModal()
    showToast('Задача успешно создана в колонке "' + getColumnTitle(newTask.value.column_id) + '"!', 'success')
    
  } catch (error) {
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

const updateTaskTitle = async () => {
  if (!selectedTask.value || !selectedTask.value.title.trim()) {
    showToast('Название задачи не может быть пустым', 'error')
    return
  }
  
  updating.value = true
  try {
    const { error } = await supabase
      .from('tasks')
      .update({ 
        title: selectedTask.value.title,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedTask.value.id)

    if (error) {
      throw error
    }

    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].title = selectedTask.value.title
    }

    showToast('Название задачи обновлено!', 'success')
  } catch (error) {
    showToast('Ошибка при обновлении названия', 'error')
  } finally {
    updating.value = false
  }
}

const updateTaskDescription = async () => {
  if (!selectedTask.value) return
  
  updating.value = true
  try {
    const { error } = await supabase
      .from('tasks')
      .update({ 
        description: selectedTask.value.description || null,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedTask.value.id)

    if (error) {
      throw error
    }

    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].description = selectedTask.value.description
    }

    showToast('Описание задачи обновлено!', 'success')
  } catch (error) {
    showToast('Ошибка при обновлении описания', 'error')
  } finally {
    updating.value = false
  }
}

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

    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].column_id = selectedTask.value.column_id
    }

    showToast('Статус задачи обновлен!', 'success')
  } catch (error) {
    showToast('Ошибка при обновлении статуса', 'error')
  }
}

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

    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].priority = selectedTask.value.priority
    }

    showToast('Приоритет задачи обновлен!', 'success')
  } catch (error) {
    showToast('Ошибка при обновлении приоритета', 'error')
  }
}

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

    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].due_date = selectedTask.value.due_date
    }

    showToast('Срок выполнения обновлен!', 'success')
  } catch (error) {
    showToast('Ошибка при обновлении срока', 'error')
  }
}

const deleteTask = async () => {
  if (!selectedTask.value) return
  
  deleting.value = true
  try {
    const { error } = await supabase
      .from('tasks')
      .delete()
      .eq('id', selectedTask.value.id)

    if (error) throw error

    tasks.value = tasks.value.filter(t => t.id !== selectedTask.value.id)

    closeTaskModal()
    showToast('Задача удалена!', 'success')
  } catch (error) {
    showToast('Ошибка при удалении задачи', 'error')
  } finally {
    deleting.value = false
  }
}

const showToast = (message, type = 'success') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

const loadBoard = async () => {
  try {
    const { data, error } = await supabase
      .from('boards')
      .select('*')
      .eq('id', boardId.value)
      .single()
    
    if (error) throw error
    board.value = data
  } catch (error) {
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
    
    if (columns.value.length > 0 && !newTask.value.column_id) {
      newTask.value.column_id = columns.value[0].id
    }
  } catch (error) {
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
      
      await loadTaskAttachmentsForAllTasks()
    } else {
      tasks.value = []
    }
  } catch (error) {
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
    if (taskId) {
      selectedTaskMembers.value = []
    } else {
      taskMembers.value = []
    }
  }
}

const loadTaskAttachments = async (taskId) => {
  try {
    const { data, error } = await supabase
      .from('attachments')
      .select('*')
      .eq('task_id', taskId)
      .order('uploaded_at', { ascending: false })
    
    if (error) throw error
    
    if (selectedTask.value && selectedTask.value.id === taskId) {
      selectedTask.value.attachments = data || []
    }
    
    return data || []
  } catch (error) {
    console.error('Ошибка загрузки вложений:', error)
    return []
  }
}

const loadTaskAttachmentsForAllTasks = async () => {
  try {
    if (tasks.value.length === 0) return
    
    const taskIds = tasks.value.map(t => t.id)
    const { data, error } = await supabase
      .from('attachments')
      .select('*')
      .in('task_id', taskIds)
    
    if (error) throw error
    
    const attachmentsByTask = {}
    data?.forEach(attachment => {
      if (!attachmentsByTask[attachment.task_id]) {
        attachmentsByTask[attachment.task_id] = []
      }
      attachmentsByTask[attachment.task_id].push(attachment)
    })
    
    tasks.value.forEach(task => {
      task.attachments = attachmentsByTask[task.id] || []
    })
  } catch (error) {
    console.error('Ошибка загрузки вложений для всех задач:', error)
  }
}

const triggerFileInput = () => {
  if (!isTaskCompleted.value) {
    showToast('Файлы можно прикреплять только к завершенным задачам', 'warning')
    return
  }
  fileInput.value?.click()
}

const handleFileSelect = async (event) => {
  const files = Array.from(event.target.files)
  if (files.length === 0) return
  
  if (!isTaskCompleted.value) {
    showToast('Файлы можно прикреплять только к завершенным задачам', 'warning')
    return
  }
  
  await uploadFiles(files)
  event.target.value = ''
}

const handleFileDrop = async (event) => {
  event.preventDefault()
  const files = Array.from(event.dataTransfer.files)
  if (files.length === 0) return
  
  if (!isTaskCompleted.value) {
    showToast('Файлы можно прикреплять только к завершенным задачам', 'warning')
    return
  }
  
  await uploadFiles(files)
}

const uploadFiles = async (files) => {
  if (!selectedTask.value) return
  
  uploading.value = true
  
  try {
    for (const file of files) {
      if (file.size > 50 * 1024 * 1024) {
        showToast(`Файл "${file.name}" слишком большой (макс. 50MB)`, 'error')
        continue
      }
      
      const fileExt = file.name.split('.').pop()
      const fileName = `${Date.now()}-${Math.random().toString(36).substring(2)}.${fileExt}`
      
      const filePath = `/filesusers/${fileName}`
      
      try {
        const { data: attachmentData, error: attachmentError } = await supabase
          .from('attachments')
          .insert({
            task_id: selectedTask.value.id,
            filename: file.name,
            file_path: filePath,
            file_size: file.size,
            uploaded_by_id: currentUser.value.id,
            uploaded_at: new Date().toISOString()
          })
          .select()
          .single()
        
        if (attachmentError) {
          console.error('Ошибка сохранения информации о файле:', attachmentError)
          showToast(`Ошибка сохранения файла "${file.name}": ${attachmentError.message}`, 'error')
          continue
        }
        
        if (!selectedTask.value.attachments) {
          selectedTask.value.attachments = []
        }
        selectedTask.value.attachments.push(attachmentData)
        
        const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
        if (taskIndex !== -1) {
          if (!tasks.value[taskIndex].attachments) {
            tasks.value[taskIndex].attachments = []
          }
          tasks.value[taskIndex].attachments.push(attachmentData)
        }
        
        showToast(`Информация о файле "${file.name}" успешно сохранена`, 'success')
        
      } catch (fileError) {
        console.error('Ошибка сохранения файла:', fileError)
        showToast(`Ошибка при сохранении файла "${file.name}": ${fileError.message}`, 'error')
        continue
      }
    }
  } catch (error) {
    console.error('Общая ошибка при загрузке файлов:', error)
    showToast('Ошибка при загрузке файлов: ' + error.message, 'error')
  } finally {
    uploading.value = false
  }
}

const downloadAttachment = async (attachment) => {
  try {
    const message = `Файл "${attachment.filename}" был прикреплен к задаче, но не может быть скачан через веб-интерфейс.\n\nИнформация о файле:\n- Название: ${attachment.filename}\n- Размер: ${formatFileSize(attachment.file_size)}\n- Путь: ${attachment.file_path}\n\nДля работы с файлами используйте локальное приложение.`
    
    const blob = new Blob([message], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `info-${attachment.filename}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    showToast('Информация о файле скачана', 'info')
  } catch (error) {
    console.error('Ошибка скачивания файла:', error)
    showToast('Ошибка при получении информации о файле', 'error')
  }
}

const deleteAttachment = async (attachmentId) => {
  try {
    const attachment = selectedTask.value.attachments.find(a => a.id === attachmentId)
    if (!attachment) return
    
    const { error: dbError } = await supabase
      .from('attachments')
      .delete()
      .eq('id', attachmentId)
    
    if (dbError) {
      throw dbError
    }
    
    selectedTask.value.attachments = selectedTask.value.attachments.filter(a => a.id !== attachmentId)
    
    const taskIndex = tasks.value.findIndex(t => t.id === selectedTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].attachments = tasks.value[taskIndex].attachments.filter(a => a.id !== attachmentId)
    }
    
    showToast('Информация о файле удалена', 'success')
  } catch (error) {
    console.error('Ошибка удаления файла:', error)
    showToast('Ошибка при удалении информации о файле', 'error')
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

watch(columns, () => {
  if (columns.value.length > 0) {
    loadTasks()
  }
})

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.container {
  min-height: 100vh;
}

.main {
  position: relative;
  min-height: calc(100vh - 60px);
}

.page-content {
  padding: 20px;
}

.board-header {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.board-loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.kanban-wrap {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding: 10px 0;
}

.kanban-column {
  min-width: 300px;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.kanban-col-title {
  font-weight: 600;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e6d1a4;
  color: #e6d1a4;
}

.kanban-items {
  min-height: 100px;
}

.kanban-item {
  background: #f8f9fa;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.kanban-item:hover {
  border-color: #B54B11;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(181, 75, 17, 0.1);
}

.item-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: #e6d1a4;
}

.item-desc {
  font-size: 14px;
  color: #ffffff;
  margin-bottom: 8px;
  line-height: 1.4;
}

.item-attachments {
  margin-bottom: 8px;
}

.attachments-count {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
}

.item-due-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  font-weight: 500;
}

.due-date-icon {
  font-size: 11px;
}

.due-date-normal {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.due-date-soon {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

.due-date-today {
  background: #fed7aa;
  color: #c2410c;
  border: 1px solid #fdba74;
  font-weight: 600;
}

.due-date-overdue {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
  font-weight: 600;
}

.item-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.priority-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.priority-low {
  background: #d1fae5;
  color: #065f46;
}

.priority-medium {
  background: #fef3c7;
  color: #92400e;
}

.priority-high {
  background: #fee2e2;
  color: #991b1b;
}

.priority-critical {
  background: #fecaca;
  color: #7f1d1d;
  font-weight: bold;
}

.member-count {
  font-size: 12px;
  color: #B54B11;
  background: #fef3c7;
  padding: 2px 6px;
  border-radius: 4px;
}

.kanban-empty {
  text-align: center;
  color: #9ca3af;
  font-style: italic;
  padding: 20px;
}

.boards-create-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #B54B11;
  color: white;
  border: none;
  font-size: 30px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(181, 75, 17, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.boards-create-btn:hover {
  background: #9a3f0e;
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(181, 75, 17, 0.4);
}

.boards-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.boards-modal {
  background: white;
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.boards-modal-large {
  max-width: 600px;
}

.boards-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.boards-modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.boards-modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.boards-modal-body {
  padding: 24px;
}

.boards-modal-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.boards-modal-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.boards-modal-field {
  margin-bottom: 20px;
}

.boards-modal-field:last-child {
  margin-bottom: 0;
}

.boards-modal-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.boards-modal-input,
.boards-modal-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

.boards-modal-input:focus,
.boards-modal-textarea:focus {
  outline: none;
  border-color: #B54B11;
}

.boards-modal-input:disabled,
.boards-modal-textarea:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
  opacity: 0.7;
}

.boards-modal-textarea {
  min-height: 80px;
  resize: vertical;
  font-family: inherit;
}

.boards-modal-hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.boards-modal-hint .due-date-overdue {
  color: #dc2626;
  font-weight: 500;
}

.boards-modal-hint .due-date-today {
  color: #c2410c;
  font-weight: 500;
}

.boards-modal-hint .due-date-soon {
  color: #92400e;
  font-weight: 500;
}

.file-upload-section {
  margin-top: 10px;
}

.file-upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.file-upload-area:hover {
  border-color: #B54B11;
  background-color: #fef7f3;
}

.file-upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.file-upload-icon {
  font-size: 32px;
  color: #6b7280;
}

.file-upload-text {
  font-weight: 500;
  color: #374151;
}

.file-upload-hint {
  font-size: 12px;
  color: #6b7280;
}

.attachments-list {
  margin-top: 15px;
}

.attachments-title {
  font-weight: 500;
  margin-bottom: 10px;
  color: #374151;
  font-size: 14px;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 8px;
  background: #f9fafb;
}

.attachment-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.attachment-name {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.attachment-size {
  font-size: 12px;
  color: #6b7280;
}

.attachment-actions {
  display: flex;
  gap: 5px;
}

.attachment-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 14px;
  transition: background 0.2s ease;
}

.attachment-download:hover {
  background: #d1fae5;
}

.attachment-delete:hover {
  background: #fee2e2;
  color: #dc2626;
}

.boards-members-add {
  display: flex;
  gap: 10px;
}

.boards-add-member-btn {
  padding: 10px 15px;
  background: #B54B11;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  font-size: 14px;
  transition: background 0.2s ease;
}

.boards-add-member-btn:hover {
  background: #9a3f0e;
}

.boards-members-list {
  margin-top: 15px;
}

.boards-members-title {
  font-weight: 500;
  margin-bottom: 10px;
  color: #374151;
  font-size: 14px;
}

.boards-member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.boards-member-item:last-child {
  border-bottom: none;
}

.boards-member-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.boards-member-email {
  color: #374151;
  font-size: 14px;
}

.boards-member-actions {
  display: flex;
  gap: 5px;
}

.boards-member-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 14px;
  transition: background 0.2s ease;
}

.boards-member-btn-remove:hover {
  background: #fee2e2;
  color: #dc2626;
}

.boards-modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
}

.boards-modal-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.boards-modal-btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.boards-modal-btn-cancel:hover {
  background: #e5e7eb;
}

.boards-modal-btn-create {
  background: #B54B11;
  color: white;
}

.boards-modal-btn-create:hover {
  background: #9a3f0e;
}

.boards-modal-btn-create:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.boards-modal-btn-danger {
  background: #ef4444;
  color: white;
}

.boards-modal-btn-danger:hover {
  background: #dc2626;
}

.boards-modal-btn-danger:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.task-created-date {
  padding: 8px 12px;
  background: #f3f4f6;
  color: #374151;
  border-radius: 6px;
  display: inline-block;
  font-weight: 500;
}

.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 6px;
  color: white;
  z-index: 3000;
  max-width: 300px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
}

.toast-success {
  background: #10b981;
}

.toast-error {
  background: #ef4444;
}

.toast-warning {
  background: #f59e0b;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .kanban-wrap {
    flex-direction: column;
  }
  
  .kanban-column {
    min-width: auto;
  }
  
  .boards-modal {
    width: 95%;
    margin: 20px;
  }
  
  .boards-members-add {
    flex-direction: column;
  }
  
  .boards-modal-actions {
    flex-direction: column;
  }
}
</style>