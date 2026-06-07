<template>
  <div v-if="show" class="profile-popover-overlay" @click="handleClose">
    <div class="profile-popover" @click.stop>
      <!-- 关闭按钮 -->
      <button class="close-btn" @click="handleClose" title="关闭">×</button>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
      </div>
      
      <!-- 用户资料 -->
      <div v-else-if="userProfile" class="profile-content">
        <!-- 头像和基本信息 -->
        <div class="profile-header">
          <div class="avatar-container">
            <img 
              :src="getAvatarUrl(userProfile.profile?.avatar_url)" 
              :alt="userProfile.username"
              class="avatar"
              @error="handleAvatarError"
            />
          </div>
          <h5 class="username">{{ userProfile.username }}</h5>
          <p v-if="userProfile.email && !hideEmail" class="email">{{ userProfile.email }}</p>
          
          <!-- 等级徽章 -->
          <div class="badges">
            <span class="badge" :class="getLevelClass(userProfile.profile?.level)">
              {{ getLevelText(userProfile.profile?.level) }}
            </span>
          </div>
          
          <!-- 注册时间 -->
          <p class="register-time">注册时间: {{ formatDate(userProfile.date_joined) }}</p>
        </div>
        
        <!-- 统计数据 -->
        <div class="stats-section">
          <div class="stats-title">
            <span class="icon">📊</span>
            <span>TA的统计</span>
          </div>
          
          <div class="main-stat">
            <h3>{{ userProfile.stats.comments_count }}</h3>
            <p>评论数</p>
          </div>
          
          <div class="sub-stats">
            <div class="stat-box">
              <h4>{{ userProfile.stats.trips_count }}</h4>
              <p>总旅行数</p>
            </div>
            <div class="stat-box">
              <h4>{{ userProfile.stats.public_trips_count }}</h4>
              <p>公开旅行</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 错误状态 -->
      <div v-else class="error-state">
        <p>😔 加载失败</p>
        <button class="btn btn-sm btn-outline-primary" @click="loadUserProfile">重试</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getUserProfile } from '@/api/user'
import { DEFAULT_AVATAR_SVG, getAvatarUrl as getAvatar } from '@/config/api'

export default {
  name: 'UserProfilePopover',
  
  props: {
    show: {
      type: Boolean,
      default: false
    },
    userId: {
      type: Number,
      default: null
    },
    hideEmail: {
      type: Boolean,
      default: true
    }
  },
  
  emits: ['close'],
  
  setup(props, { emit }) {
    const router = useRouter()
    const loading = ref(false)
    const userProfile = ref(null)
    
    // 监听 userId 变化，加载用户资料
    watch(() => props.userId, (newUserId) => {
      if (newUserId && props.show) {
        loadUserProfile()
      }
    }, { immediate: true })
    
    // 监听 show 变化
    watch(() => props.show, (newShow) => {
      if (newShow && props.userId && !userProfile.value) {
        loadUserProfile()
      }
    })
    
    const loadUserProfile = async () => {
      if (!props.userId) return
      
      loading.value = true
      try {
        const data = await getUserProfile(props.userId)
        userProfile.value = data
      } catch (error) {
        console.error('加载用户资料失败:', error)
        userProfile.value = null
      } finally {
        loading.value = false
      }
    }
    
    const handleClose = () => {
      emit('close')
    }
    
    const getAvatarUrl = (avatarUrl) => {
      return getAvatar(avatarUrl)
    }
    
    const handleAvatarError = (e) => {
      e.target.src = DEFAULT_AVATAR_SVG
      e.target.onerror = null
    }
    
    const formatDate = (dateStr) => {
      if (!dateStr) return '未知'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    }
    
    const getLevelText = (level) => {
      const levels = {
        'novice': '新手',
        'explorer': '探索者',
        'wanderer': '漫游者',
        'adventurer': '冒险家',
        'master': '旅行大师'
      }
      return levels[level] || '新手'
    }
    
    const getLevelClass = (level) => {
      const classes = {
        'novice': 'badge-novice',
        'explorer': 'badge-explorer',
        'wanderer': 'badge-wanderer',
        'adventurer': 'badge-adventurer',
        'master': 'badge-master'
      }
      return classes[level] || 'badge-novice'
    }
    
    const viewUserTrips = () => {
      // TODO: 跳转到用户的旅行列表页面
      // 暂时跳转到旅行大厅，未来可以添加用户筛选
      router.push('/trips')
      handleClose()
    }
    
    return {
      loading,
      userProfile,
      handleClose,
      getAvatarUrl,
      handleAvatarError,
      formatDate,
      getLevelText,
      getLevelClass,
      viewUserTrips,
      loadUserProfile
    }
  }
}
</script>

<style scoped>
.profile-popover-overlay {
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
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.profile-popover {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: #f8f9fa;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e9ecef;
  color: #495057;
  transform: rotate(90deg);
}

.loading-state,
.error-state {
  text-align: center;
  padding: 2rem 0;
}

.error-state p {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-header {
  text-align: center;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.avatar-container {
  margin-bottom: 1rem;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.username {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0.5rem 0;
}

.email {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0.5rem 0;
}

.badges {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin: 1rem 0;
}

.badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
  border: 1px solid transparent;
}

.badge-admin {
  background: var(--bs-danger-bg-subtle, #fef2f2);
  color: var(--bs-danger-text-emphasis, #991b1b);
  border-color: var(--bs-danger-border-subtle, #fecaca);
}

.badge-novice {
  background: var(--bs-secondary-bg-subtle, #f8fafc);
  color: var(--bs-secondary-text-emphasis, #475569);
  border-color: var(--bs-secondary-border-subtle, #e2e8f0);
}

.badge-explorer {
  background: var(--bs-primary-bg-subtle, var(--roamio-primary-muted));
  color: var(--roamio-primary-active);
  border-color: var(--bs-primary-border-subtle, #99f6e4);
}

.badge-wanderer {
  background: var(--bs-success-bg-subtle, #f0fdf4);
  color: var(--bs-success-text-emphasis, #166534);
  border-color: var(--bs-success-border-subtle, #bbf7d0);
}

.badge-adventurer {
  background: var(--bs-warning-bg-subtle, #fffbeb);
  color: var(--bs-warning-text-emphasis, #92400e);
  border-color: var(--bs-warning-border-subtle, #fde68a);
}

.badge-master {
  background: #fff7ed;
  color: #9a3412;
  border-color: #fed7aa;
}

.register-time {
  font-size: 0.85rem;
  color: #6c757d;
  margin: 0.5rem 0 0 0;
}

.stats-section {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 1.5rem;
}

.stats-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.stats-title .icon {
  font-size: 1.2rem;
}

.main-stat {
  text-align: center;
  margin-bottom: 1rem;
}

.main-stat h3 {
  font-size: 2.5rem;
  font-weight: 700;
  background: var(--roamio-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.main-stat p {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0.5rem 0 0 0;
}

.sub-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stat-box {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
}

.stat-box h4 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #28a745;
  margin: 0;
}

.stat-box:last-child h4 {
  color: #fd7e14;
}

.stat-box p {
  color: #6c757d;
  font-size: 0.85rem;
  margin: 0.5rem 0 0 0;
}

.actions {
  padding-top: 1rem;
}

.btn-primary {
  background: var(--roamio-primary);
  border: none;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(var(--bs-primary-rgb), 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--bs-primary-rgb), 0.6);
}

@media (max-width: 576px) {
  .profile-popover {
    padding: 1.5rem;
    max-width: 95%;
  }
  
  .avatar {
    width: 80px;
    height: 80px;
  }
  
  .username {
    font-size: 1.3rem;
  }
}
</style>

