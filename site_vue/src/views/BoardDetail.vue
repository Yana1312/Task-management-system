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
            <button class="kanban-add-btn" @click.prevent>+</button>
          </div>
        </div>
      </div>
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
/* стили перенесены в глобальный style.css под #board-page */
</style>