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
                  <div class="boards-card-item muted">
                    Участников: {{ getBoardMembersCount(b.id) }}
                  </div>
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
                  <div class="boards-card-item muted">
                    Участников: {{ getBoardMembersCount(b.id) }}
                  </div>
                  <div class="boards-card-item muted">
                    Админ: {{ getBoardAdmin(b.id)?.email || 'Вы' }}
                  </div>
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
          <div class="boards-modal boards-modal-large" @click.stop>
            <div class="boards-modal-header">
              <h2 class="boards-modal-title">Создание проекта</h2>
              <button class="boards-modal-close" @click="closeModal">×</button>
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
              <button class="boards-modal-btn boards-modal-btn-cancel" @click="closeModal">
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
const showModal = ref(false)
const creating = ref(false)
const newMemberEmail = ref('')
const currentUserEmail = ref('')
const roles = ref({})

const modalNameInput = ref(null)

const newBoard = ref({
  name: '',
  description: '',
  color: '#B54B11',
  members: []
})

const cardBg = '#B54B11'

const toast = ref({ visible: false, type: 'success', message: '' })

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

const openBoard = (b) => { 
  router.push({ name: 'board', params: { id: b.id } }) 
}

const openModal = async () => { 
  showModal.value = true
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

const closeModal = () => { 
  showModal.value = false
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
    if (session?.user?.email) {
      currentUserEmail.value = session.user.email.toLowerCase()
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

const removeMember = (index) => {
  newBoard.value.members.splice(index, 1)
}

const promoteToAdmin = (index) => {
  newBoard.value.members.forEach(member => {
    member.role = 'member'
  })
  newBoard.value.members[index].role = 'admin'
  showToast('Администратор назначен', 'success')
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

    const { data: ownBoards, error: ownError } = await supabase
      .from('boards')
      .select('*')
      .eq('creator_id', uid)

    if (ownError) throw ownError

    let assignedBoards = []
    if (assignedIds.length > 0) {
      const { data: assignedData, error: assignedError } = await supabase
        .from('boards')
        .select('*')
        .in('id', assignedIds)
      
      if (assignedError) throw assignedError
      assignedBoards = assignedData || []
    }

    const { data: publicBoards, error: publicError } = await supabase
      .from('boards')
      .select('*')
      .eq('is_public', true)

    if (publicError) throw publicError

    const merged = [...(ownBoards || []), ...assignedBoards, ...(publicBoards || [])]
    const uniqMap = new Map()
    merged.forEach(b => { if (b && b.id) uniqMap.set(b.id, b) })
    
    boards.value = Array.from(uniqMap.values()).sort((a, b) => 
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
      const roleId = member.role === 'admin' ? roles.value.admin : roles.value.member
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
    
    closeModal()
    showToast('Проект успешно создан!', 'success')

  } catch (error) {
    console.warn('Error creating board:', error)
    showToast('Ошибка при создании проекта: ' + error.message, 'error')
  } finally {
    creating.value = false
  }
}

onMounted(() => { 
  loadBoards() 
})

watch(showModal, async (v) => {
  if (v) {
    await nextTick()
    modalNameInput.value?.focus()
  }
})
</script>