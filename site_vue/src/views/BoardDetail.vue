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
              <div v-for="t in tasksByColumn[col.id] || []" :key="t.id" class="kanban-item">
                <div class="item-title">{{ t.title }}</div>
                <div class="item-desc" v-if="t.description">{{ t.description }}</div>
              </div>
              <div v-if="(tasksByColumn[col.id] || []).length === 0" class="kanban-empty">Нет задач</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Кнопка создания -->
      <button class="boards-create-btn" @click="openModal" aria-label="Создать задачу">+</button>
    </div>

    <!-- Модальное окно должно быть здесь, на одном уровне с основным контентом -->
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

    <!-- Toast уведомления -->
    <div v-if="toast.visible" :class="['toast', `toast-${toast.type}`]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { supabase } from '../lib/supabase.js'

const route = useRoute()
const boardId = ref(route.params.id)
const board = ref(null)
const columns = ref([])
const tasks = ref([])
const loading = ref(true)

// Добавляем реактивные переменные для модального окна
const showModal = ref(false)
const creating = ref(false)

// Данные для новой задачи
const newTask = ref({
  title: '',
  description: '',
  column_id: null
})

// Toast уведомления
const toast = ref({ visible: false, type: 'success', message: '' })

// Функции модального окна
const openModal = () => {
  showModal.value = true
  // Устанавливаем первую колонку по умолчанию
  if (columns.value.length > 0 && !newTask.value.column_id) {
    newTask.value.column_id = columns.value[0].id
  }
}

const closeModal = () => {
  showModal.value = false
  // Сбрасываем форму
  newTask.value = {
    title: '',
    description: '',
    column_id: columns.value.length > 0 ? columns.value[0].id : null
  }
}

// Функция создания задачи
const createTask = async () => {
  if (!newTask.value.title.trim()) return
  
  creating.value = true
  try {
    const { data, error } = await supabase
      .from('tasks')
      .insert({
        title: newTask.value.title,
        description: newTask.value.description || null,
        column_id: newTask.value.column_id,
        board_id: boardId.value,
        position: tasks.value.length, // Добавляем в конец
        created_at: new Date().toISOString()
      })
      .select()
      .single()

    if (error) throw error

    // Добавляем новую задачу в список
    tasks.value.push(data)
    
    closeModal()
    showToast('Задача успешно создана!', 'success')
    
  } catch (error) {
    console.error('Error creating task:', error)
    showToast('Ошибка при создании задачи', 'error')
  } finally {
    creating.value = false
  }
}

// Функция для показа уведомлений
const showToast = (message, type = 'success') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

const tasksByColumn = computed(() => {
  const m = {}
  columns.value.forEach(c => { m[c.id] = [] })
  tasks.value.forEach(t => {
    if (!m[t.column_id]) m[t.column_id] = []
    m[t.column_id].push(t)
  })
  return m
})

async function loadBoard() {
  const { data } = await supabase.from('boards').select('*').eq('id', boardId.value).single()
  board.value = data || null
}

async function loadData() {
  loading.value = true
  try {
    const [colsRes, tasksRes] = await Promise.all([
      supabase.from('columns').select('*').eq('board_id', boardId.value).order('position', { ascending: true }),
      supabase.from('tasks').select('*').eq('board_id', boardId.value).order('position', { ascending: true })
    ])
    columns.value = colsRes.data || []
    tasks.value = tasksRes.data || []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadBoard()
  await loadData()
})
</script>

<style scoped>
/* Стили для кнопки создания */
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

/* Стили для модального окна */
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

.boards-modal-field {
  margin-bottom: 20px;
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
}

.boards-modal-textarea {
  min-height: 80px;
  resize: vertical;
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

/* Toast стили */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 6px;
  color: white;
  z-index: 3000;
  max-width: 300px;
}

.toast-success {
  background: #10b981;
}

.toast-error {
  background: #ef4444;
}
</style>