<template>
  <div class="ai-trip-generator">
    <!-- 头部 -->
    <div class="generator-header">
      <h2>🤖 AI 智能生成行程</h2>
      <p class="subtitle">告诉我你的旅行想法，AI 为你规划完美行程</p>
    </div>

    <!-- 输入区 -->
    <div v-if="!isGenerating && !generatedTrip" class="input-section">
      <!-- 描述输入 -->
      <div class="prompt-area">
        <label>描述你的旅行计划 *</label>
        <textarea
          v-model="userPrompt"
          placeholder="例如：我想去云南旅游5天，主要去大理和丽江，喜欢古城和自然风光，预算中等。希望节奏不要太紧张，每天2-3个景点就好。"
          rows="6"
          maxlength="2000"
        ></textarea>
        <div class="char-count">{{ userPrompt.length }}/2000</div>
      </div>

      <!-- 偏好设置 -->
      <div class="preferences">
        <h3>偏好设置（可选）</h3>
        <div class="pref-grid">
          <div class="pref-item">
            <label>旅行天数</label>
            <input
              type="number"
              v-model.number="preferences.days"
              min="1"
              max="30"
              placeholder="5"
            />
          </div>

          <div class="pref-item">
            <label>预算等级</label>
            <select v-model="preferences.budget_level">
              <option value="low">经济型 (¥200-300/天)</option>
              <option value="medium">中等 (¥400-600/天)</option>
              <option value="high">舒适型 (¥800-1200/天)</option>
            </select>
          </div>

          <div class="pref-item">
            <label>旅行风格</label>
            <select v-model="preferences.travel_style">
              <option value="leisure">休闲放松</option>
              <option value="adventure">探险刺激</option>
              <option value="culture">文化深度</option>
              <option value="food">美食之旅</option>
              <option value="photography">摄影采风</option>
            </select>
          </div>

          <div class="pref-item">
            <label>出发日期</label>
            <input
              type="date"
              v-model="preferences.start_date"
              :min="today"
            />
          </div>
        </div>
      </div>

      <!-- 生成按钮 -->
      <div class="action-buttons">
        <button
          class="btn-generate"
          @click="generateTrip"
          :disabled="!canGenerate"
        >
          ✨ AI 生成行程
        </button>
        <div v-if="usageStats" class="usage-info">
          今日剩余次数: {{ usageStats.remaining }}/{{ usageStats.limit }}
        </div>
      </div>
    </div>

    <!-- 生成中 -->
    <div v-if="isGenerating" class="generating">
      <div class="loading-spinner"></div>
      <p>AI 正在为你规划行程...</p>
      <p class="loading-tips">预计需要 3-5 秒</p>
    </div>

    <!-- 预览区 -->
    <div v-if="generatedTrip" class="preview-section">
      <div class="preview-header">
        <h3>📋 生成的行程预览</h3>
        <div class="preview-actions">
          <button @click="applyTrip" class="btn-apply">✅ 应用到行程</button>
          <button @click="regenerate" class="btn-secondary">🔄 重新生成</button>
        </div>
      </div>

      <!-- 行程概览 -->
      <div class="trip-summary">
        <h4>{{ generatedTrip.trip_title }}</h4>
        <p>{{ generatedTrip.summary }}</p>
        <div class="trip-meta">
          <span>📍 {{ generatedTrip.destination }}</span>
          <span>📅 {{ generatedTrip.days }}天</span>
          <span>💰 预算约 ¥{{ generatedTrip.total_budget }}</span>
        </div>
      </div>

      <!-- 每日行程 -->
      <div class="days-list">
        <div
          v-for="day in generatedTrip.days_detail"
          :key="day.day_number"
          class="day-card"
        >
          <div class="day-header">
            <h5>{{ day.title }}</h5>
            <span class="day-date">{{ day.date }}</span>
          </div>
          
          <div class="activities">
            <div
              v-for="(activity, idx) in day.activities"
              :key="idx"
              class="activity-item"
            >
              <div class="activity-time">{{ activity.time }}</div>
              <div class="activity-content">
                <strong>{{ activity.location }}</strong>
                <p>{{ activity.description }}</p>
                <div class="activity-meta">
                  <span>⏱️ {{ activity.duration }}</span>
                  <span>💰 ¥{{ activity.estimated_cost }}</span>
                </div>
                <div v-if="activity.tips" class="activity-tips">
                  💡 {{ activity.tips }}
                </div>
              </div>
            </div>
          </div>

          <div class="day-total">
            当日预算: ¥{{ day.day_total }}
          </div>
        </div>
      </div>

      <!-- 旅行建议 -->
      <div v-if="generatedTrip.travel_tips" class="travel-tips">
        <h4>💡 旅行建议</h4>
        <ul>
          <li v-for="(tip, idx) in generatedTrip.travel_tips" :key="idx">
            {{ tip }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { generateTripPlan, getUsageStats } from '@/api/ai'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  // 可以接收初始参数
})

// Emits
const emit = defineEmits(['apply'])

// 数据
const userPrompt = ref('')
const preferences = ref({
  days: 5,
  budget_level: 'medium',
  travel_style: 'leisure',
  start_date: ''
})

const isGenerating = ref(false)
const generatedTrip = ref(null)
const usageStats = ref(null)

// 计算属性
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const canGenerate = computed(() => {
  return userPrompt.value.trim().length >= 10
})

// 方法
const loadUsageStats = async () => {
  try {
    const response = await getUsageStats()
    if (response.code === 200) {
      usageStats.value = response.data
    }
  } catch (error) {
    console.error('加载使用统计失败:', error)
  }
}

const generateTrip = async () => {
  if (!canGenerate.value) {
    ElMessage.warning('请详细描述你的旅行想法（至少10个字）')
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
      ElMessage.success('行程生成成功！')
      
      // 更新使用统计
      await loadUsageStats()
    } else {
      throw new Error(response.message || '生成失败')
    }
  } catch (error) {
    console.error('生成失败:', error)
    
    if (error.response?.status === 429) {
      ElMessage.error('今日生成次数已用完，请明天再试')
    } else if (error.response?.status === 401) {
      ElMessage.error('请先登录')
    } else {
      ElMessage.error(error.response?.data?.message || '生成失败，请重试')
    }
  } finally {
    isGenerating.value = false
  }
}

const applyTrip = () => {
  // 将生成的行程应用到创建表单
  emit('apply', generatedTrip.value)
  ElMessage.success('已应用到行程，你可以继续编辑')
}

const regenerate = () => {
  generatedTrip.value = null
  ElMessage.info('请重新描述你的旅行想法')
}

// 生命周期
onMounted(() => {
  loadUsageStats()
})
</script>

<style scoped lang="scss">
.ai-trip-generator {
  max-width: 900px;
  margin: 0 auto;
  padding: 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.generator-header {
  text-align: center;
  margin-bottom: 30px;

  h2 {
    font-size: 28px;
    color: #333;
    margin-bottom: 10px;
  }

  .subtitle {
    color: #666;
    font-size: 14px;
  }
}

.input-section {
  .prompt-area {
    margin-bottom: 30px;
    position: relative;

    label {
      display: block;
      font-weight: 600;
      margin-bottom: 10px;
      color: #333;
    }

    textarea {
      width: 100%;
      padding: 15px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.6;
      resize: vertical;
      transition: border-color 0.3s;
      font-family: inherit;

      &:focus {
        outline: none;
        border-color: #409eff;
      }
    }

    .char-count {
      position: absolute;
      right: 10px;
      bottom: 10px;
      font-size: 12px;
      color: #999;
    }
  }

  .preferences {
    margin-bottom: 30px;

    h3 {
      font-size: 18px;
      margin-bottom: 15px;
      color: #333;
    }

    .pref-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;

      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
    }

    .pref-item {
      label {
        display: block;
        font-size: 14px;
        margin-bottom: 8px;
        color: #666;
      }

      input,
      select {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;

        &:focus {
          outline: none;
          border-color: #409eff;
        }
      }
    }
  }

  .action-buttons {
    text-align: center;

    .btn-generate {
      padding: 15px 50px;
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      border-radius: 25px;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;

      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }

    .usage-info {
      margin-top: 15px;
      font-size: 13px;
      color: #999;
    }
  }
}

.generating {
  text-align: center;
  padding: 60px 20px;

  .loading-spinner {
    width: 50px;
    height: 50px;
    margin: 0 auto 20px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  p {
    font-size: 16px;
    color: #333;
    margin-bottom: 10px;
  }

  .loading-tips {
    font-size: 14px;
    color: #999;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.preview-section {
  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #f0f0f0;

    h3 {
      font-size: 20px;
      color: #333;
    }

    .preview-actions {
      display: flex;
      gap: 10px;

      button {
        padding: 8px 20px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.3s;
      }

      .btn-apply {
        background: #67c23a;
        color: white;

        &:hover {
          background: #5daf34;
        }
      }

      .btn-secondary {
        background: #f0f0f0;
        color: #666;

        &:hover {
          background: #e0e0e0;
        }
      }
    }
  }

  .trip-summary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 25px;
    border-radius: 10px;
    margin-bottom: 25px;

    h4 {
      font-size: 22px;
      margin-bottom: 10px;
    }

    p {
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 15px;
      opacity: 0.95;
    }

    .trip-meta {
      display: flex;
      gap: 20px;
      font-size: 14px;

      span {
        opacity: 0.9;
      }
    }
  }

  .days-list {
    .day-card {
      background: #f9f9f9;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;

      .day-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;

        h5 {
          font-size: 18px;
          color: #333;
        }

        .day-date {
          color: #999;
          font-size: 14px;
        }
      }

      .activities {
        .activity-item {
          display: flex;
          gap: 15px;
          padding: 15px;
          background: white;
          border-radius: 8px;
          margin-bottom: 10px;

          .activity-time {
            flex-shrink: 0;
            font-weight: 600;
            color: #667eea;
            font-size: 14px;
          }

          .activity-content {
            flex: 1;

            strong {
              display: block;
              margin-bottom: 5px;
              color: #333;
            }

            p {
              font-size: 14px;
              color: #666;
              line-height: 1.6;
              margin-bottom: 8px;
            }

            .activity-meta {
              display: flex;
              gap: 15px;
              font-size: 13px;
              color: #999;
              margin-bottom: 5px;
            }

            .activity-tips {
              font-size: 13px;
              color: #f56c6c;
              background: #fef0f0;
              padding: 8px 12px;
              border-radius: 6px;
              margin-top: 8px;
            }
          }
        }
      }

      .day-total {
        text-align: right;
        margin-top: 15px;
        font-weight: 600;
        color: #333;
        font-size: 15px;
      }
    }
  }

  .travel-tips {
    background: #fff9e6;
    padding: 20px;
    border-radius: 10px;
    margin-top: 25px;

    h4 {
      font-size: 18px;
      color: #333;
      margin-bottom: 15px;
    }

    ul {
      list-style: none;
      padding: 0;

      li {
        padding: 8px 0;
        padding-left: 20px;
        position: relative;
        color: #666;
        line-height: 1.6;

        &:before {
          content: "•";
          position: absolute;
          left: 0;
          color: #e6a23c;
          font-weight: bold;
        }
      }
    }
  }
}
</style>

