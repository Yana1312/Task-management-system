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
                <div v-if="getTaskMembers(t.id).length > 0" class="item-members">
                  <span class="member-count">{{ getTaskMembers(t.id).length }} участников</span>
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

            <!-- ИСПРАВЛЕНО: используем currentTaskMembers вместо taskMembers -->
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
          <h2 class="boards-modal-title">{{ selectedTask?.title }}</h2>
          <button class="boards-modal-close" @click="closeTaskModal">×</button>
        </div>
        
        <div class="boards-modal-body">
          <div class="boards-modal-section">
            <div class="boards-modal-field">
              <label class="boards-modal-label">Описание</label>
              <div class="task-description">
                {{ selectedTask?.description || 'Нет описания' }}
              </div>
            </div>

            <div class="boards-modal-field">
              <label class="boards-modal-label">Колонка</label>
              <div class="task-column">
                {{ getColumnTitle(selectedTask?.column_id) }}
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

// Данные для форм
const newTask = ref({
  title: '',
  description: '',
  column_id: null
})
const newMemberEmail = ref('')
const currentTaskMembers = ref([])
const selectedTask = ref(null)
const selectedTaskMembers = ref([])

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
      
      // Проверяем, есть ли пользователь в таблице users
      const { data: userData, error } = await supabase
        .from('users')
        .select('id')
        .eq('id', user.id)
        .single()
      
      if (error) {
        console.log('Пользователь не найден в таблице users, создаем...')
        // Создаем пользователя в таблице users
        const { data: newUser, error: createError } = await supabase
          .from('users')
          .insert({
            id: user.id,
            email: user.email,
            username: user.email.split('@')[0],
            password_hash: 'auth_user_no_password', // Фиктивное значение
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

// Методы модальных окон
const openModal = () => {
  showModal.value = true
  if (columns.value.length > 0 && !newTask.value.column_id) {
    // Автоматически выбираем первую колонку (обычно "В планах")
    newTask.value.column_id = columns.value[0].id
  }
}

const closeModal = () => {
  showModal.value = false
  newTask.value = {
    title: '',
    description: '',
    column_id: columns.value.length > 0 ? columns.value[0].id : null
  }
  currentTaskMembers.value = []
  newMemberEmail.value = ''
}

const openTaskDetails = async (task) => {
  selectedTask.value = task
  await loadTaskMembers(task.id)
  showTaskModal.value = true
}

const closeTaskModal = () => {
  showTaskModal.value = false
  selectedTask.value = null
  selectedTaskMembers.value = []
}

// Вспомогательные методы
const getColumnTitle = (columnId) => {
  const column = columns.value.find(col => col.id === columnId)
  return column ? column.title : 'Неизвестно'
}

const getTaskMembers = (taskId) => {
  return taskMembers.value.filter(member => member.task_id === taskId)
}

// Основные методы
const createTask = async () => {
  if (!newTask.value.title.trim()) return
  
  creating.value = true
  try {
    console.log('Создание задачи для доски:', boardId.value)
    console.log('Данные задачи:', newTask.value)
    
    // Проверяем, что выбрана колонка
    if (!newTask.value.column_id) {
      throw new Error('Не выбрана колонка для задачи')
    }

    // Проверяем, что есть текущий пользователь
    if (!currentUser.value) {
      throw new Error('Пользователь не авторизован')
    }

    // 1. Создаем задачу с обязательными полями
    const taskData = {
      title: newTask.value.title,
      description: newTask.value.description || null,
      column_id: newTask.value.column_id,
      position: tasks.value.length,
      creator_id: currentUser.value.id,
      assignee_id: currentUser.value.id, // Назначаем на текущего пользователя
      priority: 'medium', // Обязательное поле
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

    // 2. Добавляем участников если есть
    if (currentTaskMembers.value.length > 0) {
      console.log('Добавление участников:', currentTaskMembers.value)
      
      // Сначала находим ID пользователей по email
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

    // 3. Обновляем локальный список задач
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
    
    // Если есть колонки, устанавливаем первую как выбранную по умолчанию
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
    // Получаем текущего пользователя
    await getCurrentUser()
    // Затем загружаем остальные данные
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










<style scoped>
/* Стили остаются без изменений */
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

/* Kanban стили */
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
  border: 1px solid #9c8e71;
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
  font-size: 18px;
  text-wrap: wrap;
}

.item-desc {
  font-size: 18px;
  color: #ffffff;
  margin-bottom: 8px;
  line-height: 1.4;
}

.item-members {
  margin-top: 8px;
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

/* Кнопка создания */
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

/* Модальные окна */
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

.boards-modal-textarea {
  min-height: 80px;
  resize: vertical;
  font-family: inherit;
}

/* Стили для участников */
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

/* Действия модального окна */
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

/* Стили для просмотра задачи */
.task-description {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  color: #374151;
  line-height: 1.5;
}

.task-column {
  padding: 8px 12px;
  background: #e0e7ff;
  color: #3730a3;
  border-radius: 6px;
  display: inline-block;
  font-weight: 500;
}

/* Toast уведомления */
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
