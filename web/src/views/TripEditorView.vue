<template>
  <div class="editor-wrapper">
    <NavBar />
    
    <div class="editor-container">
      <!-- 顶部工具栏 -->
      <div class="editor-toolbar">
        <div class="container-fluid">
          <div class="d-flex justify-content-between align-items-center py-3">
            <div>
              <button class="btn btn-outline-secondary me-2" @click="goBack">
                <i class="bi bi-arrow-left me-1"></i>返回
              </button>
              <h5 class="d-inline-block mb-0 ms-3">
                {{ isEditMode ? '编辑旅行计划' : '创建旅行计划' }}
              </h5>
            </div>
            <div>
              <button 
                class="btn btn-outline-primary me-2" 
                @click="handleSave"
                :disabled="saving"
              >
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-save me-1"></i>
                保存
              </button>
              <button 
                class="btn btn-primary" 
                @click="handlePublish"
                :disabled="publishing || !canPublish"
              >
                <span v-if="publishing" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-send me-1"></i>
                发布
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 主编辑区 -->
      <div class="container py-4">
        <div class="row">
          <!-- 左侧：编辑面板 -->
          <div class="col-lg-8">
            <!-- AI 智能生成按钮 -->
            <div v-if="!isEditMode" class="ai-quick-start mb-4">
              <button 
                class="btn btn-lg btn-ai w-100" 
                @click="showAIGenerator = true"
              >
                <span class="ai-icon">🤖</span>
                <span class="ai-text">
                  <strong>AI 智能生成行程</strong>
                  <small>告诉 AI 你的想法，5分钟生成完整行程</small>
                </span>
              </button>
            </div>
            
            <!-- 基本信息编辑器 -->
            <BasicInfoEditor v-model="tripData" />
            
            <!-- 模块选择器 -->
            <ModuleSelector
              :modules="availableModules"
              :enabled-modules="tripData.config.enabledModules"
              @toggle="toggleModule"
            />
            
            <!-- 内容编辑器 -->
            <ContentEditor
              v-model="tripData.overview"
              :enabled-modules="tripData.config.enabledModules"
            />
          </div>
          
          <!-- 右侧：设置面板 -->
          <div class="col-lg-4">
            <EditorSidebar
              v-model="tripData"
              :days-count="daysCount"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- AI 生成器弹窗 -->
    <div v-if="showAIGenerator" class="ai-modal-overlay" @click.self="showAIGenerator = false">
      <div class="ai-modal-content">
        <div class="ai-modal-header">
          <h3>🤖 AI 智能生成行程</h3>
          <button class="btn-close-modal" @click="showAIGenerator = false">✕</button>
        </div>
        <div class="ai-modal-body">
          <TripGenerator @apply="handleAIApply" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { getTripPlan, createTripPlan, updateTripPlan } from '@/api/tripPlan'
import NavBar from '@/components/NavBar.vue'
import BasicInfoEditor from '@/components/editor/BasicInfoEditor.vue'
import ModuleSelector from '@/components/editor/ModuleSelector.vue'
import ContentEditor from '@/components/editor/ContentEditor.vue'
import EditorSidebar from '@/components/editor/EditorSidebar.vue'
import TripGenerator from '@/components/ai/TripGeneratorSimple.vue'

export default {
  name: 'TripEditorView',
  
  components: {
    NavBar,
    BasicInfoEditor,
    ModuleSelector,
    ContentEditor,
    EditorSidebar,
    TripGenerator
  },
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    
    const saving = ref(false)
    const publishing = ref(false)
    const showAIGenerator = ref(false)
    const tripId = computed(() => route.params.id ? parseInt(route.params.id) : null)
    
    // 可用模块
    const availableModules = [
      { id: 'basicInfo', name: '基本信息', icon: 'ℹ️', description: '出发地、目的地等' },
      { id: 'highlights', name: '行程亮点', icon: '✨', description: '主要景点和活动' },
      { id: 'itinerary', name: '详细行程', icon: '📅', description: '每日安排' },
      { id: 'budget', name: '预算参考', icon: '💰', description: '费用明细' },
      { id: 'tips', name: '实用提示', icon: '💡', description: '注意事项' },
    ]
    
    // 旅行数据
    const tripData = ref({
      title: '',
      description: '',
      icon: '🗺️',
      start_date: null,
      end_date: null,
      status: 'draft',
      visibility: 'private',
      theme_color: '#f0e68c',
      background_music: '',
      config: {
        enabledModules: ['basicInfo', 'highlights']
      },
      overview: {
        basicInfo: {
          departure: '',
          destination: '',
          transport: '',
          accommodation: '',
          participants: ''
        },
        highlights: [],
        itinerary: [],
        budget: {
          items: [],
          total: 0
        },
        tips: []
      },
      created_at: null,
      updated_at: null
    })
    
    const isEditMode = computed(() => {
      const slug = route.params.slug
      return slug && slug !== 'new'
    })
    
    const canPublish = computed(() => {
      return tripData.value.title && tripData.value.title.trim().length > 0
    })
    
    const daysCount = computed(() => {
      if (!tripData.value.start_date || !tripData.value.end_date) return 0
      const start = new Date(tripData.value.start_date)
      const end = new Date(tripData.value.end_date)
      return Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
    })
    
    // 模块管理
    const toggleModule = (moduleId) => {
      const index = tripData.value.config.enabledModules.indexOf(moduleId)
      if (index > -1) {
        tripData.value.config.enabledModules.splice(index, 1)
      } else {
        tripData.value.config.enabledModules.push(moduleId)
      }
    }
    
    // 保存
    const handleSave = async () => {
      if (!canPublish.value) {
        alert('请至少填写标题')
        return
      }
      
      saving.value = true
      try {
        // 计算预算总计
        tripData.value.overview.budget.total = tripData.value.overview.budget.items.reduce(
          (sum, item) => sum + (item.amount || 0), 0
        )
        
        if (isEditMode.value) {
          await updateTripPlan(route.params.slug, tripData.value)
          alert('保存成功！')
        } else {
          const result = await createTripPlan(tripData.value)
          alert('创建成功！')
          router.push(`/editor/${result.slug}`)
        }
      } catch (error) {
        console.error('❌ 保存失败:', error)
        console.error('错误详情:', error.response?.data)
        alert('保存失败：' + (error.response?.data?.detail || error.message))
      } finally {
        saving.value = false
      }
    }
    
    // 发布
    const handlePublish = async () => {
      if (!canPublish.value) {
        alert('请至少填写标题')
        return
      }
      
      const isPublicVisibility = tripData.value.visibility === 'public'
      const confirmMsg = isPublicVisibility
        ? '确定要发布这个旅行计划吗？发布后将可被访问。'
        : '确定要发布这个旅行计划吗？它将保持私有，仅自己可见。'
      if (!confirm(confirmMsg)) {
        return
      }
      
      publishing.value = true
      try {
        tripData.value.status = 'published'
        tripData.value.overview.budget.total = tripData.value.overview.budget.items.reduce(
          (sum, item) => sum + (item.amount || 0), 0
        )
        
        if (isEditMode.value) {
          await updateTripPlan(route.params.slug, tripData.value)
        } else {
          const result = await createTripPlan(tripData.value)
          router.push(`/editor/${result.slug}`)
        }
        
        alert('发布成功！')
      } catch (error) {
        console.error('❌ 发布失败:', error)
        console.error('错误详情:', error.response?.data)
        alert('发布失败：' + (error.response?.data?.detail || error.message))
      } finally {
        publishing.value = false
      }
    }
    
    const goBack = () => {
      if (confirm('确定要离开吗？未保存的更改将丢失。')) {
        router.push('/my-trips')
      }
    }
    
    // 加载数据
    const loadTripData = async () => {
      const slug = route.params.slug
      
      // 如果是新建模式，不加载
      if (!slug || slug === 'new') {
        // 为新建行程自动填充作者昵称
        const nickname = userStore.userInfo?.profile?.nickname || userStore.username || ''
        if (nickname) {
          tripData.value.overview.basicInfo.participants = nickname
        }
        return
      }
      
      // 编辑模式：加载现有数据
      try {
        const data = await getTripPlan(slug)
        tripData.value = {
          ...tripData.value,
          ...data,
          // 确保overview和config有默认值
          overview: data.overview || tripData.value.overview,
          config: data.config || tripData.value.config
        }
        // 若缺少作者昵称则补充
        const nickname = userStore.userInfo?.profile?.nickname || userStore.username || ''
        if (nickname && !tripData.value.overview.basicInfo?.participants) {
          tripData.value.overview.basicInfo.participants = nickname
        }
      } catch (error) {
        console.error('加载失败:', error)
        alert('加载旅行计划失败')
        router.push('/my-trips')
      }
    }
    
    // AI 生成应用处理
    const handleAIApply = (aiTripPlan) => {
      try {
        // 1. 应用基本信息
        tripData.value.title = aiTripPlan.trip_title || ''
        tripData.value.description = aiTripPlan.summary || ''
        
        // 2. 应用目的地
        if (aiTripPlan.destination) {
          tripData.value.overview.basicInfo.destination = aiTripPlan.destination
        }
        
        // 3. 应用日期
        if (aiTripPlan.days_detail && aiTripPlan.days_detail.length > 0) {
          const firstDay = aiTripPlan.days_detail[0]
          const lastDay = aiTripPlan.days_detail[aiTripPlan.days_detail.length - 1]
          if (firstDay.date) tripData.value.start_date = firstDay.date
          if (lastDay.date) tripData.value.end_date = lastDay.date
        }
        
        // 4. 应用行程亮点（提取每天最精彩的活动）
        if (aiTripPlan.days_detail && aiTripPlan.days_detail.length > 0) {
          tripData.value.overview.highlights = aiTripPlan.days_detail.map(day => {
            // 找出当天最有特色的活动（通常是景点类型）
            const mainActivity = day.activities.find(a => 
              a.location_type === '景点' || a.location_type === 'attraction'
            ) || day.activities[0]
            
            return `${day.title.replace(/^Day \d+:\s*/, '')}: ${mainActivity.location} - ${mainActivity.description.substring(0, 50)}...`
          })
        }
        
        // 5. 应用详细行程（转换为前端期望的格式）
        if (aiTripPlan.days_detail && aiTripPlan.days_detail.length > 0) {
          tripData.value.overview.itinerary = aiTripPlan.days_detail.map(day => {
            // 将 activities 数组转换为文本描述
            const contentText = day.activities.map(activity => 
              `${activity.time} - ${activity.location}\n${activity.description}`
            ).join('\n\n')
            
            // 提取当天亮点（第一个景点活动）
            const mainActivity = day.activities.find(a => 
              a.location_type === '景点' || a.location_type === 'attraction'
            ) || day.activities[0]
            
            return {
              day: day.title || `第${day.day_number}天`,
              time: day.activities.length > 0 ? 
                `${day.activities[0].time}-${day.activities[day.activities.length-1].time}` : '',
              content: contentText,
              highlight: mainActivity ? `${mainActivity.location} - ${mainActivity.description.substring(0, 30)}...` : ''
            }
          })
        }
        
        // 6. 应用预算（字段名改为 name，匹配前端组件）
        if (aiTripPlan.budget_breakdown) {
          const breakdown = aiTripPlan.budget_breakdown
          const budgetItems = []
          
          // 注意：前端组件期望 name 字段，不是 category
          if (breakdown.accommodation > 0) budgetItems.push({ name: '住宿', amount: breakdown.accommodation, note: '' })
          if (breakdown.meals > 0) budgetItems.push({ name: '餐饮', amount: breakdown.meals, note: '' })
          if (breakdown.transportation > 0) budgetItems.push({ name: '交通', amount: breakdown.transportation, note: '' })
          if (breakdown.tickets > 0) budgetItems.push({ name: '门票', amount: breakdown.tickets, note: '' })
          if (breakdown.shopping > 0) budgetItems.push({ name: '购物', amount: breakdown.shopping, note: '' })
          if (breakdown.emergency > 0) budgetItems.push({ name: '应急', amount: breakdown.emergency, note: '' })
          
          tripData.value.overview.budget.items = budgetItems
          tripData.value.overview.budget.total = aiTripPlan.total_budget || 
            budgetItems.reduce((sum, item) => sum + item.amount, 0)
        }
        
        // 7. 应用旅行建议
        if (aiTripPlan.travel_tips && Array.isArray(aiTripPlan.travel_tips)) {
          tripData.value.overview.tips = aiTripPlan.travel_tips
        }
        
        // 启用相关模块
        tripData.value.config.enabledModules = [
          'basicInfo', 'highlights', 'itinerary', 'budget', 'tips'
        ]
        
        // 关闭弹窗
        showAIGenerator.value = false
        
        alert('✅ AI 生成的行程已应用，你可以继续编辑！')
      } catch (error) {
        console.error('应用 AI 数据失败:', error)
        alert('❌ 应用失败，请重试')
      }
    }
    
    onMounted(() => {
      if (!userStore.isLoggedIn) {
        alert('请先登录')
        router.push('/login')
        return
      }
      loadTripData()
    })
    
    return {
      tripData,
      tripId,
      saving,
      publishing,
      showAIGenerator,
      isEditMode,
      canPublish,
      daysCount,
      availableModules,
      toggleModule,
      handleSave,
      handlePublish,
      handleAIApply,
      goBack
    }
  }
}
</script>

<style scoped>
.editor-wrapper {
  min-height: 100vh;
  background: #f5f7fa;
}

.editor-container {
  padding-top: 0;
}

/* 移动端需要留出导航栏空间 */
@media (max-width: 991px) {
  .editor-container {
    padding-top: 56px;
  }
}

.editor-toolbar {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 移动端：工具栏在导航栏下方 */
@media (max-width: 991px) {
  .editor-toolbar {
    top: 56px;
    position: fixed;
  }
}

.edit-panel :deep(.card) {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  overflow: hidden;
}

/* AI 快速开始按钮 */
.ai-quick-start {
  margin-bottom: 20px;
}

/* 移动端规则已合并到下方统一的 @media 中 */

.btn-ai {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  transition: all 0.3s;
  border-radius: 12px;
}

.btn-ai:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  color: white;
}

.ai-icon {
  font-size: 32px;
}

.ai-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.ai-text strong {
  font-size: 18px;
  margin-bottom: 4px;
}

.ai-text small {
  font-size: 13px;
  opacity: 0.9;
}

/* AI 弹窗样式 */
.ai-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.ai-modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 1000px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.ai-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #e0e0e0;
}

.ai-modal-header h3 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.btn-close-modal:hover {
  background: #f0f0f0;
  color: #333;
}

.ai-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* 移动端全面优化 */
@media (max-width: 768px) {
  /* 工具栏整体缩小 */
  .d-flex.justify-content-between.py-3 {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
  }
  
  /* 标题缩小并确保在一行 */
  .d-flex.justify-content-between h5 {
    font-size: 0.9rem !important;
    margin: 0 !important;
    white-space: nowrap;
  }
  
  /* 缩小工具栏按钮 */
  .d-flex.justify-content-between .btn {
    font-size: 0.75rem;
    padding: 0.35rem 0.6rem;
  }
  
  .d-flex.justify-content-between .btn i,
  .d-flex.justify-content-between .btn svg {
    width: 12px;
    height: 12px;
    font-size: 12px;
  }
  
  /* 返回按钮和标题之间的间距 */
  .d-flex.justify-content-between .ms-3 {
    margin-left: 0.5rem !important;
  }
  
  /* 保存和发布按钮之间的间距 */
  .d-flex.justify-content-between .me-2 {
    margin-right: 0.375rem !important;
  }
  
  /* 减少容器所有内边距 */
  .container.py-4 {
    padding-top: 0 !important;
    padding-bottom: 0.75rem !important;
  }
  
  /* 缩小 AI 按钮并减少间距 */
  .ai-quick-start {
    margin-top: 0 !important;
    margin-bottom: 0.5rem !important;
  }
  
  /* 工具栏内边距 */
  .editor-toolbar {
    padding: 0.375rem 0 !important;
  }
  
  .btn-ai {
    padding: 12px;
    gap: 10px;
  }
  
  .ai-icon {
    font-size: 24px;
    width: 40px;
    height: 40px;
  }
  
  .ai-text strong {
    font-size: 14px;
  }
  
  .ai-text small {
    font-size: 11px;
  }
  
  /* 缩小编辑面板 */
  .edit-panel {
    font-size: 0.85rem;
  }
  
  .edit-panel :deep(.card) {
    margin-bottom: 0.75rem;
  }
  
  .edit-panel :deep(.card-header) {
    padding: 0.625rem 0.875rem;
    font-size: 0.9rem;
  }
  
  .edit-panel :deep(.card-body) {
    padding: 0.75rem;
  }
  
  .edit-panel :deep(.form-label) {
    font-size: 0.8rem;
    margin-bottom: 0.375rem;
  }
  
  .edit-panel :deep(.form-control),
  .edit-panel :deep(.form-select),
  .edit-panel :deep(input),
  .edit-panel :deep(textarea) {
    font-size: 0.8rem;
    padding: 0.4rem 0.625rem;
  }
  
  .edit-panel :deep(.btn) {
    font-size: 0.75rem;
    padding: 0.375rem 0.625rem;
  }
  
  /* 缩小模态框 */
  .ai-modal-overlay {
    padding: 10px;
  }
  
  .ai-modal-header {
    padding: 12px 16px;
  }
  
  .ai-modal-header h3 {
    font-size: 16px;
  }
  
  .btn-close-modal {
    font-size: 20px;
    width: 28px;
    height: 28px;
  }
}

/* 响应式 */
@media (max-width: 991px) {
  .editor-container {
    padding-top: 120px;
  }
  
  .ai-modal-content {
    max-height: 95vh;
  }
}
</style>
