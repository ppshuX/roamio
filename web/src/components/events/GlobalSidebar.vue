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
            <i class="bi bi-x-lg"></i>
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
              @click="showAddEvent = true"
            >
              <i class="bi bi-plus-lg me-1"></i>
              添加待办
            </button>
          </div>
          
          <!-- 待办列表 -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">加载中...</span>
            </div>
          </div>
          
          <div v-else-if="allEvents.length === 0" class="empty-state">
            <i class="bi bi-calendar-plus text-muted mb-3" style="font-size: 64px;"></i>
            <h6 class="text-muted mb-2">还没有待办事项</h6>
            <p class="text-muted small mb-3">添加待办，设置提醒<br>让生活更有条理</p>
            <button 
              class="btn btn-primary btn-sm mb-3"
              @click="showAddEvent = true"
            >
              <i class="bi bi-plus-lg me-1"></i>
              添加第一个待办
            </button>
            <hr>
            <a 
              href="https://ralendar.com" 
              target="_blank" 
              class="btn btn-outline-primary btn-sm"
            >
              <i class="bi bi-box-arrow-up-right me-1"></i>
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
                  <button class="btn btn-sm btn-outline-secondary">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
              <p class="event-desc">{{ event.description }}</p>
              <div class="event-meta">
                <span v-if="event.event_time">
                  <i class="bi bi-clock"></i> {{ formatTime(event.event_time) }}
                </span>
                <span v-if="event.location_name">
                  <i class="bi bi-geo-alt"></i> {{ event.location_name }}
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
    const showAddEvent = ref(false)
    
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
      showAddEvent,
      formatTime
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

