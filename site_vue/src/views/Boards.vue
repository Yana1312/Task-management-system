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
                  <button 
                    v-if="canEditBoard(b.id)"
                    class="boards-edit-icon" 
                    @click.stop="openEditModal(b)" 
                    aria-label="Редактировать"
                  >✎</button>
                </div>
                <div class="boards-card-list">
                  <div class="boards-card-item">
                    <span class="item-title">{{ b.description || 'Без описания' }}</span>
                  </div>
                  <div class="boards-card-item muted">Создано: {{ formatDate(b.created_at) }}</div>
                  <div class="boards-card-item muted">
                    Участников: {{ getBoardMembersCount(b.id) }}
                  </div>
                </div>
                <div class="boards-card-footer">
                  <button class="boards-btn boards-btn-secondary" @click.stop="openBoard(b)">Открыть проект</button>
                  <button 
                    v-if="canEditBoard(b.id)"
                    class="boards-btn boards-btn-danger" 
                    @click.stop="deleteBoard(b)"
                  >Удалить проект</button>
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
                  <button 
                    v-if="canEditBoard(b.id)"
                    class="boards-edit-icon" 
                    @click.stop="openEditModal(b)" 
                    aria-label="Редактировать"
                  >✎</button>
                </div>
                <div class="boards-card-list">
                  <div class="boards-card-item">
                    <span class="item-title">{{ b.description || 'Без описания' }}</span>
                  </div>
                  <div class="boards-card-item muted">Создано: {{ formatDate(b.created_at) }}</div>
                  <div class="boards-card-item muted">
                    Участников: {{ getBoardMembersCount(b.id) }}
                  </div>
                  <div class="boards-card-item muted">
                    Админ: {{ getBoardAdmin(b.id)?.email || 'Вы' }}
                  </div>
                </div>
                <div class="boards-card-footer">
                  <button class="boards-btn boards-btn-secondary" @click.stop="openBoard(b)">Открыть проект</button>
                  <button 
                    v-if="canEditBoard(b.id)"
                    class="boards-btn boards-btn-danger" 
                    @click.stop="deleteBoard(b)"
                  >Удалить проект</button>
                </div>
              </div>
              <div v-if="teamBoards.length === 0" class="boards-empty">Нет командных досок</div>
            </div>
          </div>
        </div>

        <button class="boards-create-btn" @click="openCreateModal" aria-label="Создать доску">+</button>

        <!-- Модальное окно создания доски -->
        <div v-if="showCreateModal" class="boards-modal-overlay" @click="closeCreateModal">
          <div class="boards-modal boards-modal-large" @click.stop>
            <div class="boards-modal-header">
              <h2 class="boards-modal-title">Создание проекта</h2>
              <button class="boards-modal-close" @click="closeCreateModal">×</button>
            </div>
            
            <div class="boards-modal-body">
              <div class="boards-modal-section">
                <div class="boards-modal-field">
                  <label class="boards-modal-label">Название проекта *</label>
                  <input 
                    ref="modalNameInput"
                    v-model="newBoard.name" 
                    class="boards-modal-input" 
                    placeholder="Введите название проекта"
                  />
                </div>
                
                <div class="boards-modal-field">
                  <label class="boards-modal-label">Описание</label>
                  <textarea 
                    v-model="newBoard.description" 
                    class="boards-modal-textarea" 
                    placeholder="Краткое описание проекта"
                  ></textarea>
                </div>
                
                <div class="boards-modal-field">
                  <label class="boards-modal-label">Цвет проекта</label>
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

                <div v-if="newBoard.members.length > 0" class="boards-members-list">
                  <div class="boards-members-title">Участники проекта:</div>
                  <div 
                    v-for="(member, index) in newBoard.members" 
                    :key="index"
                    class="boards-member-item"
                  >
                    <div class="boards-member-info">
                      <span class="boards-member-email">{{ member.email }}</span>
                      <span v-if="member.role === 'admin'" class="boards-member-badge">Админ</span>
                      <span v-else class="boards-member-badge member">Участник</span>
                    </div>
                    <div class="boards-member-actions">
                      <button 
                        v-if="member.role !== 'admin'"
                        class="boards-member-btn boards-member-btn-promote"
                        @click="promoteToAdmin(index)"
                        title="Сделать администратором"
                      >
                        ⭐
                      </button>
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
              <button class="boards-modal-btn boards-modal-btn-cancel" @click="closeCreateModal">
                Отменить
              </button>
              <button 
                class="boards-modal-btn boards-modal-btn-create" 
                @click="createBoard"
                :disabled="!newBoard.name.trim() || creating"
              >
                {{ creating ? 'Создание...' : 'Создать проект' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Модальное окно редактирования доски -->
        <div v-if="showEditModal" class="boards-modal-overlay" @click="closeEditModal">
          <div class="boards-modal boards-modal-large" @click.stop>
            <div class="boards-modal-header">
              <h2 class="boards-modal-title">Редактирование проекта</h2>
              <button class="boards-modal-close" @click="closeEditModal">×</button>
            </div>
            
            <div class="boards-modal-body">
              <div class="boards-modal-section">
                <div class="boards-modal-field">
                  <label class="boards-modal-label">Название проекта *</label>
                  <input 
                    v-model="editingBoard.title" 
                    class="boards-modal-input" 
                    placeholder="Введите название проекта"
                  />
                </div>
                
                <div class="boards-modal-field">
                  <label class="boards-modal-label">Описание</label>
                  <textarea 
                    v-model="editingBoard.description" 
                    class="boards-modal-textarea" 
                    placeholder="Краткое описание проекта"
                  ></textarea>
                </div>
                
                <div class="boards-modal-field">
                  <label class="boards-modal-label">Цвет проекта</label>
                  <div class="boards-color-field">
                    <div 
                      class="boards-color-preview" 
                      :style="{ backgroundColor: editingBoard.background }"
                    ></div>
                    <input 
                      v-model="editingBoard.background" 
                      class="boards-modal-input boards-color-input" 
                      placeholder="#B54B11"
                    />
                  </div>
                </div>
              </div>

              <div class="boards-modal-section">
                <div class="boards-modal-field">
                  <label class="boards-modal-label">Информация о проекте</label>
                  <div class="boards-info-list">
                    <div class="boards-info-item">
                      <span class="boards-info-label">Создано:</span>
                      <span class="boards-info-value">{{ formatDate(editingBoard.created_at) }}</span>
                    </div>
                    <div class="boards-info-item">
                      <span class="boards-info-label">Администратор:</span>
                      <span class="boards-info-value">{{ getBoardAdmin(editingBoard.id)?.email || 'Вы' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="boards-modal-section">
                <div class="boards-modal-field">
                  <label class="boards-modal-label">Управление участниками</label>
                  <div class="boards-members-add">
                    <input 
                      v-model="editMemberEmail" 
                      class="boards-modal-input" 
                      placeholder="Email участника"
                      @keyup.enter="addEditMember"
                    />
                    <button class="boards-add-member-btn" @click="addEditMember">Добавить</button>
                  </div>
                </div>

                <div v-if="editingBoardMembers.length > 0" class="boards-members-list">
                  <div class="boards-members-title">Участники проекта:</div>
                  <div 
                    v-for="(member, index) in editingBoardMembers" 
                    :key="member.user_id"
                    class="boards-member-item"
                  >
                    <div class="boards-member-info">
                      <span class="boards-member-email">{{ member.email }}</span>
                      <span v-if="member.role === 'admin'" class="boards-member-badge">Админ</span>
                      <span v-else class="boards-member-badge member">Участник</span>
                      <span v-if="member.user_id === currentUserId" class="boards-member-badge current">Вы</span>
                    </div>
                    <div class="boards-member-actions">
                      <button 
                        v-if="canEditAdmin && member.user_id !== currentUserId"
                        class="boards-member-btn boards-member-btn-remove"
                        @click="removeEditMember(member.user_id)"
                        title="Удалить"
                      >
                        ×
                      </button>
                      <span v-if="!canEditAdmin && member.role !== 'admin'" class="boards-member-hint">
                      </span>
                      <span v-if="member.user_id === currentUserId" class="boards-member-hint">
                        Это вы
                      </span>
                    </div>
                  </div>
                </div>
                <div v-else class="boards-members-empty">
                  Нет дополнительных участников
                </div>
              </div>
            </div>
            
            <div class="boards-modal-actions">
              <button class="boards-modal-btn boards-modal-btn-cancel" @click="closeEditModal">
                Отменить
              </button>
              <button 
                class="boards-modal-btn boards-modal-btn-create" 
                @click="updateBoard"
                :disabled="!editingBoard.title.trim() || updating"
              >
                {{ updating ? 'Сохранение...' : 'Сохранить изменения' }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="toast.visible" :class="['toast', `toast-${toast.type}`]">
          {{ toast.message }}
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
const boardMembers = ref(new Map())
const loading = ref(true)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const creating = ref(false)
const updating = ref(false)
const deleting = ref(false)
const newMemberEmail = ref('')
const editMemberEmail = ref('')
const currentUserEmail = ref('')
const currentUserId = ref(null)
const roles = ref({})

const modalNameInput = ref(null)

const newBoard = ref({
  name: '',
  description: '',
  color: '#B54B11',
  members: []
})

const editingBoard = ref({
  id: null,
  title: '',
  description: '',
  background: '#B54B11',
  created_at: null
})

const editingBoardMembers = ref([])

const cardBg = '#B54B11'

const toast = ref({ visible: false, type: 'success', message: '' })

const canEditBoard = (boardId) => {
  const currentUserId = auth.userId.value
  const members = boardMembers.value.get(boardId) || []
  const adminMember = members.find(m => m.user_id === currentUserId && m.role === 'admin')
  return !!adminMember
}

const personalBoards = computed(() => {
  const uid = auth.userId.value
  return boards.value.filter(b => {
    const membersCount = getBoardMembersCount(b.id)
    return b.creator_id === uid && membersCount === 1
  })
})

const teamBoards = computed(() => {
  const uid = auth.userId.value
  return boards.value.filter(b => {
    const membersCount = getBoardMembersCount(b.id)
    return b.creator_id !== uid || membersCount > 1
  })
})

const canEditAdmin = computed(() => {
  const currentUserId = auth.userId.value
  const adminMember = editingBoardMembers.value.find(m => m.role === 'admin' && m.user_id === currentUserId)
  return !!adminMember
})

const openBoard = (b) => { 
  router.push({ name: 'board', params: { id: b.id } }) 
}

const openCreateModal = async () => { 
  showCreateModal.value = true
  newBoard.value = {
    name: '',
    description: '',
    color: '#B54B11',
    members: []
  }
  newMemberEmail.value = ''
  
  await getCurrentUserEmail()
  await loadRoles()
}

const closeCreateModal = () => { 
  showCreateModal.value = false
}

const openEditModal = async (board) => {
  if (!canEditBoard(board.id)) {
    showToast('Только администратор может редактировать проект', 'error')
    return
  }

  editingBoard.value = {
    id: board.id,
    title: board.title,
    description: board.description || '',
    background: board.background || '#B54B11',
    created_at: board.created_at
  }
  
  await loadBoardMembersForEdit(board.id)
  showEditModal.value = true
}

const closeEditModal = () => { 
  showEditModal.value = false
  editingBoardMembers.value = []
}

const deleteBoard = async (board) => {
  if (!canEditBoard(board.id)) {
    showToast('Только администратор может удалить проект', 'error')
    return
  }

  if (!confirm(`Вы уверены, что хотите удалить проект "${board.title}"? Это действие нельзя отменить.`)) {
    return
  }

  deleting.value = true
  try {
    const { data: columns, error: columnsError } = await supabase
      .from('columns')
      .select('id')
      .eq('board_id', board.id)

    if (columnsError) throw columnsError

    if (columns && columns.length > 0) {
      const columnIds = columns.map(column => column.id)

      const { data: tasks, error: tasksError } = await supabase
        .from('tasks')
        .select('id')
        .in('column_id', columnIds)

      if (tasksError) throw tasksError

      if (tasks && tasks.length > 0) {
        const taskIds = tasks.map(task => task.id)
        const { error: attachmentsError } = await supabase
          .from('attachments')
          .delete()
          .in('task_id', taskIds)

        if (attachmentsError) throw attachmentsError
      }

      const { error: deleteTasksError } = await supabase
        .from('tasks')
        .delete()
        .in('column_id', columnIds)

      if (deleteTasksError) throw deleteTasksError
    }

    const { error: deleteColumnsError } = await supabase
      .from('columns')
      .delete()
      .eq('board_id', board.id)

    if (deleteColumnsError) throw deleteColumnsError

    const { error: membersError } = await supabase
      .from('user_roles')
      .delete()
      .eq('board_id', board.id)

    if (membersError) throw membersError

    const { error } = await supabase
      .from('boards')
      .delete()
      .eq('id', board.id)

    if (error) throw error

    boards.value = boards.value.filter(b => b.id !== board.id)
    showToast('Проект успешно удален', 'success')
  } catch (error) {
    console.error('Error deleting board:', error)
    showToast('Ошибка при удалении проекта', 'error')
  } finally {
    deleting.value = false
  }
}

async function loadBoardMembersForEdit(boardId) {
  try {
    const { data: membersData, error } = await supabase
      .from('user_roles')
      .select(`
        user_id,
        roles:role_id (name_role),
        users:user_id (email)
      `)
      .eq('board_id', boardId)

    if (error) throw error

    editingBoardMembers.value = (membersData || []).map(member => ({
      user_id: member.user_id,
      email: member.users?.email,
      role: member.roles?.name_role || 'member'
    }))

  } catch (error) {
    console.error('Error loading board members for edit:', error)
    editingBoardMembers.value = []
  }
}

async function loadRoles() {
  try {
    const { data, error } = await supabase
      .from('roles')
      .select('id, name_role')
    
    if (error) throw error
    
    roles.value = {}
    data.forEach(role => {
      roles.value[role.name_role] = role.id
    })
    
  } catch (error) {
    console.error('Error loading roles:', error)
    showToast('Ошибка загрузки ролей', 'error')
  }
}

async function getCurrentUserEmail() {
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.user) {
      currentUserEmail.value = session.user.email.toLowerCase()
      currentUserId.value = session.user.id
    }
  } catch (error) {
    console.error('Error getting current user email:', error)
  }
}

const addMember = async () => {
  const email = newMemberEmail.value.trim().toLowerCase()
  
  if (!email) {
    showToast('Введите email участника', 'error')
    return
  }

  if (email === currentUserEmail.value) {
    showToast('Нельзя добавить самого себя в проект', 'error')
    return
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    showToast('Введите корректный email', 'error')
    return
  }

  if (newBoard.value.members.some(m => m.email === email)) {
    showToast('Этот участник уже добавлен', 'error')
    return
  }

  try {
    const { data: user, error } = await supabase
      .from('users')
      .select('id, email')
      .eq('email', email)
      .single()

    if (error || !user) {
      showToast('Пользователь с таким email не найден', 'error')
      return
    }

    newBoard.value.members.push({
      email: email,
      userId: user.id,
      role: 'member'
    })

    newMemberEmail.value = ''
    showToast('Участник добавлен', 'success')

  } catch (error) {
    console.error('Error checking user:', error)
    showToast('Ошибка при проверке пользователя', 'error')
  }
}

const addEditMember = async () => {
  const email = editMemberEmail.value.trim().toLowerCase()
  
  if (!email) {
    showToast('Введите email участника', 'error')
    return
  }

  if (email === currentUserEmail.value) {
    showToast('Нельзя добавить самого себя в проект', 'error')
    return
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    showToast('Введите корректный email', 'error')
    return
  }

  if (editingBoardMembers.value.some(m => m.email === email)) {
    showToast('Этот участник уже добавлен', 'error')
    return
  }

  try {
    const { data: user, error } = await supabase
      .from('users')
      .select('id, email')
      .eq('email', email)
      .single()

    if (error || !user) {
      showToast('Пользователь с таким email не найден', 'error')
      return
    }

    const { error: addError } = await supabase
      .from('user_roles')
      .insert({
        board_id: editingBoard.value.id,
        user_id: user.id,
        role_id: roles.value.member,
        created_at: new Date().toISOString()
      })

    if (addError) throw addError

    editingBoardMembers.value.push({
      user_id: user.id,
      email: email,
      role: 'member'
    })

    await loadBoardMembers()

    editMemberEmail.value = ''
    showToast('Участник добавлен', 'success')

  } catch (error) {
    console.error('Error adding member:', error)
    showToast('Ошибка при добавлении участника', 'error')
  }
}

const removeMember = (index) => {
  newBoard.value.members.splice(index, 1)
}

const removeEditMember = async (userId) => {
  if (!canEditAdmin.value) {
    showToast('Только администратор может удалять участников', 'error')
    return
  }

  if (userId === currentUserId.value) {
    showToast('Нельзя удалить самого себя из проекта', 'error')
    return
  }

  const board = boards.value.find(b => b.id === editingBoard.value.id)
  if (board && board.creator_id === userId) {
    showToast('Нельзя удалить создателя проекта', 'error')
    return
  }

  try {
    const { error } = await supabase
      .from('user_roles')
      .delete()
      .eq('board_id', editingBoard.value.id)
      .eq('user_id', userId)

    if (error) throw error

    editingBoardMembers.value = editingBoardMembers.value.filter(m => m.user_id !== userId)

    await loadBoardMembers()

    showToast('Участник удален из проекта', 'success')

  } catch (error) {
    console.error('Error removing member:', error)
    showToast('Ошибка при удалении участника', 'error')
  }
}

const promoteToAdmin = (index) => {
  showToast('Администратором всегда является создатель проекта', 'info')
}

const showToast = (message, type = 'success') => {
  toast.value = { visible: true, type, message }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

const formatDate = (iso) => {
  if (!iso) return ''
  try { return new Date(iso).toLocaleDateString() } catch { return '' }
}

const getBoardMembersCount = (boardId) => {
  return boardMembers.value.get(boardId)?.length || 1
}

const getBoardAdmin = (boardId) => {
  const members = boardMembers.value.get(boardId) || []
  const adminMember = members.find(m => m.role === 'admin')
  return adminMember || null
}

async function ensureUserId() {
  if (auth.userId.value) return auth.userId.value
  const { data } = await supabase.auth.getUser()
  const uid = data?.user?.id || null
  if (uid) auth.setUser(uid)
  return uid
}

async function loadBoardMembers() {
  const uid = await ensureUserId()
  if (!uid) return

  try {
    const { data: membersData, error } = await supabase
      .from('user_roles')
      .select(`
        board_id,
        user_id,
        roles:role_id (name_role),
        users:user_id (email)
      `)

    if (error) throw error

    const membersMap = new Map()
    membersData?.forEach(member => {
      if (!membersMap.has(member.board_id)) {
        membersMap.set(member.board_id, [])
      }
      membersMap.get(member.board_id).push({
        user_id: member.user_id,
        email: member.users?.email,
        role: member.roles?.name_role || 'member'
      })
    })

    boardMembers.value = membersMap

  } catch (error) {
    console.warn('Error loading board members:', error)
  }
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
    await loadRoles()

    const { data: userRoles, error: rolesError } = await supabase
      .from('user_roles')
      .select('board_id')
      .eq('user_id', uid)

    if (rolesError) throw rolesError

    const assignedIds = (userRoles || []).map(r => r.board_id).filter(Boolean)

    if (assignedIds.length === 0) {
      boards.value = []
      loading.value = false
      return
    }

    const { data: assignedBoards, error: assignedError } = await supabase
      .from('boards')
      .select('*')
      .in('id', assignedIds)
    
    if (assignedError) throw assignedError

    boards.value = (assignedBoards || []).sort((a, b) => 
      String(b.created_at || '').localeCompare(String(a.created_at || ''))
    )

    await loadBoardMembers()

  } catch (e) {
    console.warn('Error loading boards:', e)
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
    if (error) console.warn('Error creating default columns:', error)
  } catch (e) {
    console.warn('Error creating default columns:', e)
  }
}

async function addBoardMembers(boardId, members) {
  try {
    const uid = await ensureUserId()
    
    if (!roles.value.admin || !roles.value.member) {
      throw new Error('Роли не загружены')
    }

    const membersToAdd = [
      {
        board_id: boardId,
        user_id: uid,
        role_id: roles.value.admin,
        created_at: new Date().toISOString()
      }
    ]

    members.forEach(member => {
      const roleId = roles.value.member
      membersToAdd.push({
        board_id: boardId,
        user_id: member.userId,
        role_id: roleId,
        created_at: new Date().toISOString()
      })
    })

    const { error } = await supabase
      .from('user_roles')
      .insert(membersToAdd)

    if (error) throw error

  } catch (error) {
    console.warn('Error adding board members:', error)
    throw error
  }
}

async function createBoard() {
  const { data: { session }, error: sessionError } = await supabase.auth.getSession()
  
  if (sessionError || !session) {
    showToast('Пожалуйста, войдите в систему', 'error')
    return
  }
  
  const uid = session.user.id
  creating.value = true
  
  try {
    const now = new Date().toISOString()
    
    const { data, error } = await supabase
      .from('boards')
      .insert({
        title: newBoard.value.name,
        description: newBoard.value.description || null,
        background: newBoard.value.color || null,
        is_public: newBoard.value.members.length > 0,
        creator_id: uid,
        created_at: now,
      })
      .select()
      .single()
    
    if (error) {
      console.error('Board creation error:', error)
      throw error
    }

    await addBoardMembers(data.id, newBoard.value.members)

    await createDefaultColumns(data.id)
    
    await loadBoards()
    
    closeCreateModal()
    showToast('Проект успешно создан!', 'success')

  } catch (error) {
    console.warn('Error creating board:', error)
    showToast('Ошибка при создании проекта: ' + error.message, 'error')
  } finally {
    creating.value = false
  }
}

async function updateBoard() {
  updating.value = true
  
  try {
    const { error } = await supabase
      .from('boards')
      .update({
        title: editingBoard.value.title,
        description: editingBoard.value.description || null,
        background: editingBoard.value.background || null
      })
      .eq('id', editingBoard.value.id)

    if (error) throw error

    const boardIndex = boards.value.findIndex(b => b.id === editingBoard.value.id)
    if (boardIndex !== -1) {
      boards.value[boardIndex].title = editingBoard.value.title
      boards.value[boardIndex].description = editingBoard.value.description
      boards.value[boardIndex].background = editingBoard.value.background
    }

    await loadBoardMembers()

    closeEditModal()
    showToast('Проект успешно обновлен!', 'success')

  } catch (error) {
    console.error('Error updating board:', error)
    showToast('Ошибка при обновлении проекта: ' + error.message, 'error')
  } finally {
    updating.value = false
  }
}

onMounted(() => { 
  loadBoards() 
})

watch(showCreateModal, async (v) => {
  if (v) {
    await nextTick()
    modalNameInput.value?.focus()
  }
})
</script>

<style scoped>
.boards-info-list {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.boards-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
}

.boards-info-item:last-child {
  border-bottom: none;
}

.boards-info-label {
  font-weight: 500;
  color: #495057;
}

.boards-info-value {
  color: #6c757d;
}

.boards-member-hint {
  font-size: 12px;
  color: #6c757d;
  font-style: italic;
}

.boards-members-empty {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px dashed #dee2e6;
}

.boards-member-badge.current {
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
}

.boards-card-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: auto;
}

.boards-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.boards-btn-secondary {
  background: #6c757d;
  color: white;
}

.boards-btn-secondary:hover {
  background: #5a6268;
}

.boards-btn-danger {
  background: #dc3545;
  color: white;
}

.boards-btn-danger:hover {
  background: #c82333;
}
</style>