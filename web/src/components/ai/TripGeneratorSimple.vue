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
          <label>天数：<input type="number" v-model.number="preferences.days" min="1" max="30" /></label>
          <label>预算：
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
          <button class="btn-sync-calendar" @click="syncToCalendar">🗓️ 同步到日历</button>
          <button class="btn-apply" @click="applyTrip">✅ 应用</button>
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
const emit = defineEmits(['apply', 'sync-to-calendar'])

const userPrompt = ref('')
const preferences = ref({ days: 5, budget_level: 'medium', travel_style: 'leisure' })
const isGenerating = ref(false)
const generatedTrip = ref(null)
const usageStats = ref(null)

const canGenerate = computed(() => userPrompt.value.trim().length >= 10)

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
    alert('请详细描述你的旅行想法（至少10个字）')
    return
  }

  isGenerating.value = true
  try {
    const response = await generateTripPlan({
      prompt: userPrompt.value,
      preferences: preferences.value
    })

    if (response.code === 200) {
      generatedTrip.value = response.data.trip_plan
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
  alert('✅ 已应用到行程')
}

const syncToCalendar = () => {
  emit('sync-to-calendar', generatedTrip.value)
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
  border-color: #667eea;
}

.preferences {
  margin-bottom: 20px;
}

.pref-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.pref-row label {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.pref-row input,
.pref-row select {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.btn-generate {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  border-top: 4px solid #667eea;
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

.btn-sync-calendar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}

.btn-sync-calendar:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  color: #667eea;
}

.activity p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}
</style>

