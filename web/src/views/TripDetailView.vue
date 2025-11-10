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
      } catch (error) {
        console.error('获取旅行详情失败:', error)
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
    
    // 点赞
    const handleLike = async () => {
      if (!ensureLoggedIn()) return
      
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
        const commentData = {
          content,
          page: trip.value.slug  // 后端字段是 page，不是 trip
        }
        
        const newComment = await createComment(commentData, onProgress)
        
        // 上传图片或视频
        if (image) {
          await addCommentImage(newComment.id, image, 'image', onProgress)
        } else if (video) {
          await addCommentImage(newComment.id, video, 'video', onProgress)
        }
        
        // 刷新评论列表
        await fetchComments()
        
        // 调用完成回调
        if (onComplete) {
          onComplete()
        }
      } catch (error) {
        console.error('提交评论失败:', error)
        
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
      } catch (error) {
        console.error('❌ 提交回复失败:', error)
        console.error('错误详情:', error.response?.data)
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
    
    // 返回首页
    const goBack = () => {
      router.push('/')
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
      tripConfig,
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
</style>

