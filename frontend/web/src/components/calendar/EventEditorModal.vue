<template>
  <div class="event-editor-modal-overlay" @click.self="$emit('close')">
    <div class="event-editor-modal">
      <div class="modal-header">
        <h3>✏️ 编辑行程</h3>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label>标题 *</label>
          <input 
            type="text" 
            v-model="localEvent.title" 
            placeholder="行程标题"
            maxlength="50"
          />
          <span class="char-count">{{ localEvent.title.length }}/50</span>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>日期 *</label>
            <input 
              type="date" 
              v-model="eventDate"
              required
            />
          </div>
          <div class="form-group">
            <label>开始时间 *</label>
            <input 
              type="time" 
              v-model="startTime"
              required
            />
          </div>
          <div class="form-group">
            <label>结束时间 *</label>
            <input 
              type="time" 
              v-model="endTime"
              required
            />
          </div>
        </div>
        
        <div class="form-group">
          <label>地点 *</label>
          <input 
            type="text" 
            v-model="location" 
            placeholder="例如：故宫博物院（北京市东城区景山前街4号）"
          />
          <small class="help-text">可输入地点名称，或包含详细地址。完整地址有助于地图导航和提醒定位</small>
        </div>
        
        <div class="form-group">
          <label>地点类型</label>
          <select v-model="localEvent.location_type">
            <option value="">未分类</option>
            <option value="景点">景点</option>
            <option value="餐厅">餐厅</option>
            <option value="住宿">住宿</option>
            <option value="交通">交通</option>
            <option value="购物">购物</option>
            <option value="娱乐">娱乐</option>
            <option value="其他">其他</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>描述</label>
          <textarea 
            v-model="localEvent.description" 
            placeholder="行程描述（可选）"
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>提醒时间</label>
            <select v-model.number="localEvent.reminder_minutes">
              <option :value="5">提前 5 分钟</option>
              <option :value="10">提前 10 分钟</option>
              <option :value="15">提前 15 分钟</option>
              <option :value="30">提前 30 分钟</option>
              <option :value="60">提前 1 小时</option>
              <option :value="120">提前 2 小时</option>
            </select>
          </div>
          <div class="form-group">
            <label>邮件提醒</label>
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="localEvent.email_reminder"
              />
              <span>启用邮件提醒</span>
            </label>
          </div>
        </div>
        
        <div class="form-group">
          <label>地理坐标（可选）</label>
          <div class="coordinates-input">
              <div class="coord-input">
                <label>纬度:</label>
                <input 
                  type="number" 
                  v-model.number="localEvent.latitude" 
                  step="0.000001"
                  placeholder="39.9163"
                />
              </div>
              <div class="coord-input">
                <label>经度:</label>
                <input 
                  type="number" 
                  v-model.number="localEvent.longitude" 
                  step="0.000001"
                  placeholder="116.3972"
                />
              </div>
              <button 
                class="btn-get-coords" 
                @click="showMapPicker = true"
                type="button"
              >
                🗺️ 地图选点
              </button>
            </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">取消</button>
        <button class="btn-save" @click="handleSave">保存</button>
      </div>
    </div>
    
    <!-- 地图选择器 -->
    <MapPicker 
      :show="showMapPicker"
      :default-location="location"
      @select="handleMapSelect"
      @close="showMapPicker = false"
    />
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import MapPicker from '@/components/map/MapPicker.vue'

export default {
  name: 'EventEditorModal',
  
  components: {
    MapPicker
  },
  
  props: {
    event: {
      type: Object,
      required: true
    }
  },
  
  emits: ['save', 'close'],
  
  setup(props, { emit }) {
    // 地图选择器
    const showMapPicker = ref(false)
    
    // 创建本地副本，避免直接修改 props
    const localEvent = ref({
      title: props.event.title || '',
      description: props.event.description || '',
      location: props.event.location || props.event.location_name || '',
      location_name: props.event.location_name || props.event.location || '',
      location_address: props.event.location_address || null,
      location_type: props.event.location_type || null,
      start_time: props.event.start_time || '',
      end_time: props.event.end_time || '',
      latitude: props.event.latitude || null,
      longitude: props.event.longitude || null,
      reminder_minutes: props.event.reminder_minutes || 30,
      email_reminder: props.event.email_reminder !== undefined ? props.event.email_reminder : true
    })
    
    // 统一的地点字段（合并地点名称和详细地址）
    const location = computed({
      get: () => {
        // 优先使用 location 字段
        if (localEvent.value.location) {
          return localEvent.value.location
        }
        // 如果有 location_name 和 location_address，合并它们
        if (localEvent.value.location_name) {
          if (localEvent.value.location_address) {
            return `${localEvent.value.location_name}（${localEvent.value.location_address}）`
          }
          return localEvent.value.location_name
        }
        return ''
      },
      set: (value) => {
        localEvent.value.location = value || ''
        
        // 尝试从 location 中提取 location_name 和 location_address
        // 格式：地点名称（详细地址）
        const match = value.match(/^(.+?)（([^）]+)）$/)
        if (match) {
          localEvent.value.location_name = match[1].trim()
          localEvent.value.location_address = match[2].trim()
        } else {
          // 如果没有括号，整个字符串作为地点名称
          localEvent.value.location_name = value.trim()
          localEvent.value.location_address = null
        }
      }
    })
    
    // 日期和时间分离处理
    const eventDate = computed({
      get: () => {
        if (!localEvent.value.start_time) return ''
        const date = new Date(localEvent.value.start_time)
        return date.toISOString().split('T')[0]
      },
      set: (value) => {
        if (!value) return
        const startTime = localEvent.value.start_time ? new Date(localEvent.value.start_time) : new Date()
        const [year, month, day] = value.split('-')
        startTime.setFullYear(parseInt(year))
        startTime.setMonth(parseInt(month) - 1)
        startTime.setDate(parseInt(day))
        localEvent.value.start_time = startTime.toISOString().replace('Z', '+08:00')
        
        // 同时更新结束时间
        if (localEvent.value.end_time) {
          const endTime = new Date(localEvent.value.end_time)
          endTime.setFullYear(parseInt(year))
          endTime.setMonth(parseInt(month) - 1)
          endTime.setDate(parseInt(day))
          localEvent.value.end_time = endTime.toISOString().replace('Z', '+08:00')
        }
      }
    })
    
    const startTime = computed({
      get: () => {
        if (!localEvent.value.start_time) return ''
        const date = new Date(localEvent.value.start_time)
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        return `${hours}:${minutes}`
      },
      set: (value) => {
        if (!value) return
        const [hours, minutes] = value.split(':')
        const date = new Date(localEvent.value.start_time || new Date())
        date.setHours(parseInt(hours))
        date.setMinutes(parseInt(minutes))
        date.setSeconds(0)
        localEvent.value.start_time = date.toISOString().replace('Z', '+08:00')
      }
    })
    
    const endTime = computed({
      get: () => {
        if (!localEvent.value.end_time) return ''
        const date = new Date(localEvent.value.end_time)
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        return `${hours}:${minutes}`
      },
      set: (value) => {
        if (!value) return
        const [hours, minutes] = value.split(':')
        const date = new Date(localEvent.value.end_time || localEvent.value.start_time || new Date())
        date.setHours(parseInt(hours))
        date.setMinutes(parseInt(minutes))
        date.setSeconds(0)
        localEvent.value.end_time = date.toISOString().replace('Z', '+08:00')
      }
    })
    
    // 监听 props 变化，更新本地副本
    watch(() => props.event, (newEvent) => {
      // 合并地点信息
      let locationValue = newEvent.location || newEvent.location_name || ''
      if (newEvent.location_name && newEvent.location_address) {
        locationValue = `${newEvent.location_name}（${newEvent.location_address}）`
      } else if (newEvent.location_name) {
        locationValue = newEvent.location_name
      }
      
      localEvent.value = {
        title: newEvent.title || '',
        description: newEvent.description || '',
        location: locationValue,
        location_name: newEvent.location_name || newEvent.location || '',
        location_address: newEvent.location_address || null,
        location_type: newEvent.location_type || null,
        start_time: newEvent.start_time || '',
        end_time: newEvent.end_time || '',
        latitude: newEvent.latitude || null,
        longitude: newEvent.longitude || null,
        reminder_minutes: newEvent.reminder_minutes || 30,
        email_reminder: newEvent.email_reminder !== undefined ? newEvent.email_reminder : true
      }
    }, { deep: true })
    
    const handleSave = () => {
      // 验证必填字段
      if (!localEvent.value.title || !localEvent.value.location || !localEvent.value.start_time || !localEvent.value.end_time) {
        alert('请填写所有必填字段（标题、地点、开始时间、结束时间）')
        return
      }
      
      // 确保 location_name 字段存在（用于兼容）
      if (!localEvent.value.location_name && localEvent.value.location) {
        // 从 location 中提取 location_name
        const match = localEvent.value.location.match(/^(.+?)（([^）]+)）$/)
        if (match) {
          localEvent.value.location_name = match[1].trim()
          localEvent.value.location_address = match[2].trim()
        } else {
          localEvent.value.location_name = localEvent.value.location.trim()
        }
      }
      
      // 验证时间
      const start = new Date(localEvent.value.start_time)
      const end = new Date(localEvent.value.end_time)
      
      if (end <= start) {
        alert('结束时间必须晚于开始时间')
        return
      }
      
      // 发送保存事件
      emit('save', { ...localEvent.value })
    }
    
    // 处理地图选点
    const handleMapSelect = (mapLocation) => {
      // 更新坐标
      localEvent.value.latitude = mapLocation.lat
      localEvent.value.longitude = mapLocation.lng
      
      // 如果用户还没有输入地点，使用地图返回的地点名称
      if (!location.value || !location.value.trim()) {
        location.value = mapLocation.name
      }
      
      showMapPicker.value = false
    }
    
    return {
      localEvent,
      location,
      eventDate,
      startTime,
      endTime,
      handleSave,
      showMapPicker,
      handleMapSelect
    }
  }
}
</script>

<style scoped>
.event-editor-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.event-editor-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
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
  overflow-y: auto;
  flex: 1;
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

.form-group input[type="text"],
.form-group input[type="date"],
.form-group input[type="time"],
.form-group input[type="number"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.help-text {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  font-style: italic;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

.coordinates-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.coord-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.coord-input label {
  min-width: 50px;
  margin-bottom: 0;
}

.coord-input input {
  flex: 1;
}

.btn-get-coords {
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-start;
}

.btn-get-coords:hover {
  background: #5568d3;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-cancel,
.btn-save {
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

.btn-save {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
</style>

