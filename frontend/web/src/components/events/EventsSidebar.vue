<template>
  <div class="events-sidebar">
    <div class="sidebar-header">
      <h5>
        <i class="bi bi-calendar-check"></i> 旅行事项
      </h5>
      <button 
        v-if="isLoggedIn"
        @click="showEventForm = true" 
        class="btn btn-sm btn-primary"
      >
        <i class="bi bi-plus-lg"></i> 添加
      </button>
    </div>
    
    <div class="sidebar-body">
      <!-- 未登录提示 -->
      <div v-if="!isLoggedIn" class="login-prompt">
        <i class="bi bi-lock text-muted mb-3" style="font-size: 48px;"></i>
        <p class="text-muted mb-3">登录后即可管理旅行事项</p>
        <button @click="goToLogin" class="btn btn-primary btn-sm">
          <i class="bi bi-box-arrow-in-right me-1"></i>
          立即登录
        </button>
      </div>
      
      <!-- 已登录 - 显示事项列表 -->
      <template v-else>
        <!-- 加载状态 -->
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
          <p class="text-muted mt-2 mb-0 small">加载事项中...</p>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="cloudEvents.length === 0" class="empty-state-large">
          <i class="bi bi-calendar-plus text-muted mb-3" style="font-size: 64px;"></i>
          <h6 class="text-muted mb-2">还没有旅行事项</h6>
          <p class="text-muted small mb-3">添加景点、餐厅、活动等事项<br>让旅行更有条理</p>
          <button 
            class="btn btn-primary btn-sm"
            @click="showEventForm = true"
          >
            <i class="bi bi-plus-lg me-1"></i>
            添加第一个事项
          </button>
        </div>
        
        <!-- 事项列表 -->
        <div v-else class="events-list">
          <EventItem
            v-for="event in cloudEvents"
            :key="event.id"
            :event="event"
            :is-local="false"
            @edit="handleEdit"
            @delete="handleDelete"
          />
        </div>
      </template>
    </div>
    
    <!-- 添加/编辑事件表单 -->
    <EventForm 
      v-if="showEventForm"
      :trip-id="tripId"
      :event="editingEvent"
      @save="handleSave"
      @close="closeEventForm"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { getEvents, deleteEvent as deleteEventAPI } from '@/api/events'
import EventForm from './EventForm.vue'
import EventItem from './EventItem.vue'

const props = defineProps({
  tripId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update-count'])

const userStore = useUserStore()
const router = useRouter()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const showEventForm = ref(false)
const editingEvent = ref(null)
const cloudEvents = ref([])
const loading = ref(false)

// 监听登录状态变化
watch(isLoggedIn, (newVal) => {
  if (newVal) {
    loadCloudEvents()
  } else {
    cloudEvents.value = []
  }
})

onMounted(() => {
  if (isLoggedIn.value) {
    loadCloudEvents()
  }
})

/**
 * 加载云端事项
 */
const loadCloudEvents = async () => {
  if (!isLoggedIn.value) return
  
  loading.value = true
  try {
    const response = await getEvents(props.tripId)
    cloudEvents.value = response.data || response.results || []
  } catch (error) {
    console.error('加载云端事项失败:', error)
    cloudEvents.value = []
  } finally {
    loading.value = false
  }
}

/**
 * 处理保存
 */
const handleSave = () => {
  closeEventForm()
  loadCloudEvents()
}

/**
 * 处理编辑
 */
const handleEdit = (event) => {
  editingEvent.value = event
  showEventForm.value = true
}

/**
 * 处理删除
 */
const handleDelete = async (event) => {
  if (!confirm(`确定要删除事项"${event.title}"吗？`)) {
    return
  }
  
  try {
    await deleteEventAPI(props.tripId, event.id)
    loadCloudEvents()
  } catch (error) {
    alert('删除失败：' + (error.response?.data?.message || error.message))
  }
}

/**
 * 关闭事件表单
 */
const closeEventForm = () => {
  showEventForm.value = false
  editingEvent.value = null
}

/**
 * 跳转到登录页
 */
const goToLogin = () => {
  router.push('/auth/login')
}

// 监听事项数量变化，通知父组件
watch(cloudEvents, () => {
  emit('update-count', cloudEvents.value.length)
}, { immediate: true })
</script>

<style scoped>
.events-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 16px 20px;
  background: white;
  border-bottom: 2px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h5 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.events-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #dee2e6;
}

.section-header h6 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
}

.events-list {
  display: flex;
  flex-direction: column;
}

.empty-state-large {
  text-align: center;
  padding: 48px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.login-prompt {
  text-align: center;
  padding: 48px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.login-prompt p {
  margin: 0 0 16px 0;
  color: #666;
}

.badge {
  font-size: 12px;
  padding: 4px 8px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .events-sidebar {
    border-radius: 0;
  }
  
  .sidebar-header {
    padding: 12px 16px;
  }
  
  .sidebar-body {
    padding: 12px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
