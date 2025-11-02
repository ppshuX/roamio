<template>
  <div class="reply-item-wrapper">
    <div class="reply-item">
      <!-- 回复头部 -->
      <div class="d-flex align-items-start">
        <img
          :src="getAvatarUrl(reply.user.profile?.avatar_url)"
          class="rounded-circle me-2 flex-shrink-0"
          width="32"
          height="32"
          alt="avatar"
          @error="handleAvatarError"
        />
        <div class="flex-grow-1">
          <!-- 用户名和时间 -->
          <div class="d-flex justify-content-between align-items-center mb-1">
            <div>
              <strong class="small">{{ reply.user.username }}</strong>
              <!-- 如果是回复别人的回复，显示"回复了xxx的评论" -->
              <span v-if="parentUsername" class="text-muted small ms-1">
                回复了 {{ parentUsername }} 的评论
              </span>
            </div>
            <small class="text-muted flex-shrink-0 ms-2">{{ formatDate(reply.timestamp) }}</small>
          </div>
          
          <!-- 回复内容 -->
          <p class="mb-2 small">{{ reply.content }}</p>
          
          <!-- 操作按钮 -->
          <div class="reply-actions d-flex gap-2 align-items-center">
            <button 
              class="action-btn"
              @click="$emit('toggle-reply', reply.id)"
              title="回复"
            >
              <span class="action-icon">💬</span>
              <span class="action-text">回复</span>
            </button>
            
            <button
              v-if="reply.can_delete"
              class="action-btn text-danger"
              @click="$emit('delete-reply', reply.id)"
              title="删除此回复"
            >
              <span class="action-icon">🗑️</span>
            </button>
          </div>
          
          <!-- 回复表单（折叠） -->
          <div v-if="showingReplyForm" class="reply-form mt-2">
            <textarea
              v-model="replyContent"
              class="form-control form-control-sm"
              rows="2"
              :placeholder="`回复 ${reply.user.username}...`"
            ></textarea>
            <div class="mt-2 d-flex gap-2">
              <button
                class="btn btn-sm btn-primary"
                @click="handleSubmitReply"
                :disabled="!replyContent.trim()"
              >
                提交
              </button>
              <button
                class="btn btn-sm btn-outline-secondary"
                @click="showingReplyForm = false; replyContent = ''"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 递归渲染嵌套回复 -->
    <div v-if="reply.replies && reply.replies.length > 0" class="nested-replies">
      <ReplyItem
        v-for="nestedReply in reply.replies"
        :key="nestedReply.id"
        :reply="nestedReply"
        :get-avatar-url="getAvatarUrl"
        :parent-username="reply.user.username"
        :depth="depth + 1"
        :active-reply-id="activeReplyId"
        @toggle-reply="$emit('toggle-reply', $event)"
        @submit-reply="$emit('submit-reply', $event)"
        @delete-reply="$emit('delete-reply', $event)"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ReplyItem',
  
  props: {
    reply: {
      type: Object,
      required: true
    },
    getAvatarUrl: {
      type: Function,
      required: true
    },
    parentUsername: {
      type: String,
      default: null
    },
    depth: {
      type: Number,
      default: 1
    },
    activeReplyId: {
      type: Number,
      default: null
    }
  },
  
  emits: ['toggle-reply', 'submit-reply', 'delete-reply'],
  
  setup(props, { emit }) {
    const replyContent = ref('')
    
    const showingReplyForm = computed(() => {
      return props.activeReplyId === props.reply.id
    })
    
    const handleAvatarError = (e) => {
      e.target.src = '/static/images/default_avatar.png'
    }
    
    const handleSubmitReply = () => {
      const content = replyContent.value.trim()
      if (content) {
        emit('submit-reply', {
          parentId: props.reply.id,
          content: content
        })
        replyContent.value = ''
      }
    }
    
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      const now = new Date()
      const diff = now - date
      
      // 刚刚（1分钟内）
      if (diff < 60000) {
        return '刚刚'
      }
      
      // X分钟前
      if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`
      }
      
      // X小时前
      if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`
      }
      
      // X天前
      if (diff < 2592000000) {
        return `${Math.floor(diff / 86400000)}天前`
      }
      
      // 完整日期
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      
      return `${year}-${month}-${day} ${hours}:${minutes}`
    }
    
    return {
      replyContent,
      showingReplyForm,
      handleAvatarError,
      handleSubmitReply,
      formatDate
    }
  }
}
</script>

<style scoped>
.reply-item-wrapper {
  position: relative;
}

.reply-item {
  padding: 0.75rem;
  background: #ffffff;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  border-left: 2px solid #667eea;
  transition: all 0.2s ease;
}

.reply-item:hover {
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  transform: translateX(2px);
}

.reply-item img {
  flex-shrink: 0;
  object-fit: cover;
}

.reply-actions {
  margin-top: 0.25rem;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  color: #6c757d;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
  border-radius: 4px;
}

.action-btn:hover {
  background: #f8f9fa;
  color: #667eea;
}

.action-btn.text-danger:hover {
  background: #fff5f5;
  color: #dc3545;
}

.action-icon {
  font-size: 0.9rem;
}

.action-text {
  font-size: 0.85rem;
}

.reply-form {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.reply-form textarea {
  font-size: 0.9rem;
  background: white;
  border: 1px solid #dee2e6;
}

/* 嵌套回复样式 */
.nested-replies {
  margin-left: 2.5rem;
  margin-top: 0.5rem;
  position: relative;
}

/* 连接线 */
.nested-replies::before {
  content: '';
  position: absolute;
  left: -1.25rem;
  top: 0;
  bottom: 0.5rem;
  width: 2px;
  background: linear-gradient(to bottom, #dee2e6 0%, #dee2e6 90%, transparent 100%);
}

/* 深度缩进限制（最多5层） */
.reply-item-wrapper {
  max-width: 100%;
}

@media (max-width: 768px) {
  .nested-replies {
    margin-left: 1.5rem;
  }
  
  .nested-replies::before {
    left: -0.75rem;
  }
  
  .reply-item {
    padding: 0.5rem;
  }
  
  .reply-item img {
    width: 28px !important;
    height: 28px !important;
  }
}
</style>

