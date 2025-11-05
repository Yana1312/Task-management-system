<template>
  <body>
    <div id="app" class="container">
      <div class="main-content">
        <div class="header-section">
          <div class="title-bar">АРХИВИРОВАННЫЕ ПРОЕКТЫ И ЗАДАЧИ</div>
        </div>

        <div v-if="loading" class="loading">
          <div class="loading-spinner"></div>
          <p>Загрузка архивных данных...</p>
        </div>

        <div v-else class="archive-sections">
          <div class="archive-panel personal-archive">
            <div class="section-title">ЛИЧНЫЕ ПРОЕКТЫ</div>
            <div class="archive-items">
              <div 
                class="archive-card" 
                v-for="project in personalProjects" 
                :key="'personal-' + project.id"
              >
                <h3>{{ project.board_title || 'Без названия' }}</h3>
                <p class="status">{{ formatStatus(project) }}</p>
                <div 
                  class="task-entry" 
                  v-for="task in project.tasks" 
                  :key="'task-' + task.id"
                >
                  <div class="task-info">
                    <span class="task-name">{{ task.title }}</span>
                    <span class="file-count" v-if="task.attachments && task.attachments.length > 1">
                      ({{ task.attachments.length }} файлов)
                    </span>
                  </div>
                  <a 
                    href="#" 
                    class="file-link"
                    @click.prevent="downloadAllFiles(task)"
                    v-if="task.attachments && task.attachments.length > 0"
                  >
                    <i class="fas fa-download"></i> 
                    <span v-if="task.attachments.length === 1">
                      {{ task.attachments[0].filename }}
                    </span>
                    <span v-else>
                      Скачать все файлы ({{ task.attachments.length }})
                    </span>
                  </a>
                </div>
                <div v-if="project.tasks.length === 0" class="no-tasks">
                  Нет завершенных задач с файлами
                </div>
              </div>
              <div v-if="personalProjects.length === 0" class="no-projects">
                <p>Нет персональных проектов с завершенными задачами</p>
              </div>
            </div>
          </div>

          <div class="archive-panel team-archive">
            <div class="section-title">КОМАНДНЫЕ ПРОЕКТЫ</div>
            <div class="archive-items">
              <div 
                class="archive-card" 
                v-for="project in teamProjects" 
                :key="'team-' + project.id"
              >
                <h3>{{ project.board_title || 'Без названия' }}</h3>
                <p class="status">{{ formatStatus(project) }}</p>
                <div 
                  class="task-entry" 
                  v-for="task in project.tasks" 
                  :key="'task-' + task.id"
                >
                  <div class="task-info">
                    <span class="task-name">{{ task.title }}</span>
                    <span class="file-count" v-if="task.attachments && task.attachments.length > 1">
                      ({{ task.attachments.length }} файлов)
                    </span>
                  </div>
                  <a 
                    href="#" 
                    class="file-link"
                    @click.prevent="downloadAllFiles(task)"
                    v-if="task.attachments && task.attachments.length > 0"
                  >
                    <i class="fas fa-download"></i> 
                    <span v-if="task.attachments.length === 1">
                      {{ task.attachments[0].filename }}
                    </span>
                    <span v-else>
                      Скачать все файлы ({{ task.attachments.length }})
                    </span>
                  </a>
                </div>
                <div v-if="project.tasks.length === 0" class="no-tasks">
                  Нет завершенных задач с файлами
                </div>
              </div>
              <div v-if="teamProjects.length === 0" class="no-projects">
                <p>Нет командных проектов с завершенными задачами</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="downloadProgress.visible" class="download-notification">
          <div class="notification-content">
            <div class="notification-icon">
              <i class="fas fa-file-archive"></i>
            </div>
            <div class="notification-text">
              <p>Подготовка архива...</p>
              <p class="notification-details">
                {{ downloadProgress.current }}/{{ downloadProgress.total }} файлов
              </p>
            </div>
            <div class="notification-spinner"></div>
          </div>
        </div>
      </div>
    </div>
  </body>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { supabase } from '../lib/supabase.js'
import JSZip from 'jszip'

export default {
  name: 'ArchiveView',
  setup() {
    const loading = ref(true)
    const archivedProjects = ref([])
    const currentUser = ref(null)
    const downloadProgress = ref({
      visible: false,
      current: 0,
      total: 0
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

    const loadArchivedData = async () => {
      try {
        loading.value = true
        
        const { data: userBoards, error: boardsError } = await supabase
          .from('user_roles')
          .select(`
            board_id,
            boards (
              id,
              title,
              creator_id,
              created_at
            )
          `)
          .eq('user_id', currentUser.value.id)

        if (boardsError) throw boardsError

        const { data: createdBoards, error: createdError } = await supabase
          .from('boards')
          .select('*')
          .eq('creator_id', currentUser.value.id)

        if (createdError) throw createdError

        const allBoardIds = new Set()
        const allBoards = []

        userBoards?.forEach(role => {
          if (role.boards && !allBoardIds.has(role.boards.id)) {
            allBoardIds.add(role.boards.id)
            allBoards.push(role.boards)
          }
        })

        createdBoards?.forEach(board => {
          if (!allBoardIds.has(board.id)) {
            allBoardIds.add(board.id)
            allBoards.push(board)
          }
        })

        const projectsWithTasks = []

        for (const board of allBoards) {
          const { data: doneColumns, error: columnsError } = await supabase
            .from('columns')
            .select('id')
            .eq('board_id', board.id)
            .ilike('title', '%готово%')

          if (columnsError) {
            console.error('Ошибка загрузки колонок:', columnsError)
            continue
          }

          if (doneColumns.length === 0) continue

          const doneColumnIds = doneColumns.map(col => col.id)

          const { data: completedTasks, error: tasksError } = await supabase
            .from('tasks')
            .select(`
              id,
              title,
              description,
              created_at,
              due_date,
              attachments (
                id,
                filename,
                file_path,
                file_size,
                uploaded_at
              )
            `)
            .in('column_id', doneColumnIds)
            .not('attachments', 'is', null)

          if (tasksError) {
            console.error('Ошибка загрузки задач:', tasksError)
            continue
          }

          const tasksWithFiles = completedTasks.filter(task => 
            task.attachments && task.attachments.length > 0
          )

          if (tasksWithFiles.length > 0) {
            projectsWithTasks.push({
              id: board.id,
              board_title: board.title,
              creator_id: board.creator_id,
              created_at: board.created_at,
              tasks: tasksWithFiles
            })
          }
        }

        archivedProjects.value = projectsWithTasks

      } catch (error) {
        console.error('Ошибка загрузки архивных данных:', error)
      } finally {
        loading.value = false
      }
    }

    const personalProjects = computed(() => {
      return archivedProjects.value.filter(project => {
        const isCreator = project.creator_id === currentUser.value?.id
        const hasMultipleMembers = project.tasks.some(task => 
          task.assignee_id !== currentUser.value?.id
        )
        return isCreator && !hasMultipleMembers
      })
    })

    const teamProjects = computed(() => {
      return archivedProjects.value.filter(project => {
        const isCreator = project.creator_id === currentUser.value?.id
        const hasMultipleMembers = project.tasks.some(task => 
          task.assignee_id !== currentUser.value?.id
        )
        return !isCreator || hasMultipleMembers
      })
    })

    const downloadAllFiles = async (task) => {
      try {
        downloadProgress.value = {
          visible: true,
          current: 0,
          total: task.attachments.length
        }

        const zip = new JSZip()
        const taskFolder = zip.folder(task.title.replace(/[^a-zA-Z0-9]/g, '_'))

        const taskInfo = `Задача: ${task.title}\n` +
                        `Описание: ${task.description || 'Нет описания'}\n` +
                        `Дата создания: ${formatDate(task.created_at)}\n` +
                        `Срок выполнения: ${task.due_date ? formatDate(task.due_date) : 'Не установлен'}\n` +
                        `Количество файлов: ${task.attachments.length}\n\n` +
                        'Список файлов:\n' +
                        task.attachments.map((att, index) => 
                          `${index + 1}. ${att.filename} (${formatFileSize(att.file_size)})`
                        ).join('\n')

        taskFolder.file('Информация_о_задаче.txt', taskInfo)

        for (let i = 0; i < task.attachments.length; i++) {
          const attachment = task.attachments[i]
          
          const fileInfo = `Информация о файле:\n\n` +
                          `Название: ${attachment.filename}\n` +
                          `Размер: ${formatFileSize(attachment.file_size)}\n` +
                          `Путь: ${attachment.file_path}\n` +
                          `Дата загрузки: ${formatDate(attachment.uploaded_at)}\n` +
                          `Тип файла: ${getFileType(attachment.filename)}\n\n` +
                          `Файл был прикреплен к задаче "${task.title}" как подтверждение выполнения.`

          const safeFileName = attachment.filename.replace(/[^a-zA-Z0-9.]/g, '_')
          const infoFileName = `Информация_${safeFileName}.txt`
          
          taskFolder.file(infoFileName, fileInfo)

          downloadProgress.value.current = i + 1
          
          await new Promise(resolve => setTimeout(resolve, 100))
        }

        const zipContent = await zip.generateAsync({ 
          type: 'blob',
          compression: 'DEFLATE',
          compressionOptions: { level: 6 }
        })

        const url = URL.createObjectURL(zipContent)
        const a = document.createElement('a')
        a.href = url
        a.download = `Архив_${task.title.replace(/[^a-zA-Z0-9]/g, '_')}_${new Date().getTime()}.zip`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

        setTimeout(() => {
          downloadProgress.value.visible = false
        }, 1000)

      } catch (error) {
        console.error('Ошибка создания архива:', error)
        downloadProgress.value.visible = false
        alert('Ошибка при создании архива файлов')
      }
    }

    const formatStatus = (project) => {
      const taskCount = project.tasks.length
      const fileCount = project.tasks.reduce((total, task) => 
        total + (task.attachments ? task.attachments.length : 0), 0
      )
      return `Завершено задач: ${taskCount}, файлов: ${fileCount}`
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Не указана'
      return new Date(dateString).toLocaleDateString('ru-RU')
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const getFileType = (filename) => {
      const ext = filename.split('.').pop().toLowerCase()
      const types = {
        'pdf': 'PDF документ',
        'doc': 'Word документ',
        'docx': 'Word документ',
        'xls': 'Excel таблица',
        'xlsx': 'Excel таблица',
        'zip': 'Архив',
        'rar': 'Архив',
        'jpg': 'Изображение',
        'jpeg': 'Изображение',
        'png': 'Изображение',
        'txt': 'Текстовый файл'
      }
      return types[ext] || `Файл .${ext}`
    }

    onMounted(async () => {
      await getCurrentUser()
      await loadArchivedData()
    })

    return {
      loading,
      personalProjects,
      teamProjects,
      downloadProgress,
      formatStatus,
      downloadAllFiles,
      formatFileSize
    }
  }
}
</script>

<style scoped>

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #E6D1A4;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(206, 121, 57, 0.3);
  border-left: 4px solid #CE7939;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-tasks {
  text-align: center;
  color: rgba(230, 209, 164, 0.6);
  font-style: italic;
  padding: 10px;
  font-size: 0.9em;
}

.no-projects {
  text-align: center;
  color: rgba(230, 209, 164, 0.6);
  font-style: italic;
  padding: 40px 20px;
  font-size: 1em;
}

/* Новые стили для отображения информации о файлах */
.task-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  gap: 4px;
}

.file-count {
  font-size: 0.8em;
  color: rgba(230, 209, 164, 0.7);
  font-style: italic;
}

/* Уведомление о скачивании */
.download-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #B54B11 0%, #CE7939 100%);
  border-radius: 12px;
  padding: 16px;
  color: #E6D1A4;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1000;
  animation: slideInRight 0.3s ease;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-icon {
  font-size: 1.5em;
  color: #E6D1A4;
}

.notification-text {
  flex-grow: 1;
}

.notification-text p {
  margin: 0;
  font-size: 0.9em;
}

.notification-details {
  font-size: 0.8em;
  color: rgba(230, 209, 164, 0.8);
  margin-top: 4px;
}

.notification-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(230, 209, 164, 0.3);
  border-left: 2px solid #E6D1A4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Обновленные стили для ссылки скачивания */
.archive-card .file-link {
  color: #E6D1A4;
  text-decoration: none;
  font-size: 0.85em;
  margin-left: 12px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(72, 9, 2, 0.4);
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid rgba(230, 209, 164, 0.2);
  min-width: fit-content;
}

.archive-card .file-link:hover {
  background: rgba(72, 9, 2, 0.6);
  transform: translateX(2px);
  text-decoration: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.archive-card .file-link i {
  font-size: 0.9em;
}

/* Остальные существующие стили... */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    background: linear-gradient(135deg, #E6D1A4 0%, #CE7939 100%);
    color: #2c3e50;
    min-height: 100vh;
    display: flex;
    padding: 20px;
}

.container {
    display: flex;
    width: 100%;
    gap: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.main-content {
    flex-grow: 1;
    background: #480902;
    border-radius: 20px;
    padding: 25px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    min-width: 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.header-section {
    margin-bottom: 20px;
}

.title-bar {
    background: linear-gradient(135deg, #B54B11 0%, #CE7939 100%);
    padding: 18px 25px;
    border-radius: 12px;
    font-size: 1.6em;
    color: #E6D1A4;
    text-align: center;
    margin: 0;
    font-weight: 700;
    letter-spacing: 1px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    box-shadow: 0 4px 15px rgba(181, 75, 17, 0.3);
}

.archive-sections {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 25px;
    flex-grow: 1;
}

.archive-panel {
    background: rgba(181, 75, 17, 0.1);
    border-radius: 15px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(206, 121, 57, 0.3);
    backdrop-filter: blur(10px);
}

.section-title {
    color: #CE7939;
    font-size: 1.4em;
    font-weight: 700;
    margin: 0 0 20px 0;
    letter-spacing: 1px;
    text-transform: uppercase;
    text-align: center;
    padding-bottom: 12px;
    border-bottom: 2px solid #CE7939;
}

.archive-items {
    display: flex;
    flex-direction: column;
    gap: 15px;
    flex-grow: 1;
}

.archive-card {
    background: linear-gradient(135deg, #B54B11 0%, #CE7939 100%);
    border-radius: 12px;
    padding: 18px;
    color: #E6D1A4;
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.archive-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.archive-card h3 {
    font-size: 1.1em;
    margin: 0 0 8px 0;
    color: #E6D1A4;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.archive-card .status {
    font-size: 0.85em;
    color: rgba(230, 209, 164, 0.9);
    margin-bottom: 12px;
    font-style: italic;
}

.archive-card .task-entry {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    font-size: 0.9em;
    margin-top: 10px;
    border-top: 1px solid rgba(230, 209, 164, 0.3);
    padding-top: 12px;
    gap: 12px;
}

.archive-card .task-entry .task-name {
    font-weight: 500;
    color: #E6D1A4;
}

@media (max-width: 768px) {
    .archive-card .task-entry {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }
    
    .archive-card .file-link {
        margin-left: 0;
        align-self: stretch;
        text-align: center;
        justify-content: center;
    }
    
    .download-notification {
        top: 10px;
        right: 10px;
        left: 10px;
    }
}

</style>