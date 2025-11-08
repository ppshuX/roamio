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
    
    <!-- 悬浮 Ralendar 按钮（仅编辑模式 + 移动端） -->
    <FloatingRalendarButton 
      v-if="isEditMode && tripId"
      ref="floatingButton"
      :trip-id="tripId"
    />
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
import FloatingRalendarButton from '@/components/events/FloatingRalendarButton.vue'

export default {
  name: 'TripEditorView',
  
  components: {
    NavBar,
    BasicInfoEditor,
    ModuleSelector,
    ContentEditor,
    EditorSidebar,
    FloatingRalendarButton
  },
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    
    const saving = ref(false)
    const publishing = ref(false)
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
        console.error('保存失败:', error)
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
        console.error('发布失败:', error)
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
      isEditMode,
      canPublish,
      daysCount,
      availableModules,
      toggleModule,
      handleSave,
      handlePublish,
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
  padding-top: 60px;
}

.editor-toolbar {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.edit-panel :deep(.card) {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  overflow: hidden;
}

/* 响应式 */
@media (max-width: 991px) {
  .editor-container {
    padding-top: 120px;
  }
}
</style>
