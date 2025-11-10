<template>
  <div class="trip-detail-container" :style="{ background: (trip && trip.theme_color) || '#f0e68c' }">
    <!-- 导航栏 -->
    <NavBar />
    
    <!-- 操作按钮组 -->
    <TripActionButtons
      :is-playing="isPlaying"
      @back="goBack"
      @scroll-to-comments="scrollToComments"
      @toggle-music="toggleMusic"
    />
    
    <!-- 背景音乐 -->
    <audio ref="audioPlayer" :src="musicSrc || ''" preload="auto" loop></audio>
    
    <div class="container-fluid py-5">
      <!-- Loading状态 -->
      <div v-if="loading" class="text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
      </div>
      
      <!-- 错误提示 -->
      <div v-else-if="error" class="row justify-content-center">
        <div class="col-lg-6 col-xl-5">
          <div class="error-card">
            <div class="error-icon">🔒</div>
            <h3 class="error-title">{{ errorMessage }}</h3>
            <p class="error-description">
              {{ errorMessage.includes('不存在') ? '该旅行可能不存在、已被删除，或设置为私有。' : '如有疑问，请联系旅行计划的作者。' }}
            </p>
            <div class="error-actions">
              <button class="btn btn-primary" @click="router.push('/')">
                <i class="bi bi-arrow-left me-2"></i>返回首页
              </button>
              <button v-if="!isAuthenticated && errorMessage.includes('不存在')" class="btn btn-outline-primary ms-2" @click="router.push('/login')">
                <i class="bi bi-box-arrow-in-right me-2"></i>登录后查看
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 旅行详情 -->
      <div v-else-if="trip" class="row g-4 justify-content-center">
        <!-- 主内容区 -->
        <div class="col-lg-8 col-xl-7">
          <!-- 页面标题 -->
          <TripHeader
            :title="trip.name || trip.title"
            :description="trip.description"
          />
          
          <!-- 旅行进度条 -->
          <TripProgress
            v-if="(tripConfig && tripConfig.dates) || (trip.start_date && trip.end_date)"
            :start-date="tripConfig?.dates?.start || trip.start_date"
            :end-date="tripConfig?.dates?.end || trip.end_date"
          />
          
          <!-- 行程概览 -->
          <TripOverview v-if="trip.overview && Object.keys(trip.overview).length > 0" title="行程概览">
            <!-- 基本信息 -->
            <TripBasicInfo v-if="trip.overview.basicInfo" :basic-info="trip.overview.basicInfo" />
            
            <!-- 行程亮点 -->
            <TripHighlights v-if="trip.overview.highlights" :highlights="trip.overview.highlights" />
            
            <!-- 详细行程 -->
            <TripItinerary v-if="trip.overview.itinerary" :itinerary="trip.overview.itinerary" />
            
            <!-- 预算参考 -->
            <TripBudget v-if="trip.overview.budget" :budget="trip.overview.budget" />
            
            <!-- 实用提示 -->
            <TripTips v-if="trip.overview.tips" :tips="trip.overview.tips" />
          </TripOverview>
          
          <!-- 如果没有 overview，尝试使用旧的 tripConfig（向后兼容） -->
          <TripOverview v-else-if="tripConfig && tripConfig.overview" title="行程概览">
            <!-- 基本信息 -->
            <TripBasicInfo :basic-info="tripConfig.overview.basicInfo" />
            
            <!-- 行程亮点 -->
            <TripHighlights :highlights="tripConfig.overview.highlights" />
            
            <!-- 详细行程 -->
            <TripItinerary :itinerary="tripConfig.overview.itinerary" />
            
            <!-- 预算参考 -->
            <TripBudget :budget="tripConfig.overview.budget" />
            
            <!-- 实用提示 -->
            <TripTips :tips="tripConfig.overview.tips" />
          </TripOverview>
          
          <!-- 如果都没有，显示默认内容 -->
          <TripOverview v-else title="行程概览">
            <p class="text-muted text-center">行程内容正在筹划中，敬请期待...</p>
          </TripOverview>
          
          <!-- 统计组件 -->
          <TripStats
            :views="trip.stats?.views || 0"
            :likes="trip.stats?.likes || 0"
            :can-like="trip.overview ? (trip.visibility === 'public') : true"
            @like="handleLike"
          />
          
          <!-- 评论区组件 -->
          <CommentSection
            ref="commentSectionRef"
            :comments="comments"
            :is-admin="isAdmin"
            :is-author="isAuthor"
            :get-avatar-url="getAvatarUrl"
            @submit-comment="handleSubmitComment"
            @delete-comment="handleDeleteComment"
            @add-image="handleAddImage"
            @update-comment="handleUpdateComment"
            @submit-reply="handleSubmitReply"
            @submit-nested-reply="handleSubmitNestedReply"
            @load-replies="handleLoadReplies"
            @like-reply="handleLikeReply"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { getTripDetail, likeTrip, getTripStats, getTripPlanStats, likeTripPlan, viewTripPlan } from '@/api/trip'
import { getCommentList, createComment, deleteComment, addCommentImage, updateComment, getCommentReplies, likeComment } from '@/api/comment'
import { getAvatarUrl } from '@/config/api'
import { getTripConfig } from '@/config/tripConfig'

// 组件导入
import NavBar from '@/components/NavBar.vue'
import TripHeader from '@/components/trip/TripHeader.vue'
import TripProgress from '@/components/TripProgress.vue'
import TripOverview from '@/components/TripOverview.vue'
import TripBasicInfo from '@/components/trip/TripBasicInfo.vue'
import TripHighlights from '@/components/trip/TripHighlights.vue'
import TripItinerary from '@/components/trip/TripItinerary.vue'
import TripBudget from '@/components/trip/TripBudget.vue'
import TripTips from '@/components/trip/TripTips.vue'
import TripStats from '@/components/TripStats.vue'
import TripActionButtons from '@/components/trip/TripActionButtons.vue'
import CommentSection from '@/components/CommentSection.vue'

export default {
  name: 'TripDetailView',
  
  components: {
    NavBar,
    TripHeader,
    TripProgress,
    TripOverview,
    TripBasicInfo,
    TripHighlights,
    TripItinerary,
    TripBudget,
    TripTips,
    TripStats,
    TripActionButtons,
    CommentSection
  },
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    
    // 状态
    const trip = ref(null)
    const comments = ref([])
    const loading = ref(true)
    const error = ref(false)
    const errorMessage = ref('')
    const tripConfig = ref(null)
    const tripId = computed(() => parseInt(route.params.id))
    
    // 音乐相关
    const isPlaying = ref(false)
    const audioPlayer = ref(null)
    const musicSrc = computed(() => {
      const bg = trip.value?.background_music
      if (bg === '') return ''
      return bg || '/music/rain.mp3'
    })
    
    // 评论区引用
    const commentSectionRef = ref(null)
    
    // 权限相关
    const isAdmin = computed(() => userStore.isAdmin)
    const isAuthor = computed(() => {
      return trip.value?.author?.id === userStore.userInfo?.id
    })
    const isAuthenticated = computed(() => userStore.isLoggedIn)
    
    // 是否有行程安排
    const hasItinerary = computed(() => {
      return tripConfig.value?.overview?.itinerary && tripConfig.value.overview.itinerary.length > 0
    })
    
    
    // 登录校验
    const ensureLoggedIn = () => {
      if (!userStore.isLoggedIn) {
        const next = encodeURIComponent(route.fullPath)
        router.push(`/login?next=${next}`)
        return false
      }
      return true
    }
    
    // 获取旅行详情
    const fetchTripDetail = async () => {
      const slug = route.params.slug
      try {
        loading.value = true
        const response = await getTripDetail(slug)
        trip.value = response
        
        // 确保 stats 存在
        if (!trip.value.stats) {
          trip.value.stats = { views: 0, likes: 0 }
        }
        
        // 加载配置
        tripConfig.value = getTripConfig(slug)
        
        // 加载评论
        await fetchComments()
        
        // 记录浏览量并刷新统计
        if (trip.value.overview) {
          await viewTripPlan(slug)
          // 刷新统计数据
          const statsResponse = await getTripPlanStats(slug)
          trip.value.stats.views = statsResponse.views
          trip.value.stats.likes = statsResponse.likes
        }
      } catch (err) {
        console.error('获取旅行详情失败:', err)
        error.value = true
        // 根据错误类型设置友好提示
        const status = err.response?.status || err.status
        if (status === 404) {
          errorMessage.value = err.response?.data?.detail || '该旅行计划不存在或已被删除'
        } else if (status === 403) {
          errorMessage.value = '您没有权限访问该旅行计划'
        } else if (status === 502 || status === 503) {
          errorMessage.value = '服务器暂时无法访问，请稍后再试'
        } else {
          errorMessage.value = '加载失败，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    // 获取评论列表
    let fetchingComments = false
    const fetchComments = async () => {
      // 防止重复调用
      if (fetchingComments) return
      fetchingComments = true
      
      try {
        // 后端 CommentFilter 使用 'trip' 参数映射到 'page' 字段
        const response = await getCommentList({ trip: trip.value.slug })
        comments.value = response.results || response || []
      } catch (error) {
        console.error('❌ 获取评论失败:', error)
      } finally {
        fetchingComments = false
      }
    }
    
    // 点赞（旅行点赞不需要登录，允许重复点赞）
    const handleLike = async () => {
      try {
        // 立即更新 UI（乐观更新）
        if (!trip.value.stats) {
          trip.value.stats = { views: 0, likes: 0 }
        }
        trip.value.stats.likes += 1
        
        // 发送点赞请求
        if (trip.value.overview) {
          await likeTripPlan(trip.value.slug)
        } else {
          await likeTrip(tripId.value)
        }
        
        // 后台刷新统计（确保数据准确）
        const statsResponse = trip.value.overview 
          ? await getTripPlanStats(trip.value.slug)
          : await getTripStats(tripId.value)
        
        trip.value.stats.likes = statsResponse.likes
        trip.value.stats.views = statsResponse.views
      } catch (error) {
        console.error('点赞失败:', error)
        // 如果失败，回滚
        if (trip.value.stats) {
          trip.value.stats.likes -= 1
        }
      }
    }
    
    // 提交评论
    const handleSubmitComment = async (payload) => {
      if (!ensureLoggedIn()) return
      
      // payload 格式: { data: { content, image, video }, onProgress, onComplete }
      const { data, onProgress, onComplete } = payload
      const { content, image, video } = data
      
      try {
        // 使用 FormData 一次性提交（包含文件）
        const formData = new FormData()
        formData.append('content', content || '')
        formData.append('page', trip.value.slug)
        
        if (image) {
          formData.append('image', image)
        }
        if (video) {
          formData.append('video', video)
        }
        
        await createComment(formData, onProgress)
        
        // 刷新评论列表
        await fetchComments()
        
        // 成功提示
        alert('✅ 评论发表成功！')
        
        // 调用完成回调
        if (onComplete) {
          onComplete()
        }
      } catch (error) {
        console.error('提交评论失败:', error)
        alert('❌ 评论发表失败：' + (error.response?.data?.detail || error.message))
        
        // 即使失败也要调用完成回调
        if (onComplete) {
          onComplete()
        }
      }
    }
    
    // 删除评论
    const handleDeleteComment = async (commentId) => {
      // 删除前确认
      if (!confirm('确定要删除这条评论吗？此操作无法撤销。')) {
        return
      }
      
      try {
        await deleteComment(commentId)
        await fetchComments()
      } catch (error) {
        console.error('删除评论失败:', error)
      }
    }
    
    // 添加图片
    const handleAddImage = async (commentId, file, type) => {
      try {
        await addCommentImage(commentId, file, type)
        await fetchComments()
      } catch (error) {
        console.error('添加图片失败:', error)
      }
    }
    
    // 更新评论
    const handleUpdateComment = async (commentId, content) => {
      try {
        await updateComment(commentId, { content })
        await fetchComments()
      } catch (error) {
        console.error('更新评论失败:', error)
      }
    }
    
    // 提交回复
    const handleSubmitReply = async (payload) => {
      if (!ensureLoggedIn()) return
      
      // payload 格式: { commentId, content }
      const { commentId, content } = payload
      
      try {
        await createComment({
          content,
          page: trip.value.slug,
          parent: commentId
        })
        await fetchComments()
        alert('✅ 回复成功！')
      } catch (error) {
        console.error('❌ 提交回复失败:', error)
        alert('❌ 回复失败：' + (error.response?.data?.detail || error.message))
      }
    }
    
    // 提交嵌套回复
    const handleSubmitNestedReply = async (payload) => {
      // payload 格式: { parentId, content }
      const { parentId, content } = payload
      await handleSubmitReply({ commentId: parentId, content })
    }
    
    // 加载回复
    const handleLoadReplies = async (commentId) => {
      try {
        return await getCommentReplies(commentId)
      } catch (error) {
        console.error('加载回复失败:', error)
        return []
      }
    }
    
    // 点赞回复
    const handleLikeReply = async (replyId) => {
      if (!ensureLoggedIn()) return
      
      try {
        await likeComment(replyId)
        await fetchComments()
      } catch (error) {
        console.error('点赞回复失败:', error)
      }
    }
    
    // 返回上一页或首页
    const goBack = () => {
      // 如果有历史记录，返回上一页；否则跳转到首页
      if (window.history.length > 1) {
        router.back()
      } else {
        router.push('/')
      }
    }
    
    // 切换音乐
    const toggleMusic = () => {
      if (!audioPlayer.value) return
      
      if (isPlaying.value) {
        audioPlayer.value.pause()
      } else {
        audioPlayer.value.play()
      }
      isPlaying.value = !isPlaying.value
    }
    
    // 滚动到评论区
    const scrollToComments = () => {
      if (commentSectionRef.value?.$el) {
        commentSectionRef.value.$el.scrollIntoView({ behavior: 'smooth' })
      }
    }
    
    // 生命周期
    onMounted(() => {
      fetchTripDetail()
    })
    
    onUnmounted(() => {
      if (audioPlayer.value) {
        audioPlayer.value.pause()
      }
    })
    
    return {
      trip,
      tripId,
      comments,
      loading,
      error,
      errorMessage,
      tripConfig,
      router,
      isAdmin,
      isPlaying,
      audioPlayer,
      musicSrc,
      commentSectionRef,
      isAuthor,
      isAuthenticated,
      hasItinerary,
      handleLike,
      handleSubmitComment,
      handleDeleteComment,
      handleAddImage,
      handleUpdateComment,
      handleSubmitReply,
      handleSubmitNestedReply,
      handleLikeReply,
      handleLoadReplies,
      goBack,
      toggleMusic,
      scrollToComments,
      getAvatarUrl
    }
  }
}
</script>

<style scoped>
.trip-detail-container {
  min-height: 100vh;
  transition: background 0.5s ease;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.text-center {
  padding: 3rem 0;
}

/* 错误提示卡片 */
.error-card {
  background: white;
  border-radius: 20px;
  padding: 3rem 2rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.6;
}

.error-title {
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.error-description {
  color: #666;
  font-size: 1rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}
</style>

