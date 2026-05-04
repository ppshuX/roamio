<template>
  <div class="date-picker-modal-overlay" @click.self="$emit('close')">
    <div class="date-picker-modal">
      <div class="modal-header">
        <h3>📅 选择出发日期</h3>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>
      
      <div class="modal-body">
        <p class="description">
          请选择旅行的出发日期，系统将根据此日期计算每天的行程安排。
        </p>
        
        <div class="form-group">
          <label>出发日期 *</label>
          <input 
            type="date" 
            v-model="selectedDate"
            :min="minDate"
            required
          />
          <small class="help-text">选择旅行开始的第一天</small>
        </div>
        
        <div v-if="selectedDate" class="date-preview">
          <p class="preview-title">📅 行程预览：</p>
          <div class="preview-days">
            <div 
              v-for="(day, index) in previewDays" 
              :key="index"
              class="preview-day"
            >
              <span class="day-label">第 {{ index + 1 }} 天</span>
              <span class="day-date">{{ formatDate(day) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">取消</button>
        <button 
          class="btn-confirm" 
          @click="handleConfirm"
          :disabled="!selectedDate"
        >
          确认
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'DatePickerModal',
  
  props: {
    days: {
      type: Number,
      default: 3
    },
    defaultDate: {
      type: String,
      default: null
    }
  },
  
  emits: ['confirm', 'close'],
  
  setup(props, { emit }) {
    // 最小日期（今天）
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    const minDate = `${year}-${month}-${day}`
    
    // 默认选择今天或传入的日期
    const selectedDate = ref(props.defaultDate || minDate)
    
    // 预览天数
    const previewDays = computed(() => {
      if (!selectedDate.value) return []
      
      const days = []
      const start = new Date(selectedDate.value)
      
      for (let i = 0; i < props.days; i++) {
        const current = new Date(start)
        current.setDate(start.getDate() + i)
        days.push(current)
      }
      
      return days
    })
    
    const formatDate = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      const weekday = weekdays[date.getDay()]
      return `${year}-${month}-${day} ${weekday}`
    }
    
    const handleConfirm = () => {
      if (!selectedDate.value) {
        alert('请选择出发日期')
        return
      }
      
      emit('confirm', selectedDate.value)
    }
    
    return {
      minDate,
      selectedDate,
      previewDays,
      formatDate,
      handleConfirm
    }
  }
}
</script>

<style scoped>
.date-picker-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10001;
}

.date-picker-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
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

.modal-body {
  padding: 20px;
}

.description {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
  line-height: 1.6;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.form-group input[type="date"] {
  width: 100%;
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-group input[type="date"]:focus {
  outline: none;
  border-color: #667eea;
}

.help-text {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.date-preview {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9ff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.preview-title {
  margin: 0 0 12px 0;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.preview-days {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-day {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  font-size: 14px;
}

.day-label {
  color: #667eea;
  font-weight: 600;
}

.day-date {
  color: #666;
}

.modal-footer {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

