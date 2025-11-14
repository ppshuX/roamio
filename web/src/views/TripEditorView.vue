<template>
  <div class="editor-wrapper">
    <NavBar />
    
    <div class="editor-container">
      <!-- 顶部工具栏 -->
      <div class="editor-toolbar">
        <div class="container-fluid">
          <div class="editor-toolbar-content">
            <div class="editor-toolbar-left">
              <button class="btn btn-outline-secondary btn-back" @click="goBack">
                <i class="bi bi-arrow-left"></i>
                <span class="btn-text">返回</span>
              </button>
              <h5 class="editor-toolbar-title">
                {{ isEditMode ? '编辑旅行计划' : '创建旅行计划' }}
              </h5>
            </div>
            <div class="editor-toolbar-actions">
              <button 
                v-if="isEditMode"
                class="btn btn-outline-success btn-toolbar-action" 
                @click="handleSyncToRalendarFromEditor"
                :disabled="syncingToCalendar"
                title="将行程同步到 Ralendar 日历"
              >
                <span v-if="syncingToCalendar" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-calendar-check"></i>
                <span class="btn-text">{{ syncingToCalendar ? '同步中...' : '同步到日历' }}</span>
              </button>
              <button 
                class="btn btn-outline-primary btn-toolbar-action" 
                @click="handleSave"
                :disabled="saving"
              >
                <span v-if="saving" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-save"></i>
                <span class="btn-text">保存</span>
              </button>
              <button 
                class="btn btn-primary btn-toolbar-action" 
                @click="handlePublish"
                :disabled="publishing || !canPublish"
              >
                <span v-if="publishing" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-send"></i>
                <span class="btn-text">发布</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 主编辑区 -->
      <div class="editor-main-content">
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
    </div>
    
    <!-- AI 生成器弹窗 -->
    <div v-if="showAIGenerator" class="ai-modal-overlay" @click.self="showAIGenerator = false">
      <div class="ai-modal-content">
        <div class="ai-modal-header">
          <h3>🤖 AI 智能生成行程</h3>
          <button class="btn-close-modal" @click="showAIGenerator = false">✕</button>
        </div>
        <div class="ai-modal-body">
          <TripGenerator 
            @apply="handleAIApply" 
            @sync-to-calendar="handleSyncToCalendar"
          />
        </div>
      </div>
    </div>
    
    <!-- 日期选择弹窗 -->
    <DatePickerModal
      v-if="showDatePicker"
      :days="pendingAIPlan?.days || pendingAIPlan?.days_detail?.length || 3"
      :default-date="tripData.start_date || null"
      @confirm="handleDateSelected"
      @close="showDatePicker = false"
    />
    
    <!-- 同步到日历选择界面 -->
    <div v-if="showCalendarSync" class="calendar-sync-overlay" @click.self="showCalendarSync = false">
      <div class="calendar-sync-container">
        <CalendarSyncSelector
          :events="calendarEvents"
          @close="showCalendarSync = false"
          @confirm="handleCalendarSyncConfirm"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { getTripPlan, createTripPlan, updateTripPlan } from '@/api/tripPlan'
import { syncTripToCalendar } from '@/api/ralendar'
import { convertAITripToEvents, validateEvents } from '@/utils/aiToRalendarConverter'
import { convertTripToRalendarEvents, validateTripEvents } from '@/utils/tripToRalendarConverter'
import NavBar from '@/components/NavBar.vue'
import BasicInfoEditor from '@/components/editor/BasicInfoEditor.vue'
import ModuleSelector from '@/components/editor/ModuleSelector.vue'
import ContentEditor from '@/components/editor/ContentEditor.vue'
import EditorSidebar from '@/components/editor/EditorSidebar.vue'
import TripGenerator from '@/components/ai/TripGeneratorSimple.vue'
import CalendarSyncSelector from '@/components/calendar/CalendarSyncSelector.vue'
import DatePickerModal from '@/components/calendar/DatePickerModal.vue'

export default {
  name: 'TripEditorView',
  
  components: {
    NavBar,
    BasicInfoEditor,
    ModuleSelector,
    ContentEditor,
    EditorSidebar,
    TripGenerator,
    CalendarSyncSelector,
    DatePickerModal
  },
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    
    const saving = ref(false)
    const publishing = ref(false)
    const showAIGenerator = ref(false)
    const showDatePicker = ref(false)
    const showCalendarSync = ref(false)
    const syncingToCalendar = ref(false)
    const aiGeneratedPlan = ref(null) // 保存 AI 生成的原始数据，用于同步
    const pendingAIPlan = ref(null) // 待处理同步的 AI 数据
    const calendarEvents = ref([]) // 准备同步到日历的事件列表
    const tripSlug = computed(() => route.params.slug && route.params.slug !== 'new' ? route.params.slug : null)
    
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
        
        let tripSlug = null
        if (isEditMode.value) {
          // 编辑模式：更新现有行程
          const result = await updateTripPlan(route.params.slug, tripData.value)
          tripSlug = result.slug || route.params.slug
        } else {
          // 新建模式：创建新行程
          const result = await createTripPlan(tripData.value)
          tripSlug = result.slug
        }
        
        // 发布成功后跳转到旅行详情页面
        if (tripSlug) {
          alert('发布成功！')
          router.push(`/trip/${tripSlug}/`)
        } else {
          alert('发布成功！但无法获取行程标识，请手动刷新页面')
        }
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
        
        // 保存 AI 生成的原始数据，用于后续同步到日历
        aiGeneratedPlan.value = aiTripPlan
        
        // 关闭弹窗
        showAIGenerator.value = false
        
        alert('✅ AI 生成的行程已应用，你可以继续编辑！')
      } catch (error) {
        console.error('应用 AI 数据失败:', error)
        alert('❌ 应用失败，请重试')
      }
    }
    
    // 从编辑页面同步到 Ralendar（使用已保存的行程数据）
    const handleSyncToRalendarFromEditor = () => {
      // 检查是否有行程数据
      if (!tripData.value || !tripData.value.overview || !tripData.value.overview.itinerary) {
        alert('❌ 请先添加行程内容')
        return
      }
      
      // 检查是否有开始日期
      if (!tripData.value.start_date || tripData.value.start_date === 'YYYY-MM-DD') {
        alert('❌ 请先设置行程的开始日期')
        return
      }
      
      // 检查是否有 tripSlug（已保存的行程）
      if (!tripSlug.value) {
        alert('❌ 请先保存行程，然后再同步到日历')
        return
      }
      
      try {
        // 转换行程数据为 Ralendar 事件
        const events = convertTripToRalendarEvents(tripData.value)
        
        if (events.length === 0) {
          alert('❌ 无法从行程中提取事件，请检查行程内容')
          return
        }
        
        // 验证事件
        const { valid, invalid } = validateTripEvents(events)
        
        if (invalid.length > 0) {
          console.warn('部分事件无效:', invalid)
          if (valid.length === 0) {
            alert('❌ 所有事件都无效，请检查行程内容')
            return
          }
        }
        
        // 设置日历事件列表
        calendarEvents.value = valid
        
        // 打开日历同步选择界面
        showCalendarSync.value = true
        
      } catch (error) {
        console.error('转换行程事件失败:', error)
        alert('❌ 转换行程事件失败：' + error.message)
      }
    }
    
    // 处理"同步到日历"按钮点击（AI生成后直接同步，保留此功能但建议使用上面的方法）
    const handleSyncToCalendar = (aiPlan) => {
      if (!aiPlan || !aiPlan.days_detail || aiPlan.days_detail.length === 0) {
        alert('❌ 没有可同步的行程数据')
        return
      }
      
      // 保存待处理的 AI 数据
      pendingAIPlan.value = aiPlan
      
      // 检查是否有有效的开始日期
      let hasValidDate = false
      let startDate = null
      
      // 优先检查 AI 数据中的日期范围（如果用户选择了日期范围）
      if (aiPlan.date_type === 'range' && aiPlan.date_range) {
        if (aiPlan.date_range.start_date && 
            aiPlan.date_range.start_date !== 'YYYY-MM-DD' && 
            /^\d{4}-\d{2}-\d{2}$/.test(aiPlan.date_range.start_date)) {
          startDate = aiPlan.date_range.start_date
          hasValidDate = true
          // 同时更新 tripData 的日期
          tripData.value.start_date = aiPlan.date_range.start_date
          tripData.value.end_date = aiPlan.date_range.end_date
        }
      }
      
      // 如果 AI 数据中没有日期范围，检查 tripData 中的日期
      if (!hasValidDate && tripData.value.start_date && 
          tripData.value.start_date !== 'YYYY-MM-DD' && 
          /^\d{4}-\d{2}-\d{2}$/.test(tripData.value.start_date)) {
        startDate = tripData.value.start_date
        hasValidDate = true
      } 
      // 检查 AI 数据中第一天的日期
      else if (!hasValidDate && aiPlan.days_detail?.[0]?.date) {
        const firstDayDate = aiPlan.days_detail[0].date
        if (firstDayDate !== 'YYYY-MM-DD' && /^\d{4}-\d{2}-\d{2}/.test(firstDayDate)) {
          startDate = firstDayDate.includes('T') ? firstDayDate.split('T')[0] : firstDayDate
          hasValidDate = true
        }
      }
      
      // 如果没有有效日期（用户选择了天数但没有选择日期），显示日期选择器
      if (!hasValidDate) {
        // 关闭 AI 生成弹窗，打开日期选择器
        showAIGenerator.value = false
        showDatePicker.value = true
        return
      }
      
      // 如果有有效日期，直接继续转换
      proceedWithSync(aiPlan, startDate)
    }
    
    // 处理日期选择确认
    const handleDateSelected = (selectedDate) => {
      if (!pendingAIPlan.value) {
        alert('❌ 没有待同步的行程数据')
        return
      }
      
      // 更新 tripData 中的开始日期
      if (selectedDate) {
        tripData.value.start_date = selectedDate
        
        // 计算结束日期
        const start = new Date(selectedDate)
        const days = pendingAIPlan.value.days || pendingAIPlan.value.days_detail?.length || 3
        const end = new Date(start)
        end.setDate(start.getDate() + days - 1)
        const year = end.getFullYear()
        const month = String(end.getMonth() + 1).padStart(2, '0')
        const day = String(end.getDate()).padStart(2, '0')
        tripData.value.end_date = `${year}-${month}-${day}`
      }
      
      // 关闭日期选择器，继续同步流程
      showDatePicker.value = false
      proceedWithSync(pendingAIPlan.value, selectedDate)
    }
    
    // 执行同步流程
    const proceedWithSync = (aiPlan, startDate) => {
      // 保存 AI 生成的原始数据
      aiGeneratedPlan.value = aiPlan
      
      const tripTitle = tripData.value.title || aiPlan.trip_title || '旅行'
      
      try {
        const events = convertAITripToEvents(aiPlan, tripTitle, startDate)
        
        if (events.length === 0) {
          // 诊断问题
          const hasDays = aiPlan.days_detail && aiPlan.days_detail.length > 0
          const hasActivities = aiPlan.days_detail?.some(day => 
            day.activities && Array.isArray(day.activities) && day.activities.length > 0
          )
          
          let errorMsg = '❌ 没有可同步的行程事件\n\n'
          errorMsg += '可能的原因：\n'
          if (!hasDays) errorMsg += '• 行程数据中没有天数详情\n'
          if (!hasActivities) errorMsg += '• 行程数据中没有活动信息\n'
          errorMsg += '\n请检查行程数据或重新生成行程。'
          
          alert(errorMsg)
          return
        }
        
        // 设置日历事件列表
        calendarEvents.value = events
        
        // 打开日历同步选择界面
        showCalendarSync.value = true
        
      } catch (error) {
        console.error('转换行程事件失败:', error)
        console.error('AI 行程数据:', aiPlan)
        
        let errorMsg = '❌ 转换行程事件失败\n\n'
        errorMsg += error.message || '未知错误'
        errorMsg += '\n\n请检查控制台查看详细信息。'
        
        alert(errorMsg)
      }
    }
    
    // 处理日历同步确认
    const handleCalendarSyncConfirm = async (selectedEvents) => {
      if (!selectedEvents || selectedEvents.length === 0) {
        alert('请至少选择一个行程')
        return
      }
      
      syncingToCalendar.value = true
      
      try {
        // 验证事件数据
        const { valid, invalid } = validateEvents(selectedEvents)
        
        if (invalid.length > 0) {
          console.warn('部分事件数据无效:', invalid)
          if (valid.length === 0) {
            alert('❌ 所有事件数据都无效，无法同步')
            return
          }
          const continueSync = confirm(`⚠️ 发现 ${invalid.length} 个无效事件，是否继续同步 ${valid.length} 个有效事件？`)
          if (!continueSync) {
            return
          }
        }
        
        // 获取旅行计划的 slug（优先使用计算属性，否则使用路由参数）
        let currentTripSlug = tripSlug.value || route.params.slug
        
        // 如果还没有创建旅行计划，先保存
        if (!currentTripSlug || currentTripSlug === 'new') {
          if (!tripData.value.title) {
            alert('❌ 请先填写旅行标题，才能同步到日历')
            return
          }
          
          // 先保存为草稿
          const result = await createTripPlan({
            ...tripData.value,
            status: 'draft'
          })
          currentTripSlug = result.slug
          
          // 更新路由（不刷新页面）
          router.replace(`/editor/${currentTripSlug}`)
        }
        
        // 调用后端 API 同步到 Ralendar
        const response = await syncTripToCalendar(currentTripSlug, valid)
        
        if (response.code === 200) {
          const { synced_count, failed_count } = response.data
          if (failed_count === 0) {
            alert(`✅ 同步成功！已将 ${synced_count} 个行程事件同步到 Ralendar 日历。\n\n📅 行程事件将在开始前 ${valid[0]?.reminder_minutes || 30} 分钟提醒你。`)
          } else {
            alert(`⚠️ 部分同步成功：${synced_count} 个成功，${failed_count} 个失败。`)
          }
          
          // 关闭选择界面
          showCalendarSync.value = false
          
          // 清除数据
          aiGeneratedPlan.value = null
          calendarEvents.value = []
        } else {
          throw new Error(response.message || '同步失败')
        }
        
      } catch (error) {
        console.error('同步到日历失败:', error)
        const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '同步失败，请重试'
        alert(`❌ 同步失败：${errorMsg}`)
      } finally {
        syncingToCalendar.value = false
      }
    }
    
    // 同步到 Ralendar 日历（保留原有功能，用于编辑器中的按钮）
    const syncToRalendar = async () => {
      if (!aiGeneratedPlan.value) {
        alert('❌ 请先使用 AI 生成行程，才能同步到日历')
        return
      }
      
      // 确认同步
      const confirmMsg = `确定要将所有行程同步到 Ralendar 日历吗？\n\n将创建 ${aiGeneratedPlan.value.days_detail?.length || 0} 天的行程事件，每项活动会提前 30 分钟提醒。`
      if (!confirm(confirmMsg)) {
        return
      }
      
      syncingToCalendar.value = true
      
      try {
        // 1. 转换 AI 数据为 Ralendar 事件格式
        const startDate = tripData.value.start_date || aiGeneratedPlan.value.days_detail?.[0]?.date || null
        const tripTitle = tripData.value.title || aiGeneratedPlan.value.trip_title || '旅行'
        
        const events = convertAITripToEvents(aiGeneratedPlan.value, tripTitle, startDate)
        
        if (events.length === 0) {
          alert('❌ 没有可同步的行程事件，请检查行程数据')
          return
        }
        
        // 2. 验证事件数据
        const { valid, invalid } = validateEvents(events)
        
        if (invalid.length > 0) {
          console.warn('部分事件数据无效:', invalid)
          if (valid.length === 0) {
            alert('❌ 所有事件数据都无效，无法同步')
            return
          }
          const continueSync = confirm(`⚠️ 发现 ${invalid.length} 个无效事件，是否继续同步 ${valid.length} 个有效事件？`)
          if (!continueSync) {
            return
          }
        }
        
        // 3. 获取旅行计划的 slug（如果已创建）
        let tripSlug = route.params.slug
        
        // 如果还没有创建旅行计划，先保存
        if (!tripSlug) {
          if (!tripData.value.title) {
            alert('❌ 请先填写旅行标题，才能同步到日历')
            return
          }
          
          // 先保存为草稿
          const result = await createTripPlan({
            ...tripData.value,
            status: 'draft'
          })
          tripSlug = result.slug
          
          // 更新路由（不刷新页面）
          router.replace(`/editor/${tripSlug}`)
        }
        
        // 4. 调用后端 API 同步到 Ralendar
        const response = await syncTripToCalendar(tripSlug, valid)
        
        if (response.code === 200) {
          const { synced_count, failed_count } = response.data
          if (failed_count === 0) {
            alert(`✅ 同步成功！已将 ${synced_count} 个行程事件同步到 Ralendar 日历。\n\n📅 行程事件将在开始前 30 分钟提醒你。`)
          } else {
            alert(`⚠️ 部分同步成功：${synced_count} 个成功，${failed_count} 个失败。`)
          }
          
          // 清除 AI 生成数据（表示已同步）
          aiGeneratedPlan.value = null
        } else {
          throw new Error(response.message || '同步失败')
        }
        
      } catch (error) {
        console.error('同步到日历失败:', error)
        const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '同步失败，请重试'
        alert(`❌ 同步失败：${errorMsg}`)
      } finally {
        syncingToCalendar.value = false
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
      tripSlug,
      isEditMode,
      saving,
      publishing,
      showAIGenerator,
      syncingToCalendar,
      aiGeneratedPlan,
      showDatePicker,
      showCalendarSync,
      calendarEvents,
      handleSave,
      handlePublish,
      goBack,
      handleAIApply,
      handleSyncToCalendar,
      handleSyncToRalendarFromEditor,
      handleDateSelected,
      handleCalendarSyncConfirm,
      syncToRalendar,
      availableModules,
      toggleModule,
      daysCount,
      canPublish
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

.editor-main-content {
  width: 100%;
}

/* 移动端工具栏间距在下方的 @media 中统一设置 */

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

.editor-toolbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  gap: 1rem;
}

.editor-toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.editor-toolbar-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.editor-toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-back,
.btn-toolbar-action {
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-toolbar-action i,
.btn-back i {
  font-size: 1rem;
}

/* 移动端：工具栏在导航栏下方 */
@media (max-width: 991px) {
  .editor-toolbar {
    top: 56px;
    position: fixed;
    width: 100%;
    z-index: 999; /* 确保工具栏在内容上方 */
  }
  
  /* 移动端：为固定工具栏留出空间，消除间隙 */
  .editor-main-content {
    margin-top: 0 !important; /* 移除顶部边距，紧贴工具栏 */
    padding-top: 0 !important;
  }
  
  .editor-toolbar .container-fluid {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  .editor-toolbar-content {
    padding: 0.5rem 0.75rem;
    gap: 0.5rem;
  }
  
  /* 移动端：确保容器和内容紧贴工具栏，无间隙 */
  .editor-main-content .container {
    padding-top: 0 !important;
    margin-top: 0 !important;
  }
  
  /* 移动端：确保第一个卡片（基本信息）紧贴容器顶部 */
  .editor-main-content > .container > .row > div:first-child > .card:first-child {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
  }
  
  /* 移动端：基本信息卡片头部紧贴容器顶部 */
  .editor-main-content .card-header:first-child {
    margin-top: 0 !important;
    border-top: none !important;
  }
  
  .editor-toolbar-left {
    gap: 0.5rem;
    flex: 1;
    min-width: 0;
    align-items: center;
  }
  
  .editor-toolbar-title {
    font-size: 0.875rem;
    display: block; /* 移动端显示标题，使用小字体 */
    font-weight: 500;
    color: #666;
    margin-left: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-shrink: 1;
  }
  
  .btn-back {
    padding: 0.375rem 0.5rem;
    font-size: 0.875rem;
    flex-shrink: 0;
  }
  
  .btn-back .btn-text {
    display: none; /* 移动端只显示图标 */
  }
  
  .editor-toolbar-actions {
    gap: 0.375rem;
    flex-shrink: 0;
    justify-content: flex-end;
  }
  
  .btn-toolbar-action {
    padding: 0.375rem 0.625rem;
    font-size: 0.8125rem;
    line-height: 1.2;
    min-width: auto;
  }
  
  .btn-toolbar-action i {
    font-size: 0.875rem;
    margin-right: 0.25rem;
  }
  
  .btn-toolbar-action .btn-text {
    font-size: 0.8125rem;
    display: inline;
  }
  
  .btn-toolbar-action .spinner-border-sm {
    width: 0.875rem;
    height: 0.875rem;
    margin-right: 0.25rem;
  }
}

/* 更小的移动端：按钮更紧凑 */
@media (max-width: 576px) {
  .editor-toolbar-content {
    padding: 0.4rem 0.5rem;
    gap: 0.375rem;
  }
  
  .editor-toolbar-left {
    gap: 0.375rem;
    min-width: 0;
  }
  
  .editor-toolbar-title {
    font-size: 0.75rem;
    margin-left: 0.25rem;
  }
  
  .btn-back {
    padding: 0.3rem 0.4rem;
    font-size: 0.8rem;
    flex-shrink: 0;
  }
  
  .editor-toolbar-actions {
    gap: 0.25rem;
    flex-shrink: 0;
  }
  
  .btn-toolbar-action {
    padding: 0.3rem 0.5rem;
    font-size: 0.75rem;
  }
  
  .btn-toolbar-action i {
    font-size: 0.8rem;
    margin-right: 0.2rem;
  }
  
  .btn-toolbar-action .btn-text {
    font-size: 0.75rem;
    display: inline;
  }
  
  .btn-toolbar-action .spinner-border-sm {
    margin-right: 0.2rem;
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

/* 移动端：减少AI按钮间距 */
@media (max-width: 768px) {
  .ai-quick-start {
    margin-bottom: 0.75rem !important;
  }
}

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
  
  /* 移动端：消除容器顶部内边距，让内容紧贴工具栏 */
  .container.py-4 {
    padding-top: 0 !important;  /* 消除顶部间距，紧贴工具栏 */
    padding-bottom: 0.75rem !important;
  }
  
  /* 移动端：基本信息卡片无上边距，紧贴容器顶部 */
  .editor-main-content .card:first-child {
    margin-top: 0 !important;
  }
  
  /* AI 按钮间距 */
  .ai-quick-start {
    margin-bottom: 0.75rem !important;
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

/* 日历同步弹窗样式 */
.calendar-sync-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.calendar-sync-container {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 响应式 */
@media (max-width: 991px) {
  .editor-container {
    padding-top: 56px;  /* 只需要为固定定位的导航栏留空间 */
    padding-bottom: 0;
    margin: 0;
  }
  
  /* 移动端：编辑器主内容区域紧贴工具栏 */
  .editor-main-content {
    margin-top: 0 !important;
    padding-top: 0 !important;
  }
  
  /* 移动端：容器无内边距，内容紧贴边缘 */
  .editor-main-content .container.py-4 {
    padding-top: 0 !important;
    padding-bottom: 1rem !important;
    margin-top: 0 !important;
  }
  
  /* 移动端：移除第一行和第一列的上边距 */
  .editor-main-content .container .row {
    margin-top: 0 !important;
  }
  
  .editor-main-content .container .row > div {
    padding-top: 0 !important;
  }
  
  .ai-modal-content {
    max-height: 95vh;
  }
  
  .calendar-sync-overlay {
    padding: 10px;
  }
  
  .calendar-sync-container {
    max-width: 100%;
    max-height: 95vh;
  }
}
</style>
