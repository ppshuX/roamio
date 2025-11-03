<template>
  <div v-if="expanded" class="reply-section">
    <!-- 回复表单 -->
    <div class="reply-form mb-3">
      <textarea
        v-model="replyContent"
        class="form-control form-control-sm"
        rows="2"
        placeholder="写下你的回复..."
      ></textarea>
      <div class="mt-2 d-flex gap-2">
        <button
          class="btn btn-sm btn-primary"
          @click="handleSubmit"
          :disabled="submitting"
        >
          <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
          {{ submitting ? '提交中...' : '提交回复' }}
        </button>
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="handleCancel"
        >
          取消
        </button>
      </div>
    </div>
    
    <!-- 回复列表 -->
    <div v-if="replies && replies.length > 0" class="reply-list">
      <div
        v-for="reply in replies"
        :key="reply.id"
        class="reply-item mt-2 ps-3 border-start border-secondary"
      >
        <div class="d-flex align-items-start">
          <img
            :src="getAvatarUrl(reply.user.profile?.avatar_url)"
            class="rounded-circle me-2"
            width="32"
            height="32"
            loading="lazy"
            alt="avatar"
            @error="handleAvatarError"
          />
          <div class="flex-grow-1">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <strong class="small">{{ reply.user.username }}</strong>
              <div class="d-flex gap-2 align-items-center">
                <small class="text-muted">{{ formatDate(reply.timestamp) }}</small>
                <!-- 删除按钮 -->
                <button
                  v-if="reply.can_delete"
                  class="btn btn-sm p-0 text-danger"
                  style="border: none; background: none; font-size: 0.8rem;"
                  @click="$emit('delete-reply', reply.id)"
                  title="删除此回复"
                >
                  🗑️
                </button>
              </div>
            </div>
            <p class="mb-0 small">{{ reply.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { DEFAULT_AVATAR_SVG } from '@/config/api'

export default {
  name: 'ReplySection',
  
  props: {
    expanded: {
      type: Boolean,
      default: false
    },
    replies: {
      type: Array,
      default: () => []
    },
    submitting: {
      type: Boolean,
      default: false
    },
    getAvatarUrl: {
      type: Function,
      required: true
    }
  },
  
  emits: ['submit', 'cancel', 'delete-reply'],
  
  setup(props, { emit }) {
    const replyContent = ref('')
    
    watch(() => props.expanded, (newVal) => {
      if (!newVal) {
        replyContent.value = ''
      }
    })
    
    const handleSubmit = () => {
      const content = replyContent.value.trim()
      if (content) {
        emit('submit', content)
        replyContent.value = ''
      }
    }
    
    const handleCancel = () => {
      replyContent.value = ''
      emit('cancel')
    }
    
    // 头像加载失败处理：降级到 SVG
    const handleAvatarError = (e) => {
      console.log('头像加载失败，使用 SVG 备用头像')
      e.target.src = DEFAULT_AVATAR_SVG
      // 防止无限循环：如果 SVG 也失败，移除 error 事件
      e.target.onerror = null
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
    
    return {
      replyContent,
      handleSubmit,
      handleCancel,
      handleAvatarError,
      formatDate
    }
  }
}
</script>

<style scoped>
.reply-section {
  /* 回复区域作为评论的一部分，不需要额外背景 */
  margin-top: 0.5rem;
}

.reply-form {
  margin-bottom: 1rem;
}

.reply-form textarea {
  font-size: 0.9rem;
  background: white;
  border: 1px solid #dee2e6;
}

.reply-item {
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  border-left: 3px solid #667eea;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.reply-item:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transform: translateX(2px);
}

.reply-item:last-child {
  margin-bottom: 0;
}

.reply-item img {
  flex-shrink: 0;
}

.reply-item a {
  text-decoration: none;
}

.reply-item a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .reply-section {
    padding: 0.75rem;
  }
  
  .reply-item {
    padding: 0.5rem;
    margin-bottom: 0.5rem;
  }
}
</style>
