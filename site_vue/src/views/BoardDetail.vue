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
                :class="{ 
                  'task-completed': t.is_completed && t.approval_status === 'approved',
                  'task-pending': t.approval_status === 'pending',
                  'task-rejected': t.approval_status === 'rejected'
                }"
                @click="openTaskDetails(t)"
              >
                <div class="item-header">
                  <div class="item-title">{{ t.title }}</div>
                  <div class="task-status-controls">
                    <!-- Для исполнителя: кнопки смены статуса -->
                    <div v-if="!isAdmin && canChangeTaskStatus(t)" class="user-status-actions">
                      <button 
                        v-if="isPlannedColumn(t.column_id) && !t.is_completed"
                        class="status-btn move-to-work"
                        @click.stop="moveToWork(t)"
                        title="Перевести в работу"
                      >
                        ➡️ В работу
                      </button>
                      <button 
                        v-if="isWorkColumn(t.column_id) && !t.is_completed"
                        class="status-btn move-to-done"
                        @click.stop="moveToDone(t)"
                        title="Отметить как выполненную"
                      >
                        ✅ Готово
                      </button>
                    </div>
                    
                    <!-- Статус подтверждения -->
                    <div v-if="t.is_completed" class="approval-status">
                      <span v-if="t.approval_status === 'pending'" class="status-pending">
                        ⏳ На проверке
                      </span>
                      <span v-if="t.approval_status === 'approved'" class="status-approved">
                        ✅ Одобрено
                      </span>
                      <span v-if="t.approval_status === 'rejected'" class="status-rejected">
                        ❌ Требует доработки
                      </span>
                    </div>
                    
                    <!-- Для админа: кнопки подтверждения/отклонения -->
                    <div v-if="isAdmin && t.is_completed && t.approval_status === 'pending'" class="admin-actions">
                      <button 
                        class="admin-btn approve-btn"
                        @click.stop="approveTask(t)"
                        title="Подтвердить выполнение"
                      >
                        ✓
                      </button>
                      <button 
                        class="admin-btn reject-btn"
                        @click.stop="openRejectModal(t)"
                        title="Отклонить и указать доработки"
                      >
                        ✗
                      </button>
                    </div>
                  </div>
                </div>
                
                <div class="item-desc" v-if="t.description">{{ t.description }}</div>
                
                <!-- Комментарий админа при отклонении -->
                <div v-if="t.approval_comment && t.approval_status === 'rejected'" class="admin-comment">
                  <strong>Комментарий админа:</strong> {{ t.approval_comment }}
                </div>
                
                <div v-if="t.due_date" class="item-due-date" :class="getDueDateClass(t.due_date)">
                  <span class="due-date-icon">📅</span>
                  {{ formatDueDate(t.due_date) }}
                </div>
                
                <!-- Отображение вложений в карточке задачи -->
                <div v-if="t.attachments && t.attachments.length > 0" class="item-attachments">
                  <div class="attachments-count">
                    📎 {{ t.attachments.length }} файл(ов)
                  </div>
                </div>
                
                <div class="item-meta">
                  <span v-if="t.priority" :class="['priority-badge', `priority-${t.priority}`]">
                    {{ getPriorityText(t.priority) }}
                  </span>
                  <span v-if="t.assignee_email" class="assignee-badge">
                    👤 {{ t.assignee_email }}
                  </span>
                  <span v-if="isAdmin" class="edit-badge" @click.stop="openEditModal(t)">
                    ✏️ Редактировать
                  </span>
                </div>
              </div>
              <div v-if="(tasksByColumn[col.id] || []).length === 0" class="kanban-empty">Нет задач</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Кнопка создания задачи (только для админа) -->
      <button v-if="isAdmin" class="boards-create-btn" @click="openCreateModal" aria-label="Создать задачу">+</button>
    </div>

    <!-- Модальное окно создания задачи (только для админа) -->
    <div v-if="showCreateModal && isAdmin" class="boards-modal-overlay" @click="closeCreateModal">
      <div class="boards-modal boards-modal-large" @click.stop>
        <div class="boards-modal-header">
          <h2 class="boards-modal-title">Создание задачи</h2>
          <button class="boards-modal-close" @click="closeCreateModal">×</button>
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
              <label class="boards-modal-label">Колонка *</label>
              <select v-model="newTask.column_id" class="boards-modal-input">
                <option v-for="col in columns" :key="col.id" :value="col.id">
                  {{ col.title }}
                </option>
              </select>
            </div>

            <div class="boards-modal-field" v-if="isTeamProject">
              <label class="boards-modal-label">Исполнитель задачи *</label>
              <select v-model="newTask.assignee_email" class="boards-modal-input" required>
                <option value="">Выберите исполнителя</option>
                <option v-for="user in boardMembers" :key="user.id" :value="user.email">
                  {{ user.email }}
                </option>
              </select>
            </div>

            <div class="boards-modal-field" v-else>
              <label class="boards-modal-label">Исполнитель задачи</label>
              <div class="fixed-assignee">
                {{ currentUser?.email }} (Вы)
              </div>
              <input type="hidden" v-model="newTask.assignee_email" />
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
            </div>
          </div>
        </div>
        
        <div class="boards-modal-actions">
          <button class="boards-modal-btn boards-modal-btn-cancel" @click="closeCreateModal">
            Отменить
          </button>
          <button 
            class="boards-modal-btn boards-modal-btn-create" 
            @click="createTask"
            :disabled="!newTask.title.trim() || !newTask.column_id || creating || (isTeamProject && !newTask.assignee_email)"
          >
            {{ creating ? 'Создание...' : 'Создать задачу' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования задачи (только для админа) -->
    <div v-if="showEditModal && isAdmin" class="boards-modal-overlay" @click="closeEditModal">
      <div class="boards-modal boards-modal-large" @click.stop>
        <div class="boards-modal-header">
          <h2 class="boards-modal-title">Редактирование задачи</h2>
          <button class="boards-modal-close" @click="closeEditModal">×</button>
        </div>
        
        <div class="boards-modal-body">
          <div class="boards-modal-section">
            <div class="boards-modal-field">
              <label class="boards-modal-label">Название задачи *</label>
              <input 
                v-model="editingTask.title" 
                class="boards-modal-input" 
                placeholder="Введите название задачи"
              />
            </div>
            
            <div class="boards-modal-field">
              <label class="boards-modal-label">Описание</label>
              <textarea 
                v-model="editingTask.description" 
                class="boards-modal-textarea" 
                placeholder="Описание задачи"
              ></textarea>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Колонка *</label>
              <select v-model="editingTask.column_id" class="boards-modal-input">
                <option v-for="col in columns" :key="col.id" :value="col.id">
                  {{ col.title }}
                </option>
              </select>
            </div>

            <div class="boards-modal-field" v-if="isTeamProject">
              <label class="boards-modal-label">Исполнитель задачи *</label>
              <select v-model="editingTask.assignee_email" class="boards-modal-input" required>
                <option value="">Выберите исполнителя</option>
                <option v-for="user in boardMembers" :key="user.id" :value="user.email">
                  {{ user.email }}
                </option>
              </select>
            </div>

            <div class="boards-modal-field" v-else>
              <label class="boards-modal-label">Исполнитель задачи</label>
              <div class="fixed-assignee">
                {{ currentUser?.email }} (Вы)
              </div>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Приоритет</label>
              <select v-model="editingTask.priority" class="boards-modal-input">
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
                v-model="editingTask.due_date" 
                class="boards-modal-input" 
              />
            </div>
          </div>
        </div>
        
        <div class="boards-modal-actions">
          <button 
            class="boards-modal-btn boards-modal-btn-danger" 
            @click="deleteTask"
            :disabled="deleting"
          >
            {{ deleting ? 'Удаление...' : 'Удалить задачу' }}
          </button>
          <button class="boards-modal-btn boards-modal-btn-cancel" @click="closeEditModal">
            Отменить
          </button>
          <button 
            class="boards-modal-btn boards-modal-btn-create" 
            @click="updateTask"
            :disabled="!editingTask.title.trim() || !editingTask.column_id || updating"
          >
            {{ updating ? 'Сохранение...' : 'Сохранить изменения' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно отклонения задачи (для админа) -->
    <div v-if="showRejectModal" class="boards-modal-overlay" @click="closeRejectModal">
      <div class="boards-modal" @click.stop>
        <div class="boards-modal-header">
          <h2 class="boards-modal-title">Отклонение задачи</h2>
          <button class="boards-modal-close" @click="closeRejectModal">×</button>
        </div>
        
        <div class="boards-modal-body">
          <div class="boards-modal-field">
            <label class="boards-modal-label">Что нужно доделать?</label>
            <textarea 
              v-model="rejectionComment" 
              class="boards-modal-textarea" 
              placeholder="Опишите, что требуется доработать..."
              rows="4"
            ></textarea>
          </div>
        </div>
        
        <div class="boards-modal-actions">
          <button class="boards-modal-btn boards-modal-btn-cancel" @click="closeRejectModal">
            Отмена
          </button>
          <button 
            class="boards-modal-btn boards-modal-btn-danger" 
            @click="rejectTask"
            :disabled="!rejectionComment.trim() || rejecting"
          >
            {{ rejecting ? 'Отклонение...' : 'Отклонить' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно деталей задачи (для исполнителя и админа) -->
    <div v-if="showTaskDetailsModal" class="boards-modal-overlay" @click="closeTaskDetailsModal">
      <div class="boards-modal boards-modal-large" @click.stop>
        <div class="boards-modal-header">
          <h2 class="boards-modal-title">Детали задачи</h2>
          <button class="boards-modal-close" @click="closeTaskDetailsModal">×</button>
        </div>
        
        <div class="boards-modal-body">
          <div class="boards-modal-section">
            <div class="boards-modal-field">
              <label class="boards-modal-label">Название задачи</label>
              <div class="task-detail-value">{{ selectedTask?.title }}</div>
            </div>
            
            <div class="boards-modal-field">
              <label class="boards-modal-label">Описание</label>
              <div class="task-detail-value">{{ selectedTask?.description || 'Нет описания' }}</div>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Статус</label>
              <div class="task-detail-value">{{ getColumnTitle(selectedTask?.column_id) }}</div>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Приоритет</label>
              <div class="task-detail-value">{{ getPriorityText(selectedTask?.priority) }}</div>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Срок выполнения</label>
              <div class="task-detail-value" v-if="selectedTask?.due_date">
                {{ formatDueDate(selectedTask.due_date) }}
                <span :class="getDueDateClass(selectedTask.due_date)">
                  ({{ getDueDateText(selectedTask.due_date) }})
                </span>
              </div>
              <div class="task-detail-value" v-else>Не установлен</div>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Исполнитель</label>
              <div class="task-detail-value">{{ selectedTask?.assignee_email || 'Не назначен' }}</div>
            </div>

            <!-- Статус подтверждения -->
            <div v-if="selectedTask?.is_completed" class="boards-modal-field">
              <label class="boards-modal-label">Статус проверки</label>
              <div class="task-detail-value">
                <span v-if="selectedTask.approval_status === 'pending'" class="status-pending">
                  ⏳ На проверке у администратора
                </span>
                <span v-if="selectedTask.approval_status === 'approved'" class="status-approved">
                  ✅ Задача подтверждена
                </span>
                <span v-if="selectedTask.approval_status === 'rejected'" class="status-rejected">
                  ❌ Требует доработки
                </span>
              </div>
            </div>

            <!-- Комментарий админа при отклонении -->
            <div v-if="selectedTask?.approval_comment && selectedTask.approval_status === 'rejected'" class="boards-modal-field">
              <label class="boards-modal-label">Комментарий администратора</label>
              <div class="task-detail-value admin-comment-text">
                {{ selectedTask.approval_comment }}
              </div>
            </div>
          </div>

          <!-- Секция прикрепленных файлов (только для завершенных задач) -->
          <div v-if="isTaskCompleted" class="boards-modal-section">
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
                      Максимальный размер: 50MB
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
                        title="Скачать файл"
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

          <!-- Кнопки действий для исполнителя -->
          <div v-if="!isAdmin && canChangeTaskStatus(selectedTask)" class="boards-modal-section">
            <div class="boards-modal-field">
              <label class="boards-modal-label">Действия</label>
              <div class="task-actions">
                <button 
                  v-if="isPlannedColumn(selectedTask.column_id) && !selectedTask.is_completed"
                  class="status-btn move-to-work large"
                  @click="moveToWork(selectedTask)"
                >
                  ➡️ Перевести в работу
                </button>
                <button 
                  v-if="isWorkColumn(selectedTask.column_id) && !selectedTask.is_completed"
                  class="status-btn move-to-done large"
                  @click="moveToDone(selectedTask)"
                >
                  ✅ Отметить как выполненную
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="boards-modal-actions">
          <button class="boards-modal-btn boards-modal-btn-cancel" @click="closeTaskDetailsModal">
            Закрыть
          </button>
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
import { auth } from '../js/auth.js'
import demoDataRaw from '../assets/demo_data.json'

const route = useRoute()
const boardId = ref(route.params.id)
const board = ref(null)
const columns = ref([])
const tasks = ref([])
const boardMembers = ref([])
const loading = ref(true)
const currentUser = ref(null)
const isAdmin = ref(false)
const demoData = ref(null)

function loadDemoData() {
  const persisted = (() => { try { return JSON.parse(localStorage.getItem('demo_data') || 'null') } catch { return null } })()
  demoData.value = persisted || demoDataRaw
}

function saveDemoData() {
  try { localStorage.setItem('demo_data', JSON.stringify(demoData.value)) } catch {}
}

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showRejectModal = ref(false)
const showTaskDetailsModal = ref(false)
const creating = ref(false)
const updating = ref(false)
const deleting = ref(false)
const rejecting = ref(false)
const uploading = ref(false)

const newTask = ref({
  title: '',
  description: '',
  column_id: null,
  assignee_email: '',
  priority: 'medium',
  due_date: null
})

const editingTask = ref({
  id: null,
  title: '',
  description: '',
  column_id: null,
  assignee_email: '',
  priority: 'medium',
  due_date: null
})

const selectedTask = ref(null)
const taskToReject = ref(null)
const rejectionComment = ref('')

const fileInput = ref(null)

const tasksByColumn = computed(() => {
  const grouped = {}
  columns.value.forEach(col => {
    grouped[col.id] = tasks.value.filter(task => task.column_id === col.id)
  })
  return grouped
})

const isTeamProject = computed(() => {
  return boardMembers.value.length > 1
})

const isTaskCompleted = computed(() => {
  if (!selectedTask.value) return false
  const doneColumn = columns.value.find(col => col.title.toLowerCase().includes('готов'))
  return doneColumn && selectedTask.value.column_id === doneColumn.id
})

const plannedColumn = computed(() => {
  return columns.value.find(col => 
    col.title.toLowerCase().includes('план') || 
    col.title.toLowerCase().includes('plan') ||
    col.title.toLowerCase().includes('todo')
  )
})

const workColumn = computed(() => {
  return columns.value.find(col => 
    col.title.toLowerCase().includes('работ') || 
    col.title.toLowerCase().includes('work') ||
    col.title.toLowerCase().includes('progress') ||
    col.title.toLowerCase().includes('в работе')
  )
})

const doneColumn = computed(() => {
  return columns.value.find(col => 
    col.title.toLowerCase().includes('готов') || 
    col.title.toLowerCase().includes('done') ||
    col.title.toLowerCase().includes('complete')
  )
})

const isPlannedColumn = (columnId) => {
  return plannedColumn.value?.id === columnId
}

const isWorkColumn = (columnId) => {
  return workColumn.value?.id === columnId
}

const isDoneColumn = (columnId) => {
  return doneColumn.value?.id === columnId
}

const getCurrentUser = async () => {
  try {
    if (auth.isDemo.value) {
      const demoId = auth.userId.value || 'demo-user-id'
      currentUser.value = { id: demoId, email: 'demo@example.com' }
      isAdmin.value = true
      return
    }
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
      
      await checkAdminStatus()
    }
  } catch (error) {
    console.error('Ошибка получения пользователя:', error)
  }
}

const checkAdminStatus = async () => {
  if (auth.isDemo.value) { isAdmin.value = true; return }
  try {
    const { data: userRoles, error } = await supabase
      .from('user_roles')
      .select(`
        role_id,
        roles:role_id (name_role)
      `)
      .eq('board_id', boardId.value)
      .eq('user_id', currentUser.value.id)
      .single()

    if (error) {
      console.log('Пользователь не является админом этого проекта')
      isAdmin.value = false
      return
    }

    isAdmin.value = userRoles.roles?.name_role === 'admin'
  } catch (error) {
    console.error('Ошибка проверки прав админа:', error)
    isAdmin.value = false
  }
}

const loadBoardMembers = async () => {
  try {
    if (auth.isDemo.value) {
      loadDemoData()
      const boardDemo = (demoData.value.projects || []).find(b => b.id === boardId.value)
      boardMembers.value = boardDemo?.members?.map(m => ({ id: m.id, email: m.email })) || []
      return
    }
    const { data, error } = await supabase
      .from('user_roles')
      .select(`
        user_id,
        users:user_id (email, id)
      `)
      .eq('board_id', boardId.value)

    if (error) throw error
    
    boardMembers.value = data?.map(item => ({
      id: item.user_id,
      email: item.users?.email
    })) || []
    
  } catch (error) {
    console.error('Ошибка загрузки участников проекта:', error)
    boardMembers.value = []
  }
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

const getPriorityText = (priority) => {
  const priorities = {
    low: 'Низкий',
    medium: 'Средний', 
    high: 'Высокий',
    critical: 'Критический'
  }
  return priorities[priority] || priority
}

const getColumnTitle = (columnId) => {
  const column = columns.value.find(col => col.id === columnId)
  return column ? column.title : 'Неизвестно'
}

const canChangeTaskStatus = (task) => {
  if (!currentUser.value || !task) return false
  return task.assignee_id === currentUser.value.id
}

const moveToWork = async (task) => {
  if (!canChangeTaskStatus(task)) {
    showToast('Только исполнитель задачи может менять статус', 'warning')
    return
  }

  if (!isPlannedColumn(task.column_id)) {
    showToast('Задача должна быть в колонке "В планах"', 'error')
    return
  }

  if (!workColumn.value) {
    showToast('Колонка "В работе" не найдена', 'error')
    return
  }

  try {
    if (auth.isDemo.value) {
      const taskIndex = tasks.value.findIndex(t => t.id === task.id)
      if (taskIndex !== -1) {
        tasks.value[taskIndex].column_id = workColumn.value.id
      }
      if (selectedTask.value && selectedTask.value.id === task.id) {
        selectedTask.value.column_id = workColumn.value.id
      }
      showToast('Задача перемещена в работу (демо)', 'success')
      return
    }
    const { error } = await supabase
      .from('tasks')
      .update({ 
        column_id: workColumn.value.id,
        updated_at: new Date().toISOString()
      })
      .eq('id', task.id)

    if (error) throw error

    const taskIndex = tasks.value.findIndex(t => t.id === task.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].column_id = workColumn.value.id
    }

    if (selectedTask.value && selectedTask.value.id === task.id) {
      selectedTask.value.column_id = workColumn.value.id
    }

    showToast('Задача перемещена в работу', 'success')
  } catch (error) {
    console.error('Ошибка перемещения задачи в работу:', error)
    showToast('Ошибка при перемещении задачи', 'error')
  }
}

const moveToDone = async (task) => {
  if (!canChangeTaskStatus(task)) {
    showToast('Только исполнитель задачи может менять статус', 'warning')
    return
  }

  if (!isWorkColumn(task.column_id)) {
    showToast('Задача должна быть в колонке "В работе"', 'error')
    return
  }

  if (!doneColumn.value) {
    showToast('Колонка "Готово" не найдена', 'error')
    return
  }

  try {
    const updateData = { 
      is_completed: true,
      column_id: doneColumn.value.id,
      approval_status: 'pending',
      updated_at: new Date().toISOString()
    }

    if (auth.isDemo.value) {
      const taskIndex = tasks.value.findIndex(t => t.id === task.id)
      if (taskIndex !== -1) {
        tasks.value[taskIndex].is_completed = true
        tasks.value[taskIndex].column_id = doneColumn.value.id
        tasks.value[taskIndex].approval_status = 'pending'
      }
      if (selectedTask.value && selectedTask.value.id === task.id) {
        selectedTask.value.is_completed = true
        selectedTask.value.column_id = doneColumn.value.id
        selectedTask.value.approval_status = 'pending'
      }
      showToast('Задача отправлена на проверку администратору (демо)', 'success')
      return
    }

    const { error } = await supabase
      .from('tasks')
      .update(updateData)
      .eq('id', task.id)

    if (error) throw error

    const taskIndex = tasks.value.findIndex(t => t.id === task.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].is_completed = true
      tasks.value[taskIndex].column_id = doneColumn.value.id
      tasks.value[taskIndex].approval_status = 'pending'
    }

    if (selectedTask.value && selectedTask.value.id === task.id) {
      selectedTask.value.is_completed = true
      selectedTask.value.column_id = doneColumn.value.id
      selectedTask.value.approval_status = 'pending'
    }

    showToast('Задача отправлена на проверку администратору', 'success')
  } catch (error) {
    console.error('Ошибка отметки задачи как выполненной:', error)
    showToast('Ошибка при изменении статуса задачи', 'error')
  }
}

const approveTask = async (task) => {
  if (!isAdmin.value) {
    showToast('Только администратор может подтверждать задачи', 'error')
    return
  }

  try {
    if (auth.isDemo.value) {
      const taskIndex = tasks.value.findIndex(t => t.id === task.id)
      if (taskIndex !== -1) {
        tasks.value[taskIndex].approval_status = 'approved'
        tasks.value[taskIndex].approval_comment = null
      }
      if (selectedTask.value && selectedTask.value.id === task.id) {
        selectedTask.value.approval_status = 'approved'
        selectedTask.value.approval_comment = null
      }
      showToast('Задача подтверждена! (демо)', 'success')
      return
    }
    const { error } = await supabase
      .from('tasks')
      .update({ 
        approval_status: 'approved',
        approval_comment: null,
        updated_at: new Date().toISOString()
      })
      .eq('id', task.id)

    if (error) throw error

    const taskIndex = tasks.value.findIndex(t => t.id === task.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].approval_status = 'approved'
      tasks.value[taskIndex].approval_comment = null
    }

    if (selectedTask.value && selectedTask.value.id === task.id) {
      selectedTask.value.approval_status = 'approved'
      selectedTask.value.approval_comment = null
    }

    showToast('Задача подтверждена!', 'success')
  } catch (error) {
    console.error('Ошибка подтверждения задачи:', error)
    showToast('Ошибка при подтверждении задачи', 'error')
  }
}

const openRejectModal = (task) => {
  if (!isAdmin.value) return
  taskToReject.value = task
  rejectionComment.value = ''
  showRejectModal.value = true
}

const closeRejectModal = () => {
  showRejectModal.value = false
  taskToReject.value = null
  rejectionComment.value = ''
}

const rejectTask = async () => {
  if (!isAdmin.value || !taskToReject.value) {
    showToast('Ошибка: нет прав или задача не выбрана', 'error')
    return
  }

  rejecting.value = true
  try {
    console.log('Отклонение задачи:', taskToReject.value.id)
    
    let targetColumnId = workColumn.value?.id
    
    if (!targetColumnId) {
      const availableColumn = columns.value.find(col => 
        col.id !== doneColumn.value?.id
      )
      if (availableColumn) {
        targetColumnId = availableColumn.id
      } else {
        targetColumnId = taskToReject.value.column_id
      }
    }

    const updateData = { 
      is_completed: false,
      column_id: targetColumnId,
      approval_status: 'rejected',
      approval_comment: rejectionComment.value,
      updated_at: new Date().toISOString()
    }

    console.log('Данные для обновления:', updateData)
    if (auth.isDemo.value) {
      const taskIndex = tasks.value.findIndex(t => t.id === taskToReject.value.id)
      if (taskIndex !== -1) {
        tasks.value[taskIndex].is_completed = false
        tasks.value[taskIndex].column_id = targetColumnId
        tasks.value[taskIndex].approval_status = 'rejected'
        tasks.value[taskIndex].approval_comment = rejectionComment.value
      }
      if (selectedTask.value && selectedTask.value.id === taskToReject.value.id) {
        selectedTask.value.is_completed = false
        selectedTask.value.column_id = targetColumnId
        selectedTask.value.approval_status = 'rejected'
        selectedTask.value.approval_comment = rejectionComment.value
      }
      showToast('Задача возвращена на доработку (демо)', 'success')
      closeRejectModal()
      return
    }

    const { error } = await supabase
      .from('tasks')
      .update(updateData)
      .eq('id', taskToReject.value.id)

    if (error) {
      console.error('Ошибка Supabase:', error)
      throw error
    }

    const taskIndex = tasks.value.findIndex(t => t.id === taskToReject.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].is_completed = false
      tasks.value[taskIndex].column_id = targetColumnId
      tasks.value[taskIndex].approval_status = 'rejected'
      tasks.value[taskIndex].approval_comment = rejectionComment.value
    }

    if (selectedTask.value && selectedTask.value.id === taskToReject.value.id) {
      selectedTask.value.is_completed = false
      selectedTask.value.column_id = targetColumnId
      selectedTask.value.approval_status = 'rejected'
      selectedTask.value.approval_comment = rejectionComment.value
    }

    showToast('Задача возвращена на доработку', 'success')
    closeRejectModal()
  } catch (error) {
    console.error('Ошибка отклонения задачи:', error)
    showToast('Ошибка при отклонении задачи: ' + error.message, 'error')
  } finally {
    rejecting.value = false
  }
}

const openCreateModal = () => {
  if (!isAdmin.value) {
    showToast('Только администратор может создавать задачи', 'error')
    return
  }
  showCreateModal.value = true
  if (columns.value.length > 0 && !newTask.value.column_id) {
    newTask.value.column_id = columns.value[0].id
  }
  
  if (!isTeamProject.value && currentUser.value) {
    newTask.value.assignee_email = currentUser.value.email
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  newTask.value = {
    title: '',
    description: '',
    column_id: columns.value.length > 0 ? columns.value[0].id : null,
    assignee_email: '',
    priority: 'medium',
    due_date: null
  }
}

const openEditModal = (task) => {
  if (!isAdmin.value) {
    showToast('Только администратор может редактировать задачи', 'error')
    return
  }
  
  editingTask.value = {
    id: task.id,
    title: task.title,
    description: task.description || '',
    column_id: task.column_id,
    assignee_email: task.assignee_email,
    priority: task.priority || 'medium',
    due_date: task.due_date ? task.due_date.split('T')[0] : null
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingTask.value = {
    id: null,
    title: '',
    description: '',
    column_id: null,
    assignee_email: '',
    priority: 'medium',
    due_date: null
  }
}

const openTaskDetails = async (task) => {
  selectedTask.value = { ...task }
  await loadTaskAttachments(task.id)
  showTaskDetailsModal.value = true
}

const closeTaskDetailsModal = () => {
  showTaskDetailsModal.value = false
  selectedTask.value = null
}

const createTask = async () => {
  if (!isAdmin.value) {
    showToast('Только администратор может создавать задачи', 'error')
    return
  }

  if (!newTask.value.title.trim() || !newTask.value.column_id) return
  
  creating.value = true
  try {
    if (!currentUser.value) {
      throw new Error('Пользователь не авторизован')
    }

    let assigneeId = currentUser.value.id
    let assigneeEmail = currentUser.value.email

    if (isTeamProject.value) {
      if (!newTask.value.assignee_email) {
        throw new Error('Не выбран исполнитель задачи')
      }

      const assigneeUser = boardMembers.value.find(user => user.email === newTask.value.assignee_email)
      if (!assigneeUser) {
        throw new Error('Выбранный исполнитель не найден в проекте')
      }
      assigneeId = assigneeUser.id
      assigneeEmail = assigneeUser.email
    }

    if (auth.isDemo.value) {
      loadDemoData()
      const now = new Date().toISOString()
      const newId = 'demo-task-' + Date.now() + '-' + Math.random().toString(36).slice(2,6)
      const taskData = {
        id: newId,
        title: newTask.value.title,
        description: newTask.value.description || null,
        column_id: newTask.value.column_id,
        position: tasks.value.length,
        creator_id: currentUser.value.id,
        assignee_id: assigneeId,
        priority: newTask.value.priority || 'medium',
        due_date: newTask.value.due_date || null,
        is_completed: false,
        approval_status: 'pending',
        created_at: now
      }
      demoData.value.tasks = [ ...(demoData.value.tasks || []), taskData ]
      try { localStorage.setItem('demo_data', JSON.stringify(demoData.value)) } catch {}
      const updatedTask = {
        ...taskData,
        assignee_email: assigneeEmail,
        creator_email: currentUser.value.email
      }
      tasks.value.push(updatedTask)
      closeCreateModal()
      showToast('Задача успешно создана (демо)', 'success')
      return
    }

    const taskData = {
      title: newTask.value.title,
      description: newTask.value.description || null,
      column_id: newTask.value.column_id,
      position: tasks.value.length,
      creator_id: currentUser.value.id,
      assignee_id: assigneeId,
      priority: newTask.value.priority || 'medium',
      due_date: newTask.value.due_date || null,
      is_completed: false,
      approval_status: 'pending',
      created_at: new Date().toISOString()
    }

    const { data: taskDataResult, error: taskError } = await supabase
      .from('tasks')
      .insert(taskData)
      .select(`
        *,
        assignee:assignee_id (email),
        creator:creator_id (email)
      `)
      .single()

    if (taskError) {
      throw taskError
    }

    const updatedTask = {
      ...taskDataResult,
      assignee_email: assigneeEmail,
      creator_email: taskDataResult.creator?.email
    }

    tasks.value.push(updatedTask)
    
    closeCreateModal()
    showToast('Задача успешно создана', 'success')
    
  } catch (error) {
    let errorMessage = 'Ошибка при создании задачи'
    if (error.message.includes('Только администратор')) {
      errorMessage = error.message
    } else if (error.message.includes('Не выбран исполнитель')) {
      errorMessage = 'Выберите исполнителя задачи'
    }
    
    showToast(errorMessage, 'error')
  } finally {
    creating.value = false
  }
}

const updateTask = async () => {
  if (!isAdmin.value) {
    showToast('Только администратор может редактировать задачи', 'error')
    return
  }

  if (!editingTask.value.title.trim() || !editingTask.value.column_id) return
  
  updating.value = true
  try {
    let assigneeId = currentUser.value.id
    let assigneeEmail = currentUser.value.email

    if (isTeamProject.value) {
      if (!editingTask.value.assignee_email) {
        throw new Error('Не выбран исполнитель задачи')
      }

      const assigneeUser = boardMembers.value.find(user => user.email === editingTask.value.assignee_email)
      if (!assigneeUser) {
        throw new Error('Выбранный исполнитель не найден в проекте')
      }
      assigneeId = assigneeUser.id
      assigneeEmail = assigneeUser.email
    }

    if (auth.isDemo.value) {
      loadDemoData()
      const idx = (demoData.value.tasks || []).findIndex(t => t.id === editingTask.value.id)
      if (idx !== -1) {
        demoData.value.tasks[idx] = {
          ...demoData.value.tasks[idx],
          title: editingTask.value.title,
          description: editingTask.value.description || null,
          column_id: editingTask.value.column_id,
          assignee_id: assigneeId,
          priority: editingTask.value.priority || 'medium',
          due_date: editingTask.value.due_date || null,
          updated_at: new Date().toISOString()
        }
        try { localStorage.setItem('demo_data', JSON.stringify(demoData.value)) } catch {}
      }
      const taskIndexLocal = tasks.value.findIndex(t => t.id === editingTask.value.id)
      if (taskIndexLocal !== -1) {
        tasks.value[taskIndexLocal].title = editingTask.value.title
        tasks.value[taskIndexLocal].description = editingTask.value.description
        tasks.value[taskIndexLocal].column_id = editingTask.value.column_id
        tasks.value[taskIndexLocal].assignee_id = assigneeId
        tasks.value[taskIndexLocal].assignee_email = assigneeEmail
        tasks.value[taskIndexLocal].priority = editingTask.value.priority
        tasks.value[taskIndexLocal].due_date = editingTask.value.due_date
      }
      closeEditModal()
      showToast('Задача успешно обновлена (демо)', 'success')
      return
    }

    const { error } = await supabase
      .from('tasks')
      .update({
        title: editingTask.value.title,
        description: editingTask.value.description || null,
        column_id: editingTask.value.column_id,
        assignee_id: assigneeId,
        priority: editingTask.value.priority || 'medium',
        due_date: editingTask.value.due_date || null,
        updated_at: new Date().toISOString()
      })
      .eq('id', editingTask.value.id)

    if (error) throw error

    const taskIndex = tasks.value.findIndex(t => t.id === editingTask.value.id)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].title = editingTask.value.title
      tasks.value[taskIndex].description = editingTask.value.description
      tasks.value[taskIndex].column_id = editingTask.value.column_id
      tasks.value[taskIndex].assignee_id = assigneeId
      tasks.value[taskIndex].assignee_email = assigneeEmail
      tasks.value[taskIndex].priority = editingTask.value.priority
      tasks.value[taskIndex].due_date = editingTask.value.due_date
    }

    closeEditModal()
    showToast('Задача успешно обновлена', 'success')
    
  } catch (error) {
    let errorMessage = 'Ошибка при обновлении задачи'
    if (error.message.includes('Только администратор')) {
      errorMessage = error.message
    }
    
    showToast(errorMessage, 'error')
  } finally {
    updating.value = false
  }
}

const deleteTask = async () => {
  if (!isAdmin.value) {
    showToast('Только администратор может удалять задачи', 'error')
    return
  }

  if (!editingTask.value.id) return
  
  deleting.value = true
  try {
    if (auth.isDemo.value) {
      loadDemoData()
      const taskId = editingTask.value.id
      demoData.value.attachments = (demoData.value.attachments || []).filter(att => att.task_id !== taskId)
      demoData.value.tasks = (demoData.value.tasks || []).filter(t => t.id !== taskId)
      try { localStorage.setItem('demo_data', JSON.stringify(demoData.value)) } catch {}
      tasks.value = tasks.value.filter(t => t.id !== taskId)
      closeEditModal()
      showToast('Задача успешно удалена (демо)', 'success')
      return
    }
    const { data: attachments } = await supabase
      .from('attachments')
      .select('*')
      .eq('task_id', editingTask.value.id)

    if (attachments && attachments.length > 0) {
      const filePaths = attachments.map(att => att.file_path).filter(Boolean)
      if (filePaths.length > 0) {
        await supabase.storage
          .from('task-attachments')
          .remove(filePaths)
      }

      await supabase
        .from('attachments')
        .delete()
        .eq('task_id', editingTask.value.id)
    }

    const { error } = await supabase
      .from('tasks')
      .delete()
      .eq('id', editingTask.value.id)

    if (error) throw error

    tasks.value = tasks.value.filter(t => t.id !== editingTask.value.id)
    
    closeEditModal()
    showToast('Задача успешно удалена', 'success')
    
  } catch (error) {
    console.error('Ошибка удаления задачи:', error)
    showToast('Ошибка при удалении задачи', 'error')
  } finally {
    deleting.value = false
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const loadTaskAttachments = async (taskId) => {
  try {
    if (auth.isDemo.value) {
      return []
    }
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
    if (auth.isDemo.value) {
      return
    }
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
    if (auth.isDemo.value) {
      showToast('Загрузка файлов недоступна в демо-режиме', 'warning')
      return
    }
    for (const file of files) {
      if (file.size > 50 * 1024 * 1024) {
        showToast(`Файл "${file.name}" слишком большой (макс. 50MB)`, 'error')
        continue
      }
      
      const fileExt = file.name.split('.').pop()
      const fileName = `${Date.now()}-${Math.random().toString(36).substring(2)}.${fileExt}`
      const filePath = `${selectedTask.value.id}/${fileName}`
      
      try {
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from('task-attachments')
          .upload(filePath, file)
        
        if (uploadError) {
          console.error('Ошибка загрузки файла:', uploadError)
          showToast(`Ошибка загрузки файла "${file.name}": ${uploadError.message}`, 'error')
          continue
        }
        
        const { data: urlData } = supabase.storage
          .from('task-attachments')
          .getPublicUrl(filePath)
        
        const { data: attachmentData, error: attachmentError } = await supabase
          .from('attachments')
          .insert({
            task_id: selectedTask.value.id,
            filename: file.name,
            file_path: filePath,
            file_size: file.size,
            file_url: urlData.publicUrl,
            uploaded_by_id: currentUser.value.id,
            uploaded_at: new Date().toISOString()
          })
          .select()
          .single()
        
        if (attachmentError) {
          await supabase.storage
            .from('task-attachments')
            .remove([filePath])
          
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
        
        showToast(`Файл "${file.name}" успешно загружен`, 'success')
        
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
    if (auth.isDemo.value) {
      showToast('Скачивание файлов недоступно в демо-режиме', 'warning')
      return
    }
    if (attachment.file_url) {
      const a = document.createElement('a')
      a.href = attachment.file_url
      a.download = attachment.filename
      a.target = '_blank'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      showToast('Файл скачивается', 'success')
    } else {
      const { data, error } = await supabase.storage
        .from('task-attachments')
        .download(attachment.file_path)
      
      if (error) throw error
      
      const url = URL.createObjectURL(data)
      const a = document.createElement('a')
      a.href = url
      a.download = attachment.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      showToast('Файл скачивается', 'success')
    }
  } catch (error) {
    console.error('Ошибка скачивания файла:', error)
    
    const message = `Файл "${attachment.filename}" не может быть скачан через веб-интерфейс.\n\nИнформация о файле:\n- Название: ${attachment.filename}\n- Размер: ${formatFileSize(attachment.file_size)}\n- Путь: ${attachment.file_path}\n\nДля работы с файлами используйте локальное приложение.`
    
    const blob = new Blob([message], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `info-${attachment.filename}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    showToast('Скачана информация о файле', 'info')
  }
}

const deleteAttachment = async (attachmentId) => {
  try {
    if (auth.isDemo.value) {
      showToast('Удаление файлов недоступно в демо-режиме', 'warning')
      return
    }
    const attachment = selectedTask.value.attachments.find(a => a.id === attachmentId)
    if (!attachment) return
    
    if (attachment.file_path) {
      const { error: storageError } = await supabase.storage
        .from('task-attachments')
        .remove([attachment.file_path])
      
      if (storageError) {
        console.error('Ошибка удаления файла из storage:', storageError)
      }
    }
    
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
    
    showToast('Файл удален', 'success')
  } catch (error) {
    console.error('Ошибка удаления файла:', error)
    showToast('Ошибка при удалении файла', 'error')
  }
}

const showToast = (message, type = 'success') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

const loadBoard = async () => {
  try {
    if (auth.isDemo.value) {
      loadDemoData()
      board.value = (demoData.value.projects || []).find(b => b.id === boardId.value) || null
      return
    }
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
    if (auth.isDemo.value) {
      loadDemoData()
      const cols = (demoData.value.columns || []).filter(c => c.board_id === boardId.value)
      columns.value = cols
      if (columns.value.length > 0 && !newTask.value.column_id) {
        newTask.value.column_id = columns.value[0].id
      }
      return
    }
    const { data, error } = await supabase
      .from('columns')
      .select('*')
      .eq('board_id', boardId.value)
      .order('position', { ascending: true })
    
    if (error) throw error
    columns.value = data || []
    
    console.log('Загруженные колонки:', columns.value)
    
    if (columns.value.length > 0 && !newTask.value.column_id) {
      newTask.value.column_id = columns.value[0].id
    }
  } catch (error) {
    columns.value = []
  }
}

const loadTasks = async () => {
  try {
    if (auth.isDemo.value) {
      loadDemoData()
      if (columns.value.length > 0) {
        const columnIds = columns.value.map(col => col.id)
        const membersById = {}
        const boardDemo = (demoData.value.projects || []).find(b => b.id === boardId.value)
        ;(boardDemo?.members || []).forEach(m => { membersById[m.id] = m })
        const data = (demoData.value.tasks || []).filter(t => columnIds.includes(t.column_id))
        tasks.value = data.map(task => ({
          ...task,
          assignee_email: membersById[task.assignee_id]?.email || 'demo@example.com',
          creator_email: membersById[task.creator_id]?.email || 'demo@example.com',
          attachments: []
        }))
        return
      } else {
        tasks.value = []
        return
      }
    }
    if (columns.value.length > 0) {
      const columnIds = columns.value.map(col => col.id)
      
      const { data, error } = await supabase
        .from('tasks')
        .select(`
          *,
          assignee:assignee_id (email),
          creator:creator_id (email)
        `)
        .in('column_id', columnIds)
        .order('position', { ascending: true })
      
      if (error) throw error
      
      tasks.value = (data || []).map(task => ({
        ...task,
        assignee_email: task.assignee?.email,
        creator_email: task.creator?.email
      }))

      console.log('Загруженные задачи:', tasks.value)
      
      await loadTaskAttachmentsForAllTasks()
    } else {
      tasks.value = []
    }
  } catch (error) {
    tasks.value = []
  }
}

const loadData = async () => {
  loading.value = true
  try {
    await getCurrentUser()
    await loadBoardMembers()
    await loadBoard()
    await loadColumns()
    await loadTasks()
  } catch (error) {
    console.error('Error loading data:', error)
    showToast('Ошибка загрузки данных', 'error')
  } finally {
    loading.value = false
  }
}

const toast = ref({ visible: false, type: 'success', message: '' })

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
/* Все стили из предыдущего ответа остаются без изменений */
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
  color: #E6D1A4;
}

.board-loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #E6D1A4;
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

.kanban-item.task-completed {
  background: #f0f9ff;
  border-color: #bae6fd;
  opacity: 0.8;
}

.kanban-item.task-pending {
  background: #fff3cd;
  border-color: #ffeaa7;
}

.kanban-item.task-rejected {
  background: #f8d7da;
  border-color: #f5c6cb;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.item-title {
  font-weight: 500;
  color: #e6d1a4;
  flex: 1;
  margin-right: 10px;
}

.task-status-controls {
  flex-shrink: 0;
}

.user-status-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.move-to-work {
  background: #fef3c7;
  color: #92400e;
}

.move-to-work:hover {
  background: #fde68a;
}

.move-to-done {
  background: #d1fae5;
  color: #065f46;
}

.move-to-done:hover {
  background: #a7f3d0;
}

.approval-status {
  margin-top: 8px;
}

.status-pending {
  color: #f59e0b;
  font-size: 12px;
  font-weight: 500;
}

.status-approved {
  color: #10b981;
  font-size: 12px;
  font-weight: 500;
}

.status-rejected {
  color: #ef4444;
  font-size: 12px;
  font-weight: 500;
}

.admin-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.admin-btn {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.approve-btn {
  background: #10b981;
  color: white;
}

.approve-btn:hover {
  background: #059669;
}

.reject-btn {
  background: #ef4444;
  color: white;
}

.reject-btn:hover {
  background: #dc2626;
}

.item-desc {
  font-size: 14px;
  color: #ffffff;
  margin-bottom: 8px;
  line-height: 1.4;
}

.admin-comment {
  background: #f8d7da;
  color: #721c24;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 8px;
  border-left: 3px solid #f5c6cb;
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

.assignee-badge {
  font-size: 12px;
  color: #B54B11;
  background: #fef3c7;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.edit-badge {
  font-size: 12px;
  color: #B54B11;
  background: #fef3c7;
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.edit-badge:hover {
  background: #fde68a;
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

.fixed-assignee {
  padding: 10px 12px;
  background: #f3f4f6;
  border-radius: 6px;
  color: #6b7280;
  font-style: italic;
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

.task-creator-info {
  padding: 8px 12px;
  background: #f3f4f6;
  color: #374151;
  border-radius: 6px;
  display: inline-block;
  font-weight: 500;
}

.task-detail-value {
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  color: #495057;
}

.admin-comment-text {
  background: #fff3cd;
  border-color: #ffeaa7;
  color: #856404;
}

.task-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.status-btn.large {
  padding: 12px 20px;
  font-size: 14px;
  border-radius: 8px;
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
  
</style>