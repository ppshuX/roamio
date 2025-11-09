<template>
  <div>
    <!-- 遮罩层（点击关闭） -->
    <transition name="fade">
      <div v-if="show" class="sidebar-overlay" @click="$emit('close')"></div>
    </transition>
    
    <!-- 全局右侧栏（桌面端） -->
    <transition name="slide-in">
      <div v-if="show" class="global-sidebar">
        <div class="sidebar-header">
          <h5>
            <img 
              src="/static/images/ralendar_logo_final.png" 
              alt="Ralendar"
              class="sidebar-logo"
            >
            Ralendar 待办
          </h5>
          <button @click="$emit('close')" class="btn-close" title="关闭">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
            </svg>
          </button>
        </div>
        
        <div class="sidebar-body">
        <!-- 未登录提示 -->
        <div v-if="!isLoggedIn" class="login-prompt">
          <i class="bi bi-lock text-muted mb-3" style="font-size: 48px;"></i>
          <p class="text-muted mb-3">登录后即可管理待办事项</p>
          <router-link to="/login" class="btn btn-primary btn-sm">
            <i class="bi bi-box-arrow-in-right me-1"></i>
            立即登录
          </router-link>
        </div>
        
        <!-- 已登录 - 显示所有待办 -->
        <template v-else>
          <!-- 快捷操作 -->
          <div class="quick-actions mb-3">
            <button 
              class="btn btn-primary w-100"
              @click="showAddForm = true"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 8px;">
                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
              </svg>
              添加待办
            </button>
          </div>
          
          <!-- 添加/编辑事件表单 -->
          <div v-if="showAddForm" class="add-event-form mb-3">
            <div class="card">
              <div class="card-body">
                <h6 class="card-title mb-3">{{ editingEventId ? '编辑待办' : '新建待办' }}</h6>
                <form @submit.prevent="handleAddEvent">
                  <div class="mb-3">
                    <label class="form-label small text-muted">标题 *</label>
                    <input 
                      v-model="newEvent.title" 
                      type="text" 
                      class="form-control" 
                      placeholder="例如：准备出行物品"
                      required
                    >
                  </div>
                  <div class="mb-3">
                    <label class="form-label small text-muted">描述（可选）</label>
                    <textarea 
                      v-model="newEvent.description" 
                      class="form-control" 
                      rows="2" 
                      placeholder="详细说明..."
                    ></textarea>
                  </div>
                  <div class="mb-3">
                    <label class="form-label small text-muted">时间 *</label>
                    <input 
                      v-model="newEvent.event_time" 
                      type="datetime-local" 
                      class="form-control"
                      required
                    >
                  </div>
                  <div class="d-flex gap-2">
                    <button type="submit" class="btn btn-primary btn-sm" :disabled="submitting">
                      <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
                      {{ submitting ? (editingEventId ? '保存中...' : '创建中...') : (editingEventId ? '保存' : '创建') }}
                    </button>
                    <button type="button" class="btn btn-secondary btn-sm" @click="cancelAdd">
                      取消
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
          
          <!-- 待办列表 -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">加载中...</span>
            </div>
          </div>
          
          <div v-else-if="allEvents.length === 0" class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="#6c757d" viewBox="0 0 16 16" style="margin-bottom: 1rem;">
              <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM2 2a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V3a1 1 0 0 0-1-1H2z"/>
              <path d="M2.5 4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H3a.5.5 0 0 1-.5-.5V4zM11 7.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1z"/>
            </svg>
            <h6 class="text-muted mb-2">还没有待办事项</h6>
            <p class="text-muted small mb-3">添加待办，设置提醒<br>让生活更有条理</p>
            <button 
              class="btn btn-primary btn-sm mb-3"
              @click="showAddForm = true"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 4px;">
                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
              </svg>
              添加第一个待办
            </button>
            <hr>
            <a 
              href="https://app7626.acapp.acwing.com.cn" 
              target="_blank" 
              class="btn btn-outline-primary btn-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 4px;">
                <path fill-rule="evenodd" d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"/>
                <path fill-rule="evenodd" d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"/>
              </svg>
              访问 Ralendar 完整版
            </a>
          </div>
          
          <div v-else class="events-list">
            <div
              v-for="event in allEvents"
              :key="event.id"
              class="event-item"
            >
              <div class="event-header">
                <h6 class="event-title">{{ event.title }}</h6>
                <div class="event-actions">
                  <button 
                    class="btn btn-sm btn-outline-secondary"
                    @click="handleEditEvent(event)"
                    title="编辑"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                    </svg>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="handleDeleteEvent(event)"
                    title="删除"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                      <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                    </svg>
                  </button>
                </div>
              </div>
              <p class="event-desc">{{ event.description }}</p>
              <div class="event-meta">
                <span v-if="event.start_time">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 4px;">
                    <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                    <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
                  </svg>
                  {{ formatTime(event.start_time) }}
                </span>
                <span v-if="event.location">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 4px;">
                    <path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/>
                  </svg>
                  {{ event.location }}
                </span>
              </div>
            </div>
          </div>
        </template>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, watch, defineComponent } from 'vue'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'GlobalSidebar',
  
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['close'],
  
  setup(props) {
    const userStore = useUserStore()
    
    const isLoggedIn = computed(() => userStore.isLoggedIn)
    const loading = ref(false)
    const allEvents = ref([])
    const showAddForm = ref(false)
    const submitting = ref(false)
    const editingEventId = ref(null)
    const newEvent = ref({
      title: '',
      description: '',
      event_time: ''
    })
    
    // 加载所有待办事项
    const loadAllEvents = async () => {
      if (!isLoggedIn.value) return
      
      loading.value = true
      try {
        // TODO: 调用 API 获取用户的所有待办事项
        // const response = await getAllUserEvents()
        // allEvents.value = response.data
        allEvents.value = []
      } catch (error) {
        console.error('加载待办失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 格式化时间
    const formatTime = (timeStr) => {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
    }
    
    // 添加/更新事件
    const handleAddEvent = async () => {
      if (!newEvent.value.title) {
        alert('请输入待办标题')
        return
      }
      
      if (!newEvent.value.event_time) {
        alert('请选择时间')
        return
      }
      
      submitting.value = true
      
      try {
        // 获取用户 Token
        const token = localStorage.getItem('access_token')
        if (!token) {
          alert('请先登录')
          return
        }
        
        // 准备事件数据
        const eventData = {
          title: newEvent.value.title,
          description: newEvent.value.description || '',
          start_time: newEvent.value.event_time ? new Date(newEvent.value.event_time).toISOString() : new Date().toISOString()
        }
        
        if (editingEventId.value) {
          // 编辑模式：调用更新 API
          console.log('📝 更新事件:', editingEventId.value, eventData)
          
          const response = await fetch(`https://app7626.acapp.acwing.com.cn/api/v1/events/${editingEventId.value}/`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(eventData)
          })
          
          if (!response.ok) {
            throw new Error('更新失败')
          }
          
          const result = await response.json()
          console.log('✅ 更新成功:', result)
          
          // 更新列表中的事件
          const index = allEvents.value.findIndex(e => e.id === editingEventId.value)
          if (index > -1) {
            allEvents.value[index] = result
          }
          
          alert('更新成功！')
        } else {
          // 创建模式
          console.log('📤 发送的数据:', eventData)
          
          const response = await fetch('/api/v1/ralendar/trips/events/', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(eventData)
          })
          
          console.log('📥 响应状态:', response.status, response.statusText)
          
          if (!response.ok) {
            const error = await response.json()
            console.error('❌ 错误响应:', error)
            throw new Error(error.error || '创建失败')
          }
          
          const result = await response.json()
          console.log('✅ 成功响应:', result)
          
          // 添加到列表
          allEvents.value.unshift(result)
          
          alert('创建成功！')
        }
        
        // 重置表单
        newEvent.value = {
          title: '',
          description: '',
          event_time: ''
        }
        editingEventId.value = null
        showAddForm.value = false
        
      } catch (error) {
        console.error('操作失败:', error)
        alert(error.message || '操作失败，请稍后重试')
      } finally {
        submitting.value = false
      }
    }
    
    // 取消添加/编辑
    const cancelAdd = () => {
      showAddForm.value = false
      editingEventId.value = null
      newEvent.value = {
        title: '',
        description: '',
        event_time: ''
      }
    }
    
    // 编辑事件
    const handleEditEvent = (event) => {
      // 填充表单
      newEvent.value = {
        title: event.title,
        description: event.description || '',
        event_time: event.start_time ? event.start_time.substring(0, 16) : ''
      }
      
      // 保存正在编辑的事件 ID
      editingEventId.value = event.id
      showAddForm.value = true
    }
    
    // 删除事件
    const handleDeleteEvent = async (event) => {
      if (!confirm(`确定要删除「${event.title}」吗？`)) {
        return
      }
      
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          alert('请先登录')
          return
        }
        
        // 调用 Ralendar API 删除事件
        const response = await fetch(`https://app7626.acapp.acwing.com.cn/api/v1/events/${event.id}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (!response.ok) {
          throw new Error('删除失败')
        }
        
        // 从列表中移除
        const index = allEvents.value.findIndex(e => e.id === event.id)
        if (index > -1) {
          allEvents.value.splice(index, 1)
        }
        
        alert('删除成功！')
      } catch (error) {
        console.error('删除事件失败:', error)
        alert('删除失败，请稍后重试')
      }
    }
    
    // 监听显示状态，打开时加载数据
    watch(() => props.show, (newVal) => {
      if (newVal && isLoggedIn.value) {
        loadAllEvents()
      }
    })
    
    return {
      isLoggedIn,
      loading,
      allEvents,
      showAddForm,
      submitting,
      editingEventId,
      newEvent,
      formatTime,
      handleAddEvent,
      cancelAdd,
      handleEditEvent,
      handleDeleteEvent
    }
  }
})
</script>

<style scoped>
.global-sidebar {
  position: fixed;
  top: 56px; /* 导航栏高度 */
  right: 0;
  width: 400px;
  height: calc(100vh - 56px);
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  z-index: 9998;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 2px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.sidebar-header h5 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-logo {
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.btn-close {
  background: white;
  border: none;
  color: #667eea;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 18px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-close:hover {
  background: #f8f9fa;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-close:active {
  transform: scale(0.95);
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

.login-prompt {
  text-align: center;
  padding: 48px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-prompt {
  text-align: center;
  padding: 48px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-item {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.event-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.event-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  flex: 1;
}

.event-actions {
  display: flex;
  gap: 4px;
}

.event-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.event-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 12px;
}

.event-meta i {
  margin-right: 4px;
}

.sidebar-overlay {
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 9997;
}

/* 动画 */
.slide-in-enter-active {
  transition: transform 0.3s ease-out;
}

.slide-in-leave-active {
  transition: transform 0.3s ease-in;
}

.slide-in-enter-from {
  transform: translateX(100%);
}

.slide-in-leave-to {
  transform: translateX(100%);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .global-sidebar {
    top: 0; /* 移动端从顶部开始 */
    height: 100vh;
    width: 85vw; /* 移动端占85%宽度 */
    max-width: 400px;
  }
  
  .sidebar-header {
    padding: 16px;
  }
  
  .sidebar-header h5 {
    font-size: 16px;
  }
  
  .sidebar-body {
    padding: 16px;
  }
  
  .sidebar-overlay {
    top: 0; /* 移动端遮罩从顶部开始 */
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  .global-sidebar {
    width: 320px;
  }
}
</style>

