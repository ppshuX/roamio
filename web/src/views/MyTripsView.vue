<template>
  <div class="my-trips-wrapper">
    <NavBar />
    
    <div class="container py-5">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>我的旅行列表</h2>
        <button class="btn btn-primary" @click="createNew">
          <i class="bi bi-plus-circle me-2"></i>创建新旅行
        </button>
      </div>
      
      <!-- Loading状态 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
      </div>
      
      <!-- 旅行列表 -->
      <div v-else-if="trips.length > 0" class="row">
        <div v-for="trip in trips" :key="trip.id" class="col-md-6 col-lg-4 mb-4">
          <div class="trip-card" @click="viewTrip(trip.slug)" style="cursor: pointer;">
            <div class="trip-header" :style="{ background: trip.theme_color || '#f0e68c' }">
              <div class="trip-icon">{{ trip.icon }}</div>
              <div class="trip-meta">
                <span class="badge" :class="trip.status === 'published' ? 'bg-success' : 'bg-secondary'">
                  {{ trip.status === 'published' ? '已发布' : '草稿' }}
                </span>
                <span class="badge ms-2" :class="trip.visibility === 'public' ? 'bg-info' : 'bg-warning'">
                  {{ trip.visibility === 'public' ? '公开' : '私有' }}
                </span>
              </div>
            </div>
            <div class="trip-body">
              <h5 class="trip-title">{{ trip.title }}</h5>
              <p class="trip-desc text-muted">{{ trip.description || '暂无描述' }}</p>
              <div class="trip-info">
                <small class="text-muted">
                  <i class="bi bi-calendar me-1"></i>{{ trip.days_count || 0 }}天
                </small>
                <small class="text-muted ms-3">
                  <i class="bi bi-clock me-1"></i>{{ formatDate(trip.updated_at) }}
                </small>
              </div>
            </div>
            <div class="trip-actions">
              <button class="btn btn-sm btn-outline-primary" @click.stop="editTrip(trip.slug)">
                <i class="bi bi-pencil me-1"></i>编辑
              </button>
              
              <!-- 管理员可直接添加/移除旅行树 -->
              <template v-if="userStore.isAdmin">
                <button 
                  v-if="trip.isOnTree" 
                  class="btn btn-sm btn-danger" 
                  @click.stop="removeFromTree(trip.slug)">
                  <i class="bi bi-x-circle me-1"></i>摘下果实
                </button>
                <button 
                  v-else
                  class="btn btn-sm btn-success" 
                  @click.stop="addToTree(trip.slug)">
                  <i class="bi bi-tree me-1"></i>运用到旅行树
                </button>
              </template>
              <!-- 非管理员显示申请按钮 -->
              <template v-else>
                <button 
                  class="btn btn-sm btn-success" 
                  @click.stop="requestApplyToTree()">
                  <i class="bi bi-tree me-1"></i>申请运用到旅行树
                </button>
              </template>
              <button class="btn btn-sm btn-outline-secondary" @click.stop="showAdvancedSettings(trip.slug)" title="高级选项">
                ⚙️
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-state text-center py-5">
        <div class="empty-icon mb-3">📝</div>
        <h4>还没有旅行</h4>
        <p class="text-muted mb-4">开始创建你的第一个旅行吧！</p>
        <button class="btn btn-primary btn-lg" @click="createNew">
          <i class="bi bi-plus-circle me-2"></i>创建新旅行
        </button>
      </div>
    </div>
    
    <!-- 高级设置模态框 -->
    <AdvancedSettingsModal
      :show="showModal"
      title="⚙️ 高级选项"
      warning-text="删除旅行计划将会永久删除您的所有数据，包括："
      :warning-items="[
        '所有行程安排',
        '所有评论和回复',
        '所有统计数据',
        '所有图片和视频'
      ]"
      action-button-text="🗑️ 删除旅行计划"
      @close="closeModal"
      @confirm="confirmDeleteTrip"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { getMyTrips, deleteTripPlan, addTripToTree, removeTripFromTree } from '@/api/tripPlan'
import { getTripList } from '@/api/trip'
import NavBar from '@/components/NavBar.vue'
import AdvancedSettingsModal from '@/components/AdvancedSettingsModal.vue'

export default {
  name: 'MyTripsView',
  
  components: {
    NavBar,
    AdvancedSettingsModal
  },
  
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const trips = ref([])
    const loading = ref(true)
    const showModal = ref(false)
    const currentTripSlug = ref(null)
    
    const fetchMyTrips = async () => {
      loading.value = true
      try {
        const data = await getMyTrips()
        const tripsList = data.results || data || []
        
        trips.value = tripsList
        await checkTreeStatus() // 检查是否在旅行树中
      } catch (error) {
        console.error('获取旅行大厅失败:', error)
        alert('加载失败')
      } finally {
        loading.value = false
      }
    }
    
    const createNew = () => {
      router.push('/editor/new')
    }
    
    const editTrip = (slug) => {
      router.push(`/editor/${slug}`)
    }
    
    const viewTrip = (slug) => {
      router.push(`/trip/${slug}/`)
    }
    
    // 显示高级设置模态框
    const showAdvancedSettings = (slug) => {
      if (!slug) {
        alert('错误：该旅行计划缺少标识符')
        return
      }
      currentTripSlug.value = slug
      showModal.value = true
    }
    
    // 关闭模态框
    const closeModal = () => {
      showModal.value = false
      currentTripSlug.value = null
    }
    
    // 确认删除旅行计划
    const confirmDeleteTrip = () => {
      const slug = currentTripSlug.value
      
      if (!slug) {
        alert('错误：无法获取旅行计划标识')
        closeModal()
        return
      }
      
      if (!confirm('⚠️ 请再次确认：您确定要删除这个旅行计划吗？\n\n此操作无法撤销！')) {
        return
      }
      
      deleteTrip(slug)
      closeModal()
    }
    
    // 删除旅行计划
    const deleteTrip = async (slug) => {
      if (!slug) {
        alert('错误：无法获取旅行计划标识')
        return
      }
      
      try {
        await deleteTripPlan(slug)
        alert('删除成功')
        await fetchMyTrips()
      } catch (error) {
        console.error('删除失败:', error)
        alert('删除失败：' + (error.response?.data?.detail || error.message))
      }
    }
    
    const addToTree = async (slug) => {
      if (!confirm('确定要将此旅行计划添加到旅行树吗？它将显示在首页的旅行树上。')) {
        return
      }
      
      try {
        const result = await addTripToTree(slug)
        alert(result.detail || '成功添加到旅行树！')
        await fetchMyTrips() // 刷新列表
      } catch (error) {
        console.error('添加到旅行树失败:', error)
        alert('添加到旅行树失败，请稍后重试')
      }
    }
    
    const removeFromTree = async (slug) => {
      if (!confirm('确定要将此旅行计划从旅行树摘下吗？它将不再显示在首页的旅行树上。')) {
        return
      }
      
      try {
        const result = await removeTripFromTree(slug)
        alert(result.detail || '成功摘下果实！')
        await fetchMyTrips() // 刷新列表
      } catch (error) {
        console.error('摘下果实失败:', error)
        alert('摘下果实失败，请稍后重试')
      }
    }
    
    // 非管理员：申请运用到旅行树
    const requestApplyToTree = () => {
      alert('该功能暂未开放')
    }
    
    const checkTreeStatus = async () => {
      try {
        const treeData = await getTripList()
        const treeSlugs = new Set((treeData.results || treeData || []).map(t => t.slug))
        
        // 为每个trip添加isOnTree属性
        trips.value.forEach(trip => {
          trip.isOnTree = treeSlugs.has(trip.slug)
        })
      } catch (error) {
        console.error('获取旅行树状态失败:', error)
      }
    }
    
    const formatDate = (dateStr) => {
      if (!dateStr) return '暂无'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    }
    
    onMounted(() => {
      if (!userStore.isLoggedIn) {
        alert('请先登录')
        router.push('/login')
        return
      }
      fetchMyTrips()
    })
    
    return {
      trips,
      loading,
      showModal,
      userStore,
      createNew,
      editTrip,
      viewTrip,
      showAdvancedSettings,
      closeModal,
      confirmDeleteTrip,
      deleteTrip,
      addToTree,
      removeFromTree,
      requestApplyToTree,
      formatDate
    }
  }
}
</script>

<style scoped>
.my-trips-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #e8f4fd 0%, #d1ecf1 100%);
}

.trip-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.trip-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.trip-header {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trip-icon {
  font-size: 2.5rem;
}

.trip-body {
  padding: 1.5rem;
}

.trip-title {
  color: #2c3e50;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.trip-desc {
  font-size: 0.9rem;
  margin-bottom: 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.trip-info {
  border-top: 1px solid #e0e0e0;
  padding-top: 0.75rem;
}

.trip-actions {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 0.5rem;
  justify-content: space-between;
}

/* 空状态 */
.empty-state {
  background: white;
  border-radius: 16px;
  padding: 4rem 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 4rem;
  opacity: 0.5;
}

/* 响应式 */
@media (max-width: 768px) {
  .trip-actions {
    flex-wrap: wrap;
  }
  
  .trip-actions .btn {
    flex: 1;
    min-width: 80px;
  }
}
</style>

