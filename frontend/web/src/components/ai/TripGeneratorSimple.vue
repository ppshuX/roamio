<template>
  <div class="ai-generator">
    <div v-if="!isGenerating && !generatedTrip" class="input-section">
      <h3>描述你的旅行计划</h3>
      <textarea
        v-model="userPrompt"
        placeholder="例如：我想去云南旅游5天，主要去大理和丽江，喜欢古城和自然风光，预算中等"
        rows="5"
      ></textarea>
      
      <div class="preferences">
        <div class="pref-row">
          <label>日期选择：</label>
          <div class="date-type-selector">
            <label class="radio-label">
              <input 
                type="radio" 
                name="dateType" 
                value="range" 
                v-model="dateType"
              />
              <span>日期范围</span>
            </label>
            <label class="radio-label">
              <input 
                type="radio" 
                name="dateType" 
                value="days" 
                v-model="dateType"
              />
              <span>天数</span>
            </label>
          </div>
        </div>
        
        <!-- 日期范围选择 -->
        <div v-if="dateType === 'range'" class="pref-row date-range-row">
          <label>
            <span>出发日期：</span>
            <input 
              type="date" 
              v-model="dateRange.start_date"
              :min="minDate"
            />
          </label>
          <label>
            <span>返回日期：</span>
            <input 
              type="date" 
              v-model="dateRange.end_date"
              :min="dateRange.start_date || minDate"
            />
          </label>
        </div>
        
        <!-- 天数选择 -->
        <div v-if="dateType === 'days'" class="pref-row">
          <label>
            <span>天数：</span>
            <input 
              type="number" 
              v-model.number="preferences.days" 
              min="1" 
              max="30"
            />
          </label>
        </div>
        
        <div class="pref-row">
          <label>
            <span>预算：</span>
            <select v-model="preferences.budget_level">
              <option value="low">经济型</option>
              <option value="medium">中等</option>
              <option value="high">舒适型</option>
            </select>
          </label>
        </div>
      </div>
      
      <button class="btn-generate" @click="generateTrip" :disabled="!canGenerate">
        ✨ AI 生成行程
      </button>
      <p v-if="usageStats" class="usage-info">
        今日剩余: {{ usageStats.remaining }}/{{ usageStats.limit }} 次
      </p>
    </div>

    <div v-if="isGenerating" class="generating">
      <div class="spinner"></div>
      <p>AI 正在生成中...（约 30 秒）</p>
    </div>

    <div v-if="generatedTrip" class="preview">
      <div class="preview-header">
        <h3>{{ generatedTrip.trip_title }}</h3>
        <div>
          <button class="btn-apply" @click="applyTrip">✅ 应用到行程</button>
          <button class="btn-regenerate" @click="regenerate">🔄 重新生成</button>
        </div>
      </div>
      
      <p class="summary">{{ generatedTrip.summary }}</p>
      
      <div class="days">
        <div v-for="day in generatedTrip.days_detail" :key="day.day_number" class="day-card">
          <h4>{{ day.title }}</h4>
          <div v-for="(act, idx) in day.activities" :key="idx" class="activity">
            <strong>{{ act.time }} - {{ act.location }}</strong>
            <p>{{ act.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { generateTripPlan, getUsageStats } from '@/api/ai'

// eslint-disable-next-line no-undef
const emit = defineEmits(['apply'])

const userPrompt = ref('')
const dateType = ref('days') // 'range' 或 'days'
const dateRange = ref({
  start_date: '',
  end_date: ''
})
const preferences = ref({ days: 5, budget_level: 'medium', travel_style: 'leisure' })
const isGenerating = ref(false)
const generatedTrip = ref(null)
const usageStats = ref(null)

// 最小日期（今天）
const today = new Date()
const year = today.getFullYear()
const month = String(today.getMonth() + 1).padStart(2, '0')
const day = String(today.getDate()).padStart(2, '0')
const minDate = `${year}-${month}-${day}`

// 计算天数（从日期范围）
const calculatedDays = computed(() => {
  if (dateType.value === 'range' && dateRange.value.start_date && dateRange.value.end_date) {
    const start = new Date(dateRange.value.start_date)
    const end = new Date(dateRange.value.end_date)
    const diffTime = Math.abs(end - start)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1 // 包含首尾两天
    return diffDays > 0 ? diffDays : 1
  }
  return preferences.value.days || 5
})

const canGenerate = computed(() => {
  if (userPrompt.value.trim().length < 10) return false
  
  // 如果选择日期范围，必须选择开始和结束日期
  if (dateType.value === 'range') {
    return dateRange.value.start_date && dateRange.value.end_date
  }
  
  // 如果选择天数，必须大于0
  return preferences.value.days > 0
})

const loadUsageStats = async () => {
  try {
    const response = await getUsageStats()
    if (response.code === 200) usageStats.value = response.data
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const generateTrip = async () => {
  if (!canGenerate.value) {
    if (userPrompt.value.trim().length < 10) {
      alert('请详细描述你的旅行想法（至少10个字）')
    } else if (dateType.value === 'range' && (!dateRange.value.start_date || !dateRange.value.end_date)) {
      alert('请选择出发日期和返回日期')
    } else if (dateType.value === 'days' && preferences.value.days <= 0) {
      alert('请选择有效的天数')
    }
    return
  }

  isGenerating.value = true
  try {
    // 构建偏好设置，包含日期信息
    const prefs = {
      ...preferences.value,
      days: calculatedDays.value
    }
    
    // 如果选择日期范围，添加到偏好设置中
    if (dateType.value === 'range') {
      prefs.date_range = {
        start_date: dateRange.value.start_date,
        end_date: dateRange.value.end_date
      }
    }
    
    const response = await generateTripPlan({
      prompt: userPrompt.value,
      preferences: prefs
    })

    if (response.code === 200) {
      const tripPlan = response.data.trip_plan
      
      // 如果选择日期范围，将日期信息添加到生成的行程中
      if (dateType.value === 'range' && dateRange.value.start_date && dateRange.value.end_date) {
        tripPlan.date_range = {
          start_date: dateRange.value.start_date,
          end_date: dateRange.value.end_date
        }
        tripPlan.date_type = 'range'
        // 更新每一天的日期
        if (tripPlan.days_detail && tripPlan.days_detail.length > 0) {
          const start = new Date(dateRange.value.start_date)
          tripPlan.days_detail.forEach((dayItem, index) => {
            const currentDate = new Date(start)
            currentDate.setDate(start.getDate() + index)
            const year = currentDate.getFullYear()
            const month = String(currentDate.getMonth() + 1).padStart(2, '0')
            const dayNum = String(currentDate.getDate()).padStart(2, '0')
            dayItem.date = `${year}-${month}-${dayNum}`
          })
        }
      } else {
        tripPlan.date_type = 'days'
        tripPlan.days = calculatedDays.value
      }
      
      generatedTrip.value = tripPlan
      alert('✅ 行程生成成功！')
      await loadUsageStats()
    } else {
      throw new Error(response.message || '生成失败')
    }
  } catch (error) {
    console.error('生成失败:', error)
    if (error.response?.status === 429) {
      alert('❌ 今日生成次数已用完')
    } else {
      alert('❌ ' + (error.response?.data?.message || '生成失败'))
    }
  } finally {
    isGenerating.value = false
  }
}

const applyTrip = () => {
  emit('apply', generatedTrip.value)
  alert('✅ 已应用到行程，你可以在编辑页面继续完善，然后同步到 Ralendar 日历')
}

const regenerate = () => {
  generatedTrip.value = null
}

onMounted(() => {
  loadUsageStats()
})
</script>

<style scoped>
.ai-generator {
  padding: 20px;
}

.input-section h3 {
  margin-bottom: 15px;
  color: #333;
}

.input-section textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 20px;
  font-family: inherit;
}

.input-section textarea:focus {
  outline: none;
  border-color: var(--roamio-primary);
}

.preferences {
  margin-bottom: 20px;
}

.pref-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  align-items: center;
}

.pref-row > label:first-child {
  min-width: 80px;
  font-weight: 600;
  color: #333;
}

.date-type-selector {
  display: flex;
  gap: 20px;
  flex: 1;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex: 1;
}

.radio-label input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.radio-label span {
  font-size: 14px;
  color: #666;
}

.date-range-row {
  margin-left: 80px;
  margin-top: 10px;
}

.date-range-row label {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.date-range-row label span {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.pref-row label {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.pref-row label span {
  min-width: 60px;
  font-weight: 500;
  color: #666;
}

.pref-row input[type="number"],
.pref-row input[type="date"],
.pref-row select {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.pref-row input[type="date"] {
  cursor: pointer;
}

.pref-row input:focus,
.pref-row select:focus {
  outline: none;
  border-color: var(--roamio-primary);
}

.btn-generate {
  width: 100%;
  padding: 15px;
  background: var(--roamio-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-generate:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.usage-info {
  text-align: center;
  margin-top: 10px;
  color: #999;
  font-size: 13px;
}

.generating {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--roamio-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.preview-header h3 {
  margin: 0;
  color: #333;
}

.preview-header button {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-left: 10px;
}

.btn-apply {
  background: #67c23a;
  color: white;
}

.btn-regenerate {
  background: #f0f0f0;
  color: #666;
}

.summary {
  padding: 20px;
  background: var(--roamio-primary);
  color: white;
  border-radius: 10px;
  margin-bottom: 20px;
}

.day-card {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 15px;
}

.day-card h4 {
  margin-bottom: 15px;
  color: #333;
}

.activity {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.activity strong {
  display: block;
  margin-bottom: 5px;
  color: var(--roamio-primary);
}

.activity p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}
</style>

