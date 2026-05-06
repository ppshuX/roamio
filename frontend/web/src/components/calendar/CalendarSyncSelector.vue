<template>
  <div class="calendar-sync-selector">
    <div class="selector-header">
      <h3>🗓️ 选择要同步到日历的行程</h3>
      <button class="btn-close" @click="$emit('close')">✕</button>
    </div>
    
    <div class="selector-body">
      <!-- 全选控制 -->
      <div class="select-all">
        <label>
          <input 
            type="checkbox" 
            :checked="allSelected" 
            :indeterminate="someSelected"
            @change="toggleSelectAll"
          />
          <span class="select-all-text">
            {{ allSelected ? '取消全选' : '全选' }} 
            (已选择 {{ selectedCount }} / {{ initializedEvents.length }} 个行程)
          </span>
        </label>
      </div>
      
      <!-- 行程列表 -->
      <div class="events-list">
        <div 
          v-for="(event, index) in initializedEvents" 
          :key="index" 
          class="event-item"
          :class="{ 'selected': event.selected }"
        >
          <div class="event-checkbox">
            <input 
              type="checkbox" 
              :checked="event.selected" 
              @change="toggleEvent(index)"
            />
          </div>
          
          <div class="event-content">
            <div class="event-header">
              <h4>{{ event.title }}</h4>
              <button 
                class="btn-edit" 
                @click="editEvent(index)"
                :disabled="!event.selected"
              >
                ✏️ 编辑
              </button>
            </div>
            
            <div class="event-details">
              <div class="detail-row">
                <span class="detail-label">📅 日期:</span>
                <span class="detail-value">{{ formatDate(event.start_time) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">⏰ 时间:</span>
                <span class="detail-value">
                  {{ formatTime(event.start_time) }} - {{ formatTime(event.end_time) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">📍 地点:</span>
                <span class="detail-value">
                  <strong>{{ event.location_name || event.location }}</strong>
                  <span v-if="event.location_address" class="address-text">（{{ event.location_address }}）</span>
                  <span v-if="event.location_type" class="location-type-badge">{{ event.location_type }}</span>
                </span>
              </div>
              <div v-if="event.latitude && event.longitude" class="detail-row">
                <span class="detail-label">🗺️ 坐标:</span>
                <span class="detail-value">
                  {{ event.latitude.toFixed(6) }}, {{ event.longitude.toFixed(6) }}
                  <button class="btn-map" @click="viewOnMap(event)" title="查看地图">🗺️</button>
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">🔔 提醒:</span>
                <span class="detail-value">提前 {{ event.reminder_minutes }} 分钟</span>
              </div>
              <div v-if="event.description" class="detail-row">
                <span class="detail-label">📝 描述:</span>
                <span class="detail-value">{{ truncate(event.description, 50) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="initializedEvents.length === 0" class="empty-state">
        <p>暂无行程可同步</p>
      </div>
    </div>
    
    <div class="selector-footer">
      <button class="btn-cancel" @click="$emit('close')">取消</button>
      <button 
        class="btn-confirm" 
        @click="handleConfirm"
        :disabled="selectedCount === 0 || syncing"
      >
        <span v-if="!syncing">✅ 确认同步 ({{ selectedCount }} 个)</span>
        <span v-else>⏳ 同步中...</span>
      </button>
    </div>
    
    <!-- 编辑弹窗 -->
            <EventEditorModal
      v-if="editingIndex !== null && initializedEvents[editingIndex]"
      :event="initializedEvents[editingIndex]"
      @save="handleSaveEvent"
      @close="editingIndex = null"
    />
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import EventEditorModal from './EventEditorModal.vue'

export default {
  name: 'CalendarSyncSelector',
  
  components: {
    EventEditorModal
  },
  
  props: {
    events: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  
  emits: ['close', 'confirm'],
  
  setup(props, { emit }) {
    const syncing = ref(false)
    const editingIndex = ref(null)
    
    // 初始化：所有事件默认选中
    const initializedEvents = ref(
      props.events.map(event => ({
        ...event,
        selected: true
      }))
    )
    
    // 计算属性
    const selectedCount = computed(() => {
      return initializedEvents.value.filter(e => e.selected).length
    })
    
    const allSelected = computed(() => {
      return initializedEvents.value.length > 0 && 
             initializedEvents.value.every(e => e.selected)
    })
    
    const someSelected = computed(() => {
      return selectedCount.value > 0 && selectedCount.value < initializedEvents.value.length
    })
    
    // 方法
    const toggleSelectAll = () => {
      const select = !allSelected.value
      initializedEvents.value.forEach(event => {
        event.selected = select
      })
    }
    
    const toggleEvent = (index) => {
      initializedEvents.value[index].selected = !initializedEvents.value[index].selected
    }
    
    const editEvent = (index) => {
      editingIndex.value = index
    }
    
    const handleSaveEvent = (updatedEvent) => {
      if (editingIndex.value !== null) {
        initializedEvents.value[editingIndex.value] = {
          ...updatedEvent,
          selected: initializedEvents.value[editingIndex.value].selected
        }
      }
      editingIndex.value = null
    }
    
    const handleConfirm = async () => {
      const selectedEvents = initializedEvents.value.filter(e => e.selected)
      
      if (selectedEvents.length === 0) {
        alert('请至少选择一个行程')
        return
      }
      
      syncing.value = true
      try {
        emit('confirm', selectedEvents)
      } finally {
        syncing.value = false
      }
    }
    
    const formatDate = (isoString) => {
      if (!isoString) return '未设置'
      const date = new Date(isoString)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
    
    const formatTime = (isoString) => {
      if (!isoString) return '未设置'
      // 直接从 ISO 字符串中提取时间，避免时区转换问题
      // 格式：2025-11-15T09:00:00+08:00
      const match = isoString.match(/T(\d{2}):(\d{2}):\d{2}/)
      if (match) {
        return `${match[1]}:${match[2]}`
      }
      // 如果格式不匹配，回退到 Date 解析
      const date = new Date(isoString)
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${hours}:${minutes}`
    }
    
    const truncate = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }
    
    const viewOnMap = (event) => {
      if (event.latitude && event.longitude) {
        // 打开百度地图或高德地图（根据坐标）
        const mapUrl = `https://api.map.baidu.com/marker?location=${event.latitude},${event.longitude}&title=${encodeURIComponent(event.location_name || event.location)}&content=${encodeURIComponent(event.location_address || '')}&output=html&src=roamio`
        window.open(mapUrl, '_blank')
      }
    }
    
    // 监听 props.events 变化，更新内部状态
    watch(() => props.events, (newEvents) => {
      if (newEvents && newEvents.length > 0) {
        initializedEvents.value = newEvents.map(event => ({
          ...event,
          selected: event.selected !== undefined ? event.selected : true
        }))
      }
    }, { immediate: true, deep: true })
    
    return {
      syncing,
      editingIndex,
      initializedEvents,
      selectedCount,
      allSelected,
      someSelected,
      toggleSelectAll,
      toggleEvent,
      editEvent,
      handleSaveEvent,
      handleConfirm,
      formatDate,
      formatTime,
      truncate,
      viewOnMap
    }
  }
}
</script>

<style scoped>
.calendar-sync-selector {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.selector-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selector-header h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #f5f5f5;
  color: #333;
}

.selector-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.select-all {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.select-all label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  color: #333;
}

.select-all input[type="checkbox"] {
  margin-right: 10px;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.select-all-text {
  font-size: 16px;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.event-item {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  gap: 15px;
  transition: all 0.2s;
}

.event-item:hover {
  border-color: var(--roamio-primary);
  box-shadow: 0 2px 8px rgba(var(--bs-primary-rgb), 0.1);
}

.event-item.selected {
  border-color: var(--roamio-primary);
  background: #f8f9ff;
}

.event-checkbox {
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.event-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.event-content {
  flex: 1;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.event-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.btn-edit {
  background: var(--roamio-primary);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit:hover:not(:disabled) {
  background: var(--roamio-primary-hover);
  transform: translateY(-1px);
}

.btn-edit:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.event-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  font-size: 14px;
}

.detail-label {
  color: #666;
  min-width: 60px;
  font-weight: 500;
}

.detail-value {
  color: #333;
  flex: 1;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.address-text {
  color: #666;
  font-size: 13px;
}

.location-type-badge {
  display: inline-block;
  background: var(--roamio-primary);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.btn-map {
  background: #f0f0f0;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 8px;
}

.btn-map:hover {
  background: var(--roamio-primary);
  color: white;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.selector-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-cancel,
.btn-confirm {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-confirm {
  background: var(--roamio-primary);
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--bs-primary-rgb), 0.3);
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 滚动条样式 */
.selector-body::-webkit-scrollbar {
  width: 6px;
}

.selector-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.selector-body::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.selector-body::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>

