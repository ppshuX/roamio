<template>
  <div class="event-item" :class="{ 'event-completed': event.is_completed }">
    <div class="event-header">
      <h6 class="event-title">
        <i v-if="event.is_completed" class="bi bi-check-circle-fill text-success"></i>
        {{ event.title }}
      </h6>
      <span v-if="event.synced_to_ralendar" class="badge bg-success">
        <i class="bi bi-cloud-check"></i> 已同步
      </span>
      <span v-else-if="isLocal" class="badge bg-secondary">
        <i class="bi bi-laptop"></i> 本地
      </span>
    </div>
    
    <div v-if="event.description" class="event-description">
      {{ event.description }}
    </div>
    
    <div class="event-meta">
      <!-- 时间 -->
      <div v-if="event.eventTime || event.event_time" class="meta-item">
        <i class="bi bi-clock"></i>
        <span>{{ formatTime(event.eventTime || event.event_time) }}</span>
      </div>
      
      <!-- 地点 -->
      <div v-if="getLocationName()" class="meta-item">
        <i class="bi bi-geo-alt"></i>
        <span>{{ getLocationName() }}</span>
      </div>
      
      <!-- 提醒 -->
      <div v-if="getReminderInfo()" class="meta-item">
        <i class="bi bi-bell"></i>
        <span>{{ getReminderInfo() }}</span>
      </div>
    </div>
    
    <div class="event-actions">
      <!-- 查看日历（仅已同步到 Ralendar 的事件） -->
      <button 
        v-if="event.synced_to_ralendar"
        @click="viewInRalendar"
        class="btn btn-sm btn-outline-primary"
        title="在 Ralendar 中查看"
      >
        <i class="bi bi-calendar"></i> 日历
      </button>
      
      <!-- 导航（仅已同步且有地点的事件） -->
      <button 
        v-if="event.synced_to_ralendar && getLocationName()"
        @click="navigateInRalendar"
        class="btn btn-sm btn-outline-success"
        title="在 Ralendar 中导航"
      >
        <i class="bi bi-map"></i> 导航
      </button>
      
      <!-- 拉到云端（仅本地事项） -->
      <button 
        v-if="isLocal && isLoggedIn"
        @click="handleMoveToCloud"
        class="btn btn-sm btn-outline-info"
        title="转移到云端"
      >
        <i class="bi bi-cloud-upload"></i> 拉到云端
      </button>
      
      <!-- 编辑 -->
      <button 
        @click="handleEdit"
        class="btn btn-sm btn-outline-secondary"
        title="编辑"
      >
        <i class="bi bi-pencil"></i>
      </button>
      
      <!-- 删除 -->
      <button 
        @click="handleDelete"
        class="btn btn-sm btn-outline-danger"
        title="删除"
      >
        <i class="bi bi-trash"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  event: {
    type: Object,
    required: true
  },
  isLocal: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete', 'move-to-cloud'])

const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)

/**
 * 格式化时间
 */
const formatTime = (time) => {
  if (!time) return ''
  
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 获取地点名称
 */
const getLocationName = () => {
  if (props.event.location?.name) {
    return props.event.location.name
  }
  if (props.event.location_name) {
    return props.event.location_name
  }
  if (props.event.locationName) {
    return props.event.locationName
  }
  return ''
}

/**
 * 获取提醒信息
 */
const getReminderInfo = () => {
  const reminder = props.event.reminder
  if (!reminder || !reminder.enabled) return ''
  
  const method = reminder.method === 'email' ? '邮件' : '系统'
  return `${method}提醒`
}

/**
 * 在 Ralendar 中查看
 */
const viewInRalendar = () => {
  if (!props.event.ralendar_event_id) return
  
  // TODO: 替换为实际的 Ralendar 域名
  const url = `https://ralendar.com/calendar?event_id=${props.event.ralendar_event_id}`
  window.open(url, '_blank')
}

/**
 * 在 Ralendar 中导航
 */
const navigateInRalendar = () => {
  if (!props.event.ralendar_event_id) return
  
  // TODO: 替换为实际的 Ralendar 域名
  const url = `https://ralendar.com/map?event_id=${props.event.ralendar_event_id}`
  window.open(url, '_blank')
}

/**
 * 处理编辑
 */
const handleEdit = () => {
  emit('edit', props.event)
}

/**
 * 处理删除
 */
const handleDelete = () => {
  emit('delete', props.event)
}

/**
 * 处理转移到云端
 */
const handleMoveToCloud = () => {
  emit('move-to-cloud', props.event)
}
</script>

<style scoped>
.event-item {
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.event-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.event-completed {
  opacity: 0.7;
}

.event-completed .event-title {
  text-decoration: line-through;
  color: #6c757d;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 8px;
}

.event-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-description {
  color: #666;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.5;
}

.event-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.meta-item i {
  color: #999;
  font-size: 14px;
}

.event-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.badge {
  font-size: 12px;
  padding: 4px 8px;
  white-space: nowrap;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .event-item {
    padding: 12px;
  }
  
  .event-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .event-actions {
    width: 100%;
  }
  
  .event-actions button {
    flex: 1;
    min-width: 0;
  }
}
</style>
