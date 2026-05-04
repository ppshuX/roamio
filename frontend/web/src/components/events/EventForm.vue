<template>
  <div class="event-form-modal" @click.self="handleClose">
    <div class="event-form-content">
      <div class="form-header">
        <h5>{{ isEdit ? '编辑事件' : '添加事件' }}</h5>
        <button @click="handleClose" class="btn-close" aria-label="关闭"></button>
      </div>
      
      <div class="form-body">
        <!-- 标题（必填） -->
        <div class="mb-3">
          <label class="form-label">
            事件标题 <span class="text-danger">*</span>
          </label>
          <input 
            v-model="form.title" 
            type="text" 
            class="form-control"
            :class="{ 'is-invalid': errors.title }"
            placeholder="例如：参观故宫"
            @input="clearError('title')"
          />
          <div v-if="errors.title" class="invalid-feedback">
            {{ errors.title }}
          </div>
        </div>
        
        <!-- 描述（选填） -->
        <div class="mb-3">
          <label class="form-label">事件描述</label>
          <textarea 
            v-model="form.description" 
            class="form-control"
            rows="3"
            placeholder="添加更多细节..."
          ></textarea>
        </div>
        
        <!-- 时间选择（选填） -->
        <div class="mb-3">
          <label class="form-label">事件时间</label>
          <input 
            v-model="form.eventTime" 
            type="datetime-local" 
            class="form-control"
          />
          <small v-if="form.eventTime && isLoggedIn" class="text-success">
            <i class="bi bi-check-circle"></i> 将同步到 Ralendar 日历
          </small>
        </div>
        
        <!-- 地点（选填，暂时文本输入） -->
        <div class="mb-3">
          <label class="form-label">地点</label>
          <input 
            v-model="form.locationName" 
            type="text" 
            class="form-control"
            placeholder="例如：故宫博物院"
          />
          <small class="text-muted">
            <i class="bi bi-info-circle"></i> 地图选点功能即将上线
          </small>
        </div>
        
        <!-- 提醒设置（仅登录用户） -->
        <div v-if="isLoggedIn && form.eventTime" class="mb-3">
          <div class="form-check form-switch">
            <input 
              v-model="form.reminderEnabled" 
              class="form-check-input" 
              type="checkbox"
              id="reminderSwitch"
            />
            <label class="form-check-label" for="reminderSwitch">
              启用提醒
            </label>
          </div>
          
          <div v-if="form.reminderEnabled" class="mt-2">
            <label class="form-label">提醒时间</label>
            <input 
              v-model="form.reminderTime" 
              type="datetime-local" 
              class="form-control"
            />
            
            <label class="form-label mt-2">提醒方式</label>
            <select v-model="form.reminderMethod" class="form-select">
              <option value="email">邮件提醒</option>
              <option value="system">系统通知</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="form-footer">
        <button @click="handleClose" class="btn btn-secondary">
          取消
        </button>
        
        <button 
          v-if="!isLoggedIn" 
          @click="saveToLocal" 
          class="btn btn-primary"
          :disabled="!form.title || saving"
        >
          <span v-if="saving">保存中...</span>
          <span v-else>
            <i class="bi bi-save"></i> 保存到本地
          </span>
        </button>
        
        <button 
          v-if="isLoggedIn" 
          @click="saveToCloud" 
          class="btn btn-success"
          :disabled="!form.title || saving"
        >
          <span v-if="saving">保存中...</span>
          <span v-else>
            <i class="bi bi-cloud-upload"></i> 保存到云端
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { createEvent, updateEvent } from '@/api/events'
import LocalEventStorage from '@/utils/localEventStorage'

const props = defineProps({
  tripId: {
    type: Number,
    required: true
  },
  event: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'close'])

const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)
const isEdit = computed(() => !!props.event)

const saving = ref(false)
const errors = ref({})

// 表单数据
const form = ref({
  title: props.event?.title || '',
  description: props.event?.description || '',
  eventTime: props.event?.eventTime || '',
  locationName: props.event?.location?.name || '',
  reminderEnabled: props.event?.reminder?.enabled || false,
  reminderTime: props.event?.reminder?.time || '',
  reminderMethod: props.event?.reminder?.method || 'email'
})

// 监听事件时间变化，自动设置提醒时间（提前30分钟）
watch(() => form.value.eventTime, (newTime) => {
  if (newTime && form.value.reminderEnabled && !form.value.reminderTime) {
    const eventDate = new Date(newTime)
    const reminderDate = new Date(eventDate.getTime() - 30 * 60000) // 提前30分钟
    form.value.reminderTime = reminderDate.toISOString().slice(0, 16)
  }
})

/**
 * 清除错误提示
 */
const clearError = (field) => {
  delete errors.value[field]
}

/**
 * 验证表单
 */
const validate = () => {
  errors.value = {}
  
  if (!form.value.title || form.value.title.trim() === '') {
    errors.value.title = '请输入事件标题'
    return false
  }
  
  if (form.value.reminderEnabled && !form.value.reminderTime) {
    errors.value.reminderTime = '启用提醒时必须设置提醒时间'
    return false
  }
  
  return true
}

/**
 * 保存到本地
 */
const saveToLocal = () => {
  if (!validate()) return
  
  saving.value = true
  
  try {
    const eventData = {
      tripId: props.tripId,
      title: form.value.title,
      description: form.value.description,
      eventTime: form.value.eventTime || null,
      location: {
        name: form.value.locationName,
        address: '',
        lat: null,
        lng: null
      },
      reminder: {
        enabled: false, // 本地事项不支持提醒
        time: null,
        method: 'email'
      }
    }
    
    if (isEdit.value && props.event.source === 'local') {
      // 更新本地事项
      LocalEventStorage.update(props.event.id, eventData)
    } else {
      // 添加新的本地事项
      LocalEventStorage.add(eventData)
    }
    
    emit('save', { ...eventData, source: 'local' })
    handleClose()
  } catch (error) {
    alert('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

/**
 * 保存到云端
 */
const saveToCloud = async () => {
  if (!validate()) return
  
  saving.value = true
  
  try {
    const eventData = {
      title: form.value.title,
      description: form.value.description,
      eventTime: form.value.eventTime || null,
      location: {
        name: form.value.locationName,
        address: '',
        lat: null,
        lng: null
      },
      reminder: {
        enabled: form.value.reminderEnabled,
        time: form.value.reminderTime || null,
        method: form.value.reminderMethod
      }
    }
    
    let result
    if (isEdit.value && props.event.source !== 'local') {
      // 更新云端事项
      result = await updateEvent(props.tripId, props.event.id, eventData)
    } else {
      // 创建新的云端事项
      result = await createEvent(props.tripId, eventData)
    }
    
    // 显示成功消息
    let message = '事件已保存'
    if (result.event_time) {
      message += '，已同步到日历'
    }
    if (result.reminder?.enabled) {
      message += '，提醒已设置'
    }
    
    alert(message)
    
    emit('save', result)
    handleClose()
  } catch (error) {
    alert('保存失败：' + (error.response?.data?.message || error.message))
  } finally {
    saving.value = false
  }
}

/**
 * 关闭表单
 */
const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.event-form-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 20px;
}

.event-form-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.form-header h5 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.form-body {
  padding: 24px;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 0 0 12px 12px;
}

.form-label {
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.text-danger {
  color: #dc3545;
}

.text-success {
  color: #198754;
  display: block;
  margin-top: 4px;
}

.text-muted {
  color: #6c757d;
  display: block;
  margin-top: 4px;
  font-size: 14px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .event-form-modal {
    padding: 0;
  }
  
  .event-form-content {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .form-header {
    padding: 16px 20px;
  }
  
  .form-body {
    padding: 20px;
  }
  
  .form-footer {
    padding: 12px 20px;
  }
}
</style>
