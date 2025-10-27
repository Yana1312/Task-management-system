<template>
  <div class="container">
    <div class="main">
      <div class="page-content active" id="boards-page">
        <div class="boards-header">СУЩЕСТВУЮЩИЕ ПРОЕКТЫ</div>

        <div class="boards-sections">
          <div class="boards-section">
            <h3 class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</h3>
            <div v-if="loading" class="loading">Загрузка...</div>
            <div v-else class="boards-row">
              <div
                v-for="b in personalBoards"
                :key="b.id"
                class="boards-card"
                :style="{ backgroundColor: b.background || cardBg }"
                @click="openBoard(b)"
              >
                <div class="boards-card-header">
                  <div class="boards-pill">{{ b.title }}</div>
                  <button class="boards-edit-icon" @click.stop="openEdit(b)" aria-label="Редактировать">✎</button>
                </div>
                <div class="boards-card-list">
                  <div class="boards-card-item">
                    <span class="item-title">{{ b.description || 'Без описания' }}</span>
                  </div>
                  <div class="boards-card-item muted">Создано: {{ formatDate(b.created_at) }}</div>
                  <div class="boards-card-item muted">{{ b.is_public ? 'Публичная' : 'Личная' }}</div>
                </div>
                <div class="boards-card-footer">
                  <button class="boards-btn boards-btn-secondary" @click.stop="openBoard(b)">Открыть проект</button>
                  <button class="boards-btn boards-btn-primary" @click.stop="openEdit(b)">Редактировать</button>
                </div>
              </div>
              <div v-if="personalBoards.length === 0" class="boards-empty">Нет личных досок</div>
            </div>
          </div>

          <div class="boards-section">
            <h3 class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</h3>
            <div v-if="loading" class="loading">Загрузка...</div>
            <div v-else class="boards-row">
              <div
                v-for="b in teamBoards"
                :key="b.id"
                class="boards-card"
                :style="{ backgroundColor: b.background || cardBg }"
                @click="openBoard(b)"
              >
                <div class="boards-card-header">
                  <div class="boards-pill">{{ b.title }}</div>
                  <button class="boards-edit-icon" @click.stop="openEdit(b)" aria-label="Редактировать">✎</button>
                </div>
                <div class="boards-card-list">
                  <div class="boards-card-item">
                    <span class="item-title">{{ b.description || 'Без описания' }}</span>
                  </div>
                  <div class="boards-card-item muted">Создано: {{ formatDate(b.created_at) }}</div>
                  <div class="boards-card-item muted">{{ b.is_public ? 'Публичная' : 'Личная' }}</div>
                </div>
                <div class="boards-card-footer">
                  <button class="boards-btn boards-btn-secondary" @click.stop="openBoard(b)">Открыть проект</button>
                  <button class="boards-btn boards-btn-primary" @click.stop="openEdit(b)">Редактировать</button>
                </div>
              </div>
              <div v-if="teamBoards.length === 0" class="boards-empty">Нет командных досок</div>
            </div>
          </div>
        </div>

        <button class="boards-create-btn" @click="openModal" aria-label="Создать доску">+</button>

        <div v-if="showModal" class="boards-modal-overlay" @click="closeModal">
          <div class="boards-modal" @click.stop>
            <div class="boards-modal-header">
              <h2 class="boards-modal-title">Создание доски</h2>
              <button class="boards-modal-close" @click="closeModal">×</button>
            </div>
            
            <div class="boards-modal-body">
              <div class="boards-modal-field">
                <label class="boards-modal-label">Название</label>
                <input 
                  ref="modalNameInput"
                  v-model="newBoard.name" 
                  class="boards-modal-input" 
                  placeholder="Введите название доски"
                />
              </div>
              
              <div class="boards-modal-field">
                <label class="boards-modal-label">Описание</label>
                <textarea 
                  v-model="newBoard.description" 
                  class="boards-modal-textarea" 
                  placeholder="Краткое описание"
                ></textarea>
              </div>
              
              <div class="boards-modal-field">
                <label class="boards-modal-label">Цвет/фон</label>
                <div class="boards-color-field">
                  <div 
                    class="boards-color-preview" 
                    :style="{ backgroundColor: newBoard.color }"
                  ></div>
                  <input 
                    v-model="newBoard.color" 
                    class="boards-modal-input boards-color-input" 
                    placeholder="#B54B11"
                  />
                </div>
              </div>
              
              <div class="boards-modal-field">
                <label class="boards-modal-label">Доступ</label>
                <div class="boards-access-field">
                  <div class="boards-access-toggle">
                    <button 
                      class="boards-access-option" 
                      :class="{ active: !newBoard.isPublic }"
                      @click="newBoard.isPublic = false"
                    >Личная
                    </button>
                    <button 
                      class="boards-access-option" 
                      :class="{ active: newBoard.isPublic }"
                      @click="newBoard.isPublic = true"
                    >Публичная
                    </button>
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
                @click="createBoard"
                :disabled="!newBoard.name.trim()">Создать
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '../lib/supabase.js'
import { auth } from '../js/auth.js'

const router = useRouter()
const boards = ref([])
const loading = ref(true)
const modalOpen = ref(false)
const creating = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const firstField = ref(null)

const title = ref('')
const description = ref('')
const background = ref('#B54B11')
const isPublic = ref(false)

const showModal = ref(false)
const modalNameInput = ref(null)
const newBoard = ref({
  name: '',
  description: '',
  color: '#B54B11',
  isPublic: false
})

const cardBg = '#B54B11'

const personalBoards = computed(() => {
  const uid = auth.userId.value
  return boards.value.filter(b => b.creator_id === uid)
})
const teamBoards = computed(() => {
  const uid = auth.userId.value
  return boards.value.filter(b => b.creator_id !== uid)
})

const openBoard = (b) => { router.push({ name: 'board', params: { id: b.id } }) }
const openModal = () => { 
  showModal.value = true
  newBoard.value = {
    name: '',
    description: '',
    color: '#B54B11',
    isPublic: false
  }
}
const closeModal = () => { 
  showModal.value = false
}

const showToast = (message, type = 'success') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => { toast.value.visible = false }, 3500)
}
const toast = ref({ visible: false, type: 'success', message: '' })

const formatDate = (iso) => {
  if (!iso) return ''
  try { return new Date(iso).toLocaleDateString() } catch { return '' }
}

async function ensureUserId() {
  if (auth.userId.value) return auth.userId.value
  const { data } = await supabase.auth.getUser()
  const uid = data?.user?.id || null
  if (uid) auth.setUser(uid)
  return uid
}

async function loadBoards() {
  loading.value = true
  const uid = await ensureUserId()
  if (!uid) {
    boards.value = []
    loading.value = false
    showToast('Войдите, чтобы увидеть ваши доски', 'error')
    return
  }

  try {
    const assignedRes = await supabase.from('user_roles').select('board_id').eq('user_id', uid)
    const assignedIds = (assignedRes.data || []).map(r => r.board_id).filter(Boolean)

    const ownReq = supabase.from('boards').select('*').eq('creator_id', uid)
    const assignedReq = assignedIds.length
      ? supabase.from('boards').select('*').in('id', assignedIds)
      : Promise.resolve({ data: [] })
    const publicReq = supabase.from('boards').select('*').eq('is_public', true)

    const [ownRes, assignedBoardsRes, publicRes] = await Promise.all([ownReq, assignedReq, publicReq])
    const merged = [...(ownRes.data || []), ...(assignedBoardsRes.data || []), ...(publicRes.data || [])]
    const uniqMap = new Map()
    merged.forEach(b => { if (b && b.id) uniqMap.set(b.id, b) })
    boards.value = Array.from(uniqMap.values()).sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
  } catch (e) {
    console.warn('[boards] loadBoards error:', e)
    showToast('Не удалось загрузить доски', 'error')
  } finally {
    loading.value = false
  }
}

async function createDefaultColumns(boardId) {
  const defaults = [
    { title: 'В планах', position: 1, color: '#6e8f72' },
    { title: 'В работе', position: 2, color: '#a2b8a5' },
    { title: 'Готово', position: 3, color: '#c7d6c9' },
  ].map(c => ({ ...c, board_id: boardId }))
  try {
    const { error } = await supabase.from('columns').insert(defaults)
    if (error) console.warn('[boards] default columns insert error:', error)
  } catch (e) {
    console.warn('[boards] default columns exception:', e)
  }
}

async function createBoard() {
  const uid = await ensureUserId()
  if (!uid) { showToast('Нужно войти в систему', 'error'); return }
  creating.value = true
  try {
    const now = new Date().toISOString()
    const { data, error } = await supabase
      .from('boards')
      .insert({
        title: newBoard.value.name,
        description: newBoard.value.description || null,
        background: newBoard.value.color || null,
        is_public: !!newBoard.value.isPublic,
        creator_id: uid,
        created_at: now,
      })
      .select()
      .single()
    if (error) { showToast('Не удалось создать доску', 'error'); creating.value = false; return }
    boards.value = [data, ...boards.value]
    closeModal()
    await createDefaultColumns(data.id)
    showToast('Доска создана', 'success')
  } catch (e) {
    console.warn('[boards] createBoard exception:', e)
    showToast('Ошибка при создании доски', 'error')
  } finally {
    creating.value = false
  }
}

onMounted(() => { loadBoards() })
</script>

watch(showModal, async (v) => {
  if (v) {
    await nextTick()
    modalNameInput.value?.focus()
  }
})
watch(modalOpen, async (v) => {
  if (v) {
    await nextTick()
    firstField.value?.focus()
  }
})