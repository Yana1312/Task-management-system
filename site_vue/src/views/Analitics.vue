<template>
  <div class="analytics-page">
    <div class="analytics-container">
      <div class="analytics-header">
        <h1>Аналитика продуктивности</h1>
        <p>Мониторинг загруженности и эффективности команды</p>
      </div>

      <div class="analytics-controls">
        <div class="control-group">
          <label>Период:</label>
          <select v-model="selectedPeriod" @change="loadAnalytics">
            <option value="7">Последние 7 дней</option>
            <option value="30">Последние 30 дней</option>
            <option value="90">Последние 3 месяца</option>
            <option value="365">Последний год</option>
          </select>
        </div>
        <div class="control-group">
          <label>Проект:</label>
          <select v-model="selectedProject" @change="onProjectChange">
            <option value="all">Все проекты</option>
            <option v-for="project in availableProjects" :key="project.id" :value="project.id">
              {{ project.title }}
            </option>
          </select>
        </div>
        <div class="control-group">
          <label>Участник:</label>
          <select v-model="selectedTeam" @change="loadAnalytics">
            <option value="all">Все участники</option>
            <option v-for="user in availableUsers" :key="user.id" :value="user.id">
              {{ user.email }}
            </option>
          </select>
        </div>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-tasks"></i>
          </div>
          <div class="metric-info">
            <h3>{{ analytics.totalTasks }}</h3>
            <p>Всего задач</p>
          </div>
          <div class="metric-trend" :class="getTrendClass(analytics.tasksTrend)">
            <i class="fas" :class="getTrendIcon(analytics.tasksTrend)"></i>
            {{ analytics.tasksTrend }}%
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon completed">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="metric-info">
            <h3>{{ analytics.completedTasks }}</h3>
            <p>Выполнено</p>
          </div>
          <div class="metric-trend" :class="getTrendClass(analytics.completionTrend)">
            <i class="fas" :class="getTrendIcon(analytics.completionTrend)"></i>
            {{ analytics.completionRate }}%
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon overdue">
            <i class="fas fa-clock"></i>
          </div>
          <div class="metric-info">
            <h3>{{ analytics.overdueTasks }}</h3>
            <p>Просрочено</p>
          </div>
          <div class="metric-trend negative">
            <i class="fas fa-exclamation-triangle"></i>
            {{ analytics.overdueRate }}%
          </div>
        </div>
      </div>

      <div class="analytics-sections">
        <div class="analytics-section">
          <h3>Загруженность команды</h3>
          <div class="section-content">
            <div class="workload-chart">
              <div v-for="user in userWorkload" :key="user.id" class="workload-item">
                <div class="user-info">
                  <div class="user-avatar">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <div class="user-details">
                    <strong>{{ user.username }}</strong>
                    <span>{{ user.email }}</span>
                  </div>
                </div>
                <div class="workload-stats">
                  <div class="stat">
                    <span class="stat-value">{{ user.active_tasks }}</span>
                    <span class="stat-label">активных</span>
                  </div>
                  <div class="stat">
                    <span class="stat-value">{{ user.completed_tasks }}</span>
                    <span class="stat-label">выполнено</span>
                  </div>
                  <div class="stat">
                    <span class="stat-value">{{ user.overdue_tasks }}</span>
                    <span class="stat-label">просрочено</span>
                  </div>
                </div>
                <div class="workload-bar">
                  <div class="workload-progress">
                    <div 
                      class="progress-segment completed" 
                      :style="{ width: user.completion_rate + '%' }"
                      :title="'Выполнено: ' + user.completion_rate + '%'"
                    ></div>
                    <div 
                      class="progress-segment overdue" 
                      :style="{ width: user.overdue_rate + '%' }"
                      :title="'Просрочено: ' + user.overdue_rate + '%'"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="analytics-section">
          <h3>Задачи по приоритетам</h3>
          <div class="section-content">
            <div class="priority-grid">
              <div v-for="priority in priorityDistribution" :key="priority.name" 
                   class="priority-item" :class="'priority-' + priority.name">
                <div class="priority-header">
                  <span class="priority-name">{{ getPriorityLabel(priority.name) }}</span>
                  <span class="priority-count">{{ priority.count }}</span>
                </div>
                <div class="priority-bar">
                  <div class="priority-progress" :style="{ width: priority.percentage + '%' }"></div>
                </div>
                <div class="priority-percentage">{{ priority.percentage }}%</div>
              </div>
            </div>
          </div>
        </div>

        <div class="analytics-section">
          <h3>Активность по проектам</h3>
          <div class="section-content">
            <div class="projects-activity">
              <div v-for="project in projectsActivity" :key="project.id" class="project-item">
                <div class="project-info">
                  <h4>{{ project.title }}</h4>
                  <p>{{ project.description }}</p>
                </div>
                <div class="project-stats">
                  <div class="project-metric">
                    <i class="fas fa-users"></i>
                    <span>{{ project.member_count }} участников</span>
                  </div>
                  <div class="project-metric">
                    <i class="fas fa-tasks"></i>
                    <span>{{ project.task_count }} задач</span>
                  </div>
                  <div class="project-metric">
                    <i class="fas fa-check"></i>
                    <span>{{ project.completion_rate }}% выполнено</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { supabase } from '../lib/supabase.js'

export default {
  name: 'AnalyticsView',
  setup() {
    const selectedPeriod = ref('30')
    const selectedTeam = ref('all')
    const selectedProject = ref('all')
    const analytics = ref({
      totalTasks: 0,
      completedTasks: 0,
      overdueTasks: 0,
      completionRate: 0,
      overdueRate: 0,
      tasksTrend: 0,
      completionTrend: 0
    })
    const userWorkload = ref([])
    const priorityDistribution = ref([])
    const projectsActivity = ref([])
    const availableUsers = ref([])
    const availableProjects = ref([])
    const loading = ref(false)

    const loadAnalytics = async () => {
      try {
        loading.value = true
        
        await Promise.all([
          loadGeneralMetrics(),
          loadUserWorkload(),
          loadPriorityDistribution(),
          loadProjectsActivity()
        ])
        
      } catch (error) {
        console.error('Ошибка загрузки аналитики:', error)
      } finally {
        loading.value = false
      }
    }

    const loadUserProjects = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session?.user) return

        const { data: userRoles, error } = await supabase
          .from('user_roles')
          .select(`
            board_id,
            boards!inner (
              id,
              title,
              description
            )
          `)
          .eq('user_id', session.user.id)

        if (error) throw error

        availableProjects.value = userRoles?.map(role => role.boards) || []
      } catch (error) {
        console.error('Ошибка загрузки проектов:', error)
      }
    }

    const loadProjectUsers = async (projectId) => {
      try {
        let query = supabase
          .from('user_roles')
          .select(`
            user_id,
            users!inner (
              id,
              email,
              username
            )
          `)

        if (projectId !== 'all') {
          query = query.eq('board_id', projectId)
        }

        const { data: projectUsers, error } = await query

        if (error) throw error

        const uniqueUsersMap = new Map()
        projectUsers?.forEach(pu => {
          if (pu.users && !uniqueUsersMap.has(pu.users.id)) {
            uniqueUsersMap.set(pu.users.id, pu.users)
          }
        })

        availableUsers.value = Array.from(uniqueUsersMap.values())
      } catch (error) {
        console.error('Ошибка загрузки пользователей проекта:', error)
      }
    }

    const onProjectChange = async () => {
      await loadProjectUsers(selectedProject.value)
      await loadAnalytics()
    }

    const loadGeneralMetrics = async () => {
      const days = parseInt(selectedPeriod.value)
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)

      try {
        let tasksQuery = supabase
          .from('tasks')
          .select(`
            *,
            columns!inner (
              board_id
            )
          `)
          .gte('created_at', startDate.toISOString())

        if (selectedProject.value !== 'all') {
          tasksQuery = tasksQuery.eq('columns.board_id', selectedProject.value)
        }

        if (selectedTeam.value !== 'all') {
          tasksQuery = tasksQuery.eq('assignee_id', selectedTeam.value)
        }

        const { data: tasks, error: tasksError } = await tasksQuery

        if (tasksError) throw tasksError

        const totalTasks = tasks?.length || 0
        const completedTasks = tasks?.filter(task => task.is_completed)?.length || 0
        const overdueTasks = tasks?.filter(task => 
          !task.is_completed && 
          task.due_date && 
          new Date(task.due_date) < new Date()
        )?.length || 0

        const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
        const overdueRate = totalTasks > 0 ? Math.round((overdueTasks / totalTasks) * 100) : 0

        analytics.value = {
          totalTasks,
          completedTasks,
          overdueTasks,
          completionRate,
          overdueRate,
          tasksTrend: 0,
          completionTrend: 0
        }

      } catch (error) {
        console.error('Ошибка в loadGeneralMetrics:', error)
        throw error
      }
    }

    const loadUserWorkload = async () => {
      const days = parseInt(selectedPeriod.value)
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)

      try {
        const userWorkloadMap = new Map()

        const workloadPromises = availableUsers.value.map(async (user) => {
          if (selectedTeam.value !== 'all' && user.id !== selectedTeam.value) {
            return null
          }

          let tasksQuery = supabase
            .from('tasks')
            .select(`
              *,
              columns!inner (
                board_id
              )
            `)
            .eq('assignee_id', user.id)
            .gte('created_at', startDate.toISOString())

          if (selectedProject.value !== 'all') {
            tasksQuery = tasksQuery.eq('columns.board_id', selectedProject.value)
          }

          const { data: userTasks, error: tasksError } = await tasksQuery

          if (tasksError) throw tasksError

          const activeTasks = userTasks?.filter(task => !task.is_completed)?.length || 0
          const completedTasks = userTasks?.filter(task => task.is_completed)?.length || 0
          const overdueTasks = userTasks?.filter(task => 
            !task.is_completed && 
            task.due_date && 
            new Date(task.due_date) < new Date()
          )?.length || 0

          const totalTasks = activeTasks + completedTasks + overdueTasks
          const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
          const overdueRate = totalTasks > 0 ? Math.round((overdueTasks / totalTasks) * 100) : 0

          return {
            id: user.id,
            username: user.username,
            email: user.email,
            active_tasks: activeTasks,
            completed_tasks: completedTasks,
            overdue_tasks: overdueTasks,
            completion_rate: completionRate,
            overdue_rate: overdueRate
          }
        })

        const results = await Promise.all(workloadPromises)
        
        const validResults = results.filter(user => user !== null)
        
        validResults.forEach(user => {
          userWorkloadMap.set(user.id, user)
        })

        userWorkload.value = Array.from(userWorkloadMap.values())

      } catch (error) {
        console.error('Ошибка в loadUserWorkload:', error)
        throw error
      }
    }

    const loadPriorityDistribution = async () => {
      const days = parseInt(selectedPeriod.value)
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)

      try {
        let tasksQuery = supabase
          .from('tasks')
          .select(`
            priority,
            columns!inner (
              board_id
            )
          `)
          .gte('created_at', startDate.toISOString())

        if (selectedProject.value !== 'all') {
          tasksQuery = tasksQuery.eq('columns.board_id', selectedProject.value)
        }

        if (selectedTeam.value !== 'all') {
          tasksQuery = tasksQuery.eq('assignee_id', selectedTeam.value)
        }

        const { data: tasks, error: tasksError } = await tasksQuery

        if (tasksError) throw tasksError

        const priorityCounts = (tasks || []).reduce((acc, task) => {
          acc[task.priority] = (acc[task.priority] || 0) + 1
          return acc
        }, {})

        const totalTasks = tasks ? tasks.length : 0
        const priorities = ['low', 'medium', 'high', 'critical']
        
        priorityDistribution.value = priorities.map(priority => ({
          name: priority,
          count: priorityCounts[priority] || 0,
          percentage: totalTasks > 0 ? Math.round(((priorityCounts[priority] || 0) / totalTasks) * 100) : 0
        })).filter(p => p.count > 0)

      } catch (error) {
        console.error('Ошибка в loadPriorityDistribution:', error)
        throw error
      }
    }

    const loadProjectsActivity = async () => {
      const days = parseInt(selectedPeriod.value)
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)

      try {
        let projectsQuery = availableProjects.value

        if (selectedProject.value !== 'all') {
          projectsQuery = availableProjects.value.filter(p => p.id === selectedProject.value)
        }

        const projectsPromises = projectsQuery.map(async (project) => {
          const { count: memberCount, error: memberError } = await supabase
            .from('user_roles')
            .select('*', { count: 'exact', head: true })
            .eq('board_id', project.id)

          if (memberError) throw memberError

          let tasksQuery = supabase
            .from('tasks')
            .select(`
              *,
              columns!inner (
                board_id
              )
            `)
            .eq('columns.board_id', project.id)
            .gte('created_at', startDate.toISOString())

          if (selectedTeam.value !== 'all') {
            tasksQuery = tasksQuery.eq('assignee_id', selectedTeam.value)
          }

          const { data: projectTasks, error: tasksError } = await tasksQuery

          if (tasksError) throw tasksError

          const totalTasks = projectTasks?.length || 0
          const completedTasks = projectTasks?.filter(task => task.is_completed)?.length || 0
          const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

          return {
            id: project.id,
            title: project.title,
            description: project.description,
            member_count: memberCount || 0,
            task_count: totalTasks,
            completion_rate: completionRate
          }
        })

        projectsActivity.value = await Promise.all(projectsPromises)

      } catch (error) {
        console.error('Ошибка в loadProjectsActivity:', error)
        throw error
      }
    }

    const getTrendClass = (trend) => {
      return trend > 0 ? 'positive' : trend < 0 ? 'negative' : 'neutral'
    }

    const getTrendIcon = (trend) => {
      return trend > 0 ? 'fa-arrow-up' : trend < 0 ? 'fa-arrow-down' : 'fa-minus'
    }

    const getPriorityLabel = (priority) => {
      const labels = {
        low: 'Низкий',
        medium: 'Средний',
        high: 'Высокий',
        critical: 'Критический'
      }
      return labels[priority] || priority
    }

    onMounted(async () => {
      await loadUserProjects()
      await loadProjectUsers('all')
      await loadAnalytics()
    })

    return {
      selectedPeriod,
      selectedTeam,
      selectedProject,
      analytics,
      userWorkload,
      priorityDistribution,
      projectsActivity,
      availableUsers,
      availableProjects,
      loading,
      loadAnalytics,
      onProjectChange,
      getTrendClass,
      getTrendIcon,
      getPriorityLabel
    }
  }
}
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background-color: #e6d1a4;
  padding: 20px;
}

.analytics-container {
  max-width: 1400px;
  margin: 0 auto;
  background-color: #480902;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.analytics-header {
  text-align: center;
  margin-bottom: 30px;
}

.analytics-header h1 {
  background: linear-gradient(135deg, #B54B11 0%, #CE7939 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 2.5em;
  margin-bottom: 10px;
}

.analytics-header p {
  color: #E6D1A4;
  opacity: 0.8;
  font-size: 1.1em;
}

.analytics-controls {
  display: flex;
  gap: 20px;
  align-items: end;
  margin-bottom: 30px;
  padding: 20px;
  background: rgba(181, 75, 17, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(206, 121, 57, 0.3);
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group label {
  color: #CE7939;
  font-weight: 600;
  font-size: 0.9em;
}

.control-group select {
  background: rgba(72, 9, 2, 0.6);
  border: 1px solid rgba(206, 121, 57, 0.3);
  border-radius: 8px;
  padding: 10px 12px;
  color: #E6D1A4;
  min-width: 180px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: linear-gradient(135deg, #B54B11 0%, #CE7939 100%);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5em;
}

.metric-icon.completed {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.metric-icon.overdue {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
}

.metric-info h3 {
  font-size: 1.8em;
  margin: 0;
  color: #E6D1A4;
}

.metric-info p {
  margin: 0;
  color: rgba(230, 209, 164, 0.8);
  font-size: 0.9em;
}

.metric-trend {
  margin-left: auto;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 600;
}

.metric-trend.positive {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.metric-trend.negative {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
}

.metric-trend.neutral {
  background: rgba(158, 158, 158, 0.2);
  color: #9E9E9E;
}

.analytics-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-bottom: 30px;
}

.analytics-section {
  background: rgba(181, 75, 17, 0.1);
  border-radius: 15px;
  padding: 20px;
  border: 1px solid rgba(206, 121, 57, 0.3);
}

.analytics-section h3 {
  color: #CE7939;
  margin: 0 0 20px 0;
  font-size: 1.2em;
}

.section-content {
  color: #E6D1A4;
}

.workload-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(206, 121, 57, 0.3);
}

.workload-item:last-child {
  border-bottom: none;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 200px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #B54B11 0%, #CE7939 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #E6D1A4;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-details strong {
  color: #E6D1A4;
}

.user-details span {
  font-size: 0.8em;
  opacity: 0.7;
}

.workload-stats {
  display: flex;
  gap: 15px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.stat-value {
  font-weight: bold;
  font-size: 1.1em;
}

.stat-label {
  font-size: 0.7em;
  opacity: 0.7;
}

.workload-bar {
  flex: 1;
  max-width: 200px;
}

.workload-progress {
  height: 8px;
  background: rgba(72, 9, 2, 0.6);
  border-radius: 4px;
  overflow: hidden;
  display: flex;
}

.progress-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-segment.completed {
  background: #4CAF50;
}

.progress-segment.overdue {
  background: #F44336;
}

.priority-grid {
  display: grid;
  gap: 10px;
}

.priority-item {
  background: rgba(72, 9, 2, 0.4);
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid;
}

.priority-low { border-left-color: #4CAF50; }
.priority-medium { border-left-color: #FF9800; }
.priority-high { border-left-color: #F44336; }
.priority-critical { border-left-color: #9C27B0; }

.priority-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.priority-name {
  font-weight: 600;
}

.priority-count {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.8em;
}

.priority-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.priority-progress {
  height: 100%;
  background: currentColor;
  transition: width 0.3s ease;
}

.priority-percentage {
  font-size: 0.8em;
  opacity: 0.7;
  text-align: right;
}

.projects-activity {
  display: grid;
  gap: 15px;
}

.project-item {
  background: rgba(72, 9, 2, 0.4);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(206, 121, 57, 0.3);
}

.project-info h4 {
  margin: 0 0 5px 0;
  color: #E6D1A4;
}

.project-info p {
  margin: 0;
  opacity: 0.7;
  font-size: 0.9em;
}

.project-stats {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

.project-metric {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9em;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .analytics-sections {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .workload-item {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .workload-stats {
    justify-content: space-between;
  }
  
  .workload-bar {
    max-width: none;
  }
}
</style>