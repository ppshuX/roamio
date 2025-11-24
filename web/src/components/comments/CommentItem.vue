<template>
  <div class="comment-item">
    <div class="d-flex align-items-start">
      <img
        :src="getAvatarUrl(comment.user.profile?.avatar_url)"
        class="rounded-circle me-3 user-avatar"
        width="48"
        height="48"
        alt="avatar"
        loading="lazy"
        @error="handleAvatarError"
        @click="showUserProfile"
        title="查看用户资料"
      />
      <div class="flex-grow-1">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <strong class="username-link" @click="showUserProfile" title="查看用户资料">
            {{ comment.user.username }}
          </strong>
          <div class="d-flex gap-2 align-items-center actions-wrap">
            <small class="text-muted">{{ formatDate(comment.timestamp) }}</small>
            <!-- 操作按钮 -->
            <slot name="actions"></slot>
          </div>
        </div>
        
        <!-- 编辑模式：显示编辑框 -->
        <div v-if="editing" class="mb-2">
          <textarea
            v-model="localContent"
            class="form-control"
            rows="3"
            placeholder="编辑评论内容..."
          ></textarea>
        </div>
        <!-- 普通模式：显示原内容 -->
        <p v-else class="mb-2">{{ comment.content }}</p>
        
        <!-- 图片 -->
        <div v-if="comment.image" class="mb-2 comment-media">
          <img
            :src="comment.image"
            class="comment-image rounded"
            style="cursor: pointer;"
            @click="$emit('show-image-modal', comment.image)"
            alt="评论图片"
            loading="lazy"
          />
        </div>
        
        <!-- 视频 -->
        <div v-if="comment.video" class="mb-2 comment-media">
          <video
            ref="videoRef"
            :src="shouldLoadVideo ? comment.video : null"
            controls
            :preload="shouldLoadVideo ? 'metadata' : 'none'"
            class="rounded"
            @loadstart="onVideoLoadStart"
          >
            您的浏览器不支持视频播放
          </video>
        </div>
        
        <!-- 回复按钮 -->
        <div class="mt-3 pt-2 border-top border-light d-flex gap-2 align-items-center">
          <button
            class="btn btn-sm btn-link text-primary p-0 reply-toggle-btn"
            @click="$emit('toggle-reply', comment.id)"
          >
            💬 {{ isExpanded ? '收起回复' : '回复' }}
          </button>
          <span v-if="replyCount" class="text-muted small">
            ({{ replyCount }}条回复)
          </span>
        </div>
      </div>
    </div>
    
    <!-- 回复区域 - 作为评论的一部分 -->
    <div v-if="isExpanded" class="replies-container">
      <slot name="replies"></slot>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { DEFAULT_AVATAR_SVG } from '@/config/api'

export default {
  name: 'CommentItem',
  
  props: {
    comment: {
      type: Object,
      required: true
    },
    editing: {
      type: Boolean,
      default: false
    },
    isExpanded: {
      type: Boolean,
      default: false
    },
    replyCount: {
      type: Number,
      default: 0
    },
    replies: {
      type: Array,
      default: () => []
    },
    getAvatarUrl: {
      type: Function,
      required: true
    }
  },
  
  emits: ['show-image-modal', 'toggle-reply', 'update:content', 'show-user-profile'],
  
  setup(props, { emit }) {
    const localContent = ref(props.comment.content)
    const videoRef = ref(null)
    const shouldLoadVideo = ref(false)
    let observer = null
    
    // 视频懒加载：使用 IntersectionObserver
    onMounted(() => {
      if (props.comment.video) {
        // 等待 DOM 渲染完成
        nextTick(() => {
          if (videoRef.value) {
            // 检查浏览器是否支持 IntersectionObserver
            if ('IntersectionObserver' in window) {
              observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                  if (entry.isIntersecting) {
                    shouldLoadVideo.value = true
                    // 加载后停止观察
                    if (observer && videoRef.value) {
                      observer.unobserve(videoRef.value)
                    }
                  }
                })
              }, {
                rootMargin: '50px' // 提前50px开始加载
              })
              
              observer.observe(videoRef.value)
            } else {
              // 不支持 IntersectionObserver 的浏览器，直接加载
              shouldLoadVideo.value = true
            }
          }
        })
      }
    })
    
    onUnmounted(() => {
      if (observer && videoRef.value) {
        observer.unobserve(videoRef.value)
        observer = null
      }
    })
    
    const onVideoLoadStart = () => {
      // 视频开始加载时的回调
    }
    
    watch(() => props.comment.content, (newVal) => {
      localContent.value = newVal
    })
    
    watch(localContent, (newVal) => {
      emit('update:content', newVal)
    })
    
    const showUserProfile = () => {
      emit('show-user-profile', props.comment.user.id)
    }
    
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      
      return `${year}-${month}-${day} ${hours}:${minutes}`
    }
    
    // 头像加载失败处理：降级到 SVG
    const handleAvatarError = (e) => {
      console.log('头像加载失败，使用 SVG 备用头像')
      e.target.src = DEFAULT_AVATAR_SVG
      // 防止无限循环：如果 SVG 也失败，移除 error 事件
      e.target.onerror = null
    }
    
    return {
      localContent,
      formatDate,
      handleAvatarError,
      showUserProfile,
      videoRef,
      shouldLoadVideo,
      onVideoLoadStart
    }
  }
}
</script>

<style scoped>
.comment-item {
  background: #f0f0f0;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
  overflow: hidden;
  word-wrap: break-word;
}

.comment-item:hover {
  background: #e8e8e8;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.comment-item:last-child {
  margin-bottom: 0;
}

.comment-item p {
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
}

.rounded-circle {
  border: 2px solid #e0e0e0;
  object-fit: cover;
}

.user-avatar {
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.username-link {
  cursor: pointer;
  transition: all 0.3s ease;
}

.username-link:hover {
  color: #667eea;
  text-decoration: underline;
}

.comment-media {
  margin-top: 1rem;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.comment-media img.comment-image {
  max-width: 100%;
  max-height: 500px;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 8px;
}

.comment-media img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.comment-media video {
  max-width: 100%;
  max-height: 600px;
  width: auto;
  height: auto;
  border-radius: 8px;
  display: block;
  margin: 0 auto;
}

.btn-link.text-primary {
  text-decoration: none;
  font-size: 0.875rem;
}

.btn-link.text-primary:hover {
  text-decoration: underline;
}

/* 回复容器 */
.replies-container {
  margin-top: 0;
  padding: 1rem;
  background: linear-gradient(to right, #ffffff 0%, #f8f9fa 100%);
  border-radius: 0 0 12px 12px;
  border-top: 2px solid #e9ecef;
}

.reply-toggle-btn {
  font-weight: 500;
  transition: all 0.2s ease;
  text-decoration: none !important;
}

.reply-toggle-btn:hover {
  transform: translateX(2px);
  text-decoration: none !important;
}

/* 让操作区在移动端自动换行，避免溢出 */
.actions-wrap {
  flex-wrap: wrap;
  row-gap: 6px;
  column-gap: 8px;
  min-width: 0;
}

@media (max-width: 768px) {
  .comment-item {
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .comment-item img.rounded-circle {
    width: 40px;
    height: 40px;
  }
  
  .comment-media img.comment-image {
    max-width: 100%;
    max-height: 300px;
    width: auto;
    height: auto;
    object-fit: contain;
  }
  
  .replies-container {
    padding: 0.75rem;
  }
  .actions-wrap {
    max-width: 60%;
    justify-content: flex-end;
  }
}
</style>
