<template>
  <div class="card">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h3 class="mb-0">🌳 Roamio Stories.</h3>
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="toggleOrder"
          :title="isReversed ? '恢复时间顺序' : '最新记录在前'"
          style="font-size: 0.85rem;"
        >
          {{ isReversed ? '↓' : '↑' }}
        </button>
      </div>
      
      <!-- 发表评论入口（仅作者可见） -->
      <div v-if="isAuthor" class="mb-3">
        <button
          v-if="!showForm"
          class="btn btn-outline-primary"
          @click="showForm = true"
        >
          ✍️ 记录一下
        </button>
        <button
          v-else
          class="btn btn-outline-secondary mb-3"
          @click="showForm = false"
        >
          取消记录
        </button>
      </div>
      <CommentForm
        v-if="isAuthor && showForm"
        ref="commentFormRef"
        :submitting="submitting"
        @submit="handleSubmit"
      />
      
      <!-- 评论列表 -->
      <div class="comment-list">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="mb-0">记录列表 ({{ comments.length }}条)</h5>
          <!-- 管理评论模式切换按钮 -->
          <button
            v-if="hasManageableComments"
            class="btn btn-sm"
            :class="isManageMode ? 'btn-secondary' : 'btn-outline-secondary'"
            @click="toggleManageMode"
            title="管理评论"
          >
            {{ isManageMode ? '完成管理' : '管理评论' }}
          </button>
        </div>
        
        <div v-if="comments.length === 0" class="text-center text-muted py-4">
          暂无记录，快来留下你的旅行脚印吧！
        </div>
        
        <CommentItem
          v-for="comment in displayedComments"
          :key="comment.id"
          :comment="comment"
          :editing="editingComments[comment.id] !== undefined && editingComments[comment.id] !== false"
          :is-expanded="expandedReplies[comment.id] || false"
          @show-user-profile="handleShowUserProfile"
          :reply-count="(replyLists[comment.id] || []).length"
          :replies="replyLists[comment.id] || []"
          :get-avatar-url="getAvatarUrl"
          @show-image-modal="showImageModal"
          @toggle-reply="toggleReplySection"
          @update:content="(content) => updateLocalContent(comment.id, content)"
        >
          <!-- 操作按钮插槽 -->
          <template #actions>
                  <template v-if="isManageMode">
                    <!-- 编辑模式按钮 -->
                    <button
                      v-if="comment.can_delete && !editingComments[comment.id]"
                      class="btn btn-sm btn-outline-primary"
                      @click="startEditing(comment.id, comment.content)"
                      title="编辑评论"
                    >
                      ✏️
                    </button>
                    <!-- 保存按钮 -->
                    <button
                      v-if="editingComments[comment.id]"
                      class="btn btn-sm btn-success"
                      @click="handleSaveComment(comment.id)"
                      title="保存修改"
                    >
                      ✓
                    </button>
              <!-- 添加/替换图片按钮 -->
                    <button
                      v-if="canAddImage(comment) && editingComments[comment.id]"
                      class="btn btn-sm btn-outline-success"
                      @click="handleAddImage(comment.id)"
                      :title="comment.image ? '替换图片' : '添加图片'"
                    >
                      📷
                    </button>
                    <!-- 取消编辑按钮 -->
                    <button
                      v-if="editingComments[comment.id]"
                      class="btn btn-sm btn-outline-secondary"
                      @click="cancelEditing(comment.id)"
                      title="取消"
                    >
                      ✕
                    </button>
              <!-- 删除按钮 -->
                    <button
                      v-if="comment.can_delete"
                      class="btn btn-sm btn-outline-danger"
                      @click="handleDelete(comment.id)"
                      title="删除这条评论"
                    >
                      🗑️
                    </button>
                  </template>
          </template>
          
          <!-- 回复区域插槽 -->
          <template #replies>
            <div v-if="expandedReplies[comment.id]" class="reply-section-wrapper mt-3">
              <!-- 回复表单 -->
              <div class="reply-form mb-3">
                <textarea
                  v-model="replyForms[comment.id].content"
                  class="form-control form-control-sm"
                  rows="2"
                  placeholder="写下你的回复..."
                ></textarea>
                <div class="mt-2 d-flex gap-2">
                  <button
                    class="btn btn-sm btn-primary"
                    @click="handleSubmitReply(comment.id, replyForms[comment.id].content)"
                    :disabled="submittingReply[comment.id] || !replyForms[comment.id].content.trim()"
                  >
                    <span v-if="submittingReply[comment.id]" class="spinner-border spinner-border-sm me-1"></span>
                    {{ submittingReply[comment.id] ? '提交中...' : '提交回复' }}
                  </button>
                  <button
                    class="btn btn-sm btn-outline-secondary"
                    @click="cancelReply(comment.id)"
                  >
                    取消
                  </button>
                </div>
              </div>
              
              <!-- 递归渲染嵌套回复 -->
              <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
                <ReplyItem
                  v-for="reply in comment.replies"
                  :key="reply.id"
                  :reply="reply"
              :get-avatar-url="getAvatarUrl"
                  :active-reply-id="activeReplyId"
                  @toggle-reply="handleToggleNestedReply"
                  @submit-reply="handleSubmitNestedReply"
              @delete-reply="handleDeleteReply"
                  @like-reply="(replyId) => $emit('like-reply', replyId)"
            />
              </div>
            </div>
          </template>
        </CommentItem>
      </div>
    </div>
    
    <!-- 图片放大模态框 -->
    <div v-if="showModal" class="image-modal" @click="closeImageModal">
      <div class="modal-content" @click.stop>
        <button class="close-button" @click="closeImageModal">✕</button>
        <img :src="modalImageUrl" alt="放大图片" />
      </div>
    </div>
    
    <!-- 用户资料卡片 -->
    <UserProfilePopover
      :show="showUserProfilePopover"
      :user-id="selectedUserId"
      @close="closeUserProfile"
    />
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import CommentForm from './comments/CommentForm.vue'
import CommentItem from './comments/CommentItem.vue'
import ReplyItem from './comments/ReplyItem.vue'
import UserProfilePopover from './UserProfilePopover.vue'

export default {
  name: 'CommentSection',
  
  components: {
    CommentForm,
    CommentItem,
    ReplyItem,
    UserProfilePopover
  },
  
  props: {
    comments: {
      type: Array,
      default: () => []
    },
    isAdmin: {
      type: Boolean,
      default: false
    },
    isAuthor: {
      type: Boolean,
      default: false
    },
    getAvatarUrl: {
      type: Function,
      required: true
    }
  },
  
  emits: ['submit-comment', 'delete-comment', 'add-image', 'update-comment', 'submit-reply', 'load-replies', 'submit-nested-reply', 'like-reply'],
  
  setup(props, { emit }) {
    const submitting = ref(false)
    const showForm = ref(false)
    const editingComments = ref({})
    const isManageMode = ref(false)
    const showModal = ref(false)
    const modalImageUrl = ref('')
    const commentFormRef = ref(null)
    
    // 回复功能相关
    const expandedReplies = ref({})
    const replyForms = ref({})
    const submittingReply = ref({})
    const replyLists = ref({})
    const replyCounts = ref({})
    const activeReplyId = ref(null)  // 当前激活的回复表单ID
    
    // 翻转记录功能
    const isReversed = ref(false)
    
    // 用户资料卡片
    const showUserProfilePopover = ref(false)
    const selectedUserId = ref(null)
    
    // 计算属性
    const hasManageableComments = computed(() => {
      return props.comments.some(comment => comment.can_delete)
    })
    
    // 根据翻转状态显示评论列表
    const displayedComments = computed(() => {
      if (isReversed.value) {
        return [...props.comments].reverse()
      }
      return props.comments
    })

    // 默认展开包含媒体回复的评论，避免用户误以为“没有视频”
    watch(
      () => props.comments,
      (nextComments) => {
        if (!Array.isArray(nextComments)) return
        for (const comment of nextComments) {
          const hasMediaReply = Array.isArray(comment.replies) && comment.replies.some(
            (reply) => Boolean(reply?.video || reply?.image)
          )
          if (hasMediaReply) {
            expandedReplies.value[comment.id] = true
            if (!replyForms.value[comment.id]) {
              replyForms.value[comment.id] = { content: '' }
            }
            if (submittingReply.value[comment.id] === undefined) {
              submittingReply.value[comment.id] = false
            }
          }
        }
      },
      { immediate: true, deep: true }
    )
    
    // 切换排序顺序
    const toggleOrder = () => {
      isReversed.value = !isReversed.value
    }
    
    
    // 提交评论
    const handleSubmit = (commentData, onProgress) => {
      submitting.value = true
      
      // 创建一个包装的进度回调，在完成后重置进度条
      const wrappedProgress = (progressEvent) => {
        onProgress(progressEvent)
        
        // 当进度到 100% 时，标记为处理中
        if (progressEvent.percent >= 100) {
          // 等待父组件处理完成后再重置（由父组件控制）
        }
      }
      
      // 传递 payload 对象，包含 data 和包装后的进度回调
      emit('submit-comment', { 
        data: commentData, 
        onProgress: wrappedProgress,
        onComplete: () => {
          // 提交完成后的回调
        submitting.value = false
          // 延迟重置进度条
          if (commentFormRef.value && commentFormRef.value.resetProgress) {
            setTimeout(() => {
              commentFormRef.value.resetProgress()
            }, 1500)
          }
        }
      })
    }
    
    // 删除评论
    const handleDelete = (commentId) => {
      emit('delete-comment', commentId)
    }
    
    // 显示/关闭图片模态框
    const showImageModal = (url) => {
      modalImageUrl.value = url
      showModal.value = true
    }
    
    const closeImageModal = () => {
      showModal.value = false
      modalImageUrl.value = ''
    }
    
    // 显示用户资料卡片
    const handleShowUserProfile = (userId) => {
      selectedUserId.value = userId
      showUserProfilePopover.value = true
    }
    
    // 关闭用户资料卡片
    const closeUserProfile = () => {
      showUserProfilePopover.value = false
      selectedUserId.value = null
    }
    
    // 可以添加图片的判断
    const canAddImage = (comment) => {
      return !comment.video && comment.can_delete
    }
    
    // 编辑相关
    const startEditing = (commentId, originalContent) => {
      editingComments.value[commentId] = {
        isEditing: true,
        content: originalContent
      }
    }
    
    const cancelEditing = (commentId) => {
      editingComments.value[commentId] = false
    }
    
    const updateLocalContent = (commentId, content) => {
      if (editingComments.value[commentId]) {
        editingComments.value[commentId].content = content
      }
    }
    
    const handleSaveComment = (commentId) => {
      const editedContent = editingComments.value[commentId]?.content
      if (editedContent && editedContent.trim()) {
        emit('update-comment', {
          commentId,
          content: editedContent.trim()
        })
        editingComments.value[commentId] = false
      }
    }
    
    // 管理相关
    const toggleManageMode = () => {
      isManageMode.value = !isManageMode.value
      if (!isManageMode.value) {
        editingComments.value = {}
      }
    }
    
    // 添加图片
    const handleAddImage = (commentId) => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      input.onchange = (e) => {
        const file = e.target.files[0]
        if (file) {
          emit('add-image', { commentId, file })
          editingComments.value[commentId] = false
        }
      }
      input.click()
    }
    
    // 回复相关
    const toggleReplySection = (commentId) => {
      expandedReplies.value[commentId] = !expandedReplies.value[commentId]
      
      if (expandedReplies.value[commentId]) {
        // 初始化相关状态
        if (!replyForms.value[commentId]) {
          replyForms.value[commentId] = { content: '' }
        }
        if (submittingReply.value[commentId] === undefined) {
          submittingReply.value[commentId] = false
        }
        // 注意：新版本中回复数据已经包含在 comment.replies 中，不需要单独加载
      }
    }
    
    // 处理嵌套回复的回复按钮
    const handleToggleNestedReply = (replyId) => {
      activeReplyId.value = activeReplyId.value === replyId ? null : replyId
    }
    
    // 处理嵌套回复的提交
    const handleSubmitNestedReply = ({ parentId, content }) => {
      emit('submit-nested-reply', {
        parentId,
        content
      })
      activeReplyId.value = null
    }
    
    const handleSubmitReply = async (commentId, content) => {
      submittingReply.value[commentId] = true
      try {
        await emit('submit-reply', {
          commentId,
          content
        })
        replyForms.value[commentId].content = ''
        // 提交成功后，父组件会调用load-replies，这里不需要重复加载
      } catch (error) {
        console.error('提交回复失败:', error)
        alert('提交回复失败')
      } finally {
        submittingReply.value[commentId] = false
      }
    }
    
    const cancelReply = (commentId) => {
      replyForms.value[commentId].content = ''
    }
    
    // 处理删除回复
    const handleDeleteReply = (replyId) => {
      emit('delete-comment', replyId)
    }
    
    // 从外部更新回复列表的方法（暴露给父组件调用）
    const updateReplyList = (commentId, replies) => {
      // 使用Vue的响应式更新
      replyLists.value = {
        ...replyLists.value,
        [commentId]: replies || []
      }
    }
    
    return {
      submitting,
      showForm,
      editingComments,
      isManageMode,
      hasManageableComments,
      expandedReplies,
      replyForms,
      submittingReply,
      replyLists,
      replyCounts,
      showModal,
      modalImageUrl,
      commentFormRef,
      activeReplyId,
      isReversed,
      displayedComments,
      showUserProfilePopover,
      selectedUserId,
      toggleOrder,
      handleSubmit,
      handleDelete,
      showImageModal,
      closeImageModal,
      handleShowUserProfile,
      closeUserProfile,
      canAddImage,
      startEditing,
      cancelEditing,
      updateLocalContent,
      handleSaveComment,
      toggleManageMode,
      handleAddImage,
      toggleReplySection,
      handleSubmitReply,
      handleToggleNestedReply,
      handleSubmitNestedReply,
      cancelReply,
      handleDeleteReply,
      updateReplyList
    }
  }
}
</script>

<style scoped>
.card {
  background: #fff;
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.card-body {
  padding: 2rem;
}

.card-body h3 {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 0.8rem;
}

.checkin-section {
  text-align: center;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
}

.comment-list {
  margin-top: 2rem;
}

/* 回复区域样式 */
.reply-section-wrapper {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

.reply-form {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.reply-form textarea {
  font-size: 0.9rem;
  background: white;
  border: 1px solid #dee2e6;
}

.replies-list {
  margin-top: 1rem;
}

/* 模态框样式 */
.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
  animation: fadeIn 0.2s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  cursor: default;
  animation: zoomIn 0.2s ease-in;
}

@keyframes zoomIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-content img {
  max-width: 100%;
  max-height: 90vh;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  object-fit: contain;
}

.close-button {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: #333;
}

.close-button:hover {
  background: rgba(255, 255, 255, 1);
  transform: rotate(90deg);
}

/* 按钮透明度 */
.btn-outline-danger,
.btn-outline-success,
.btn-outline-primary,
.btn-outline-secondary {
  opacity: 0.7;
  transition: all 0.3s ease;
}

.btn-outline-danger:hover,
.btn-outline-success:hover,
.btn-outline-primary:hover,
.btn-outline-secondary:hover {
  opacity: 1;
  transform: scale(1.1);
}

@media (max-width: 768px) {
  .card-body {
    padding: 1rem;
  }
  
  .card-body h3 {
    font-size: 1.1rem;
    padding-bottom: 0.5rem;
  }
  
  .checkin-section {
    padding: 1rem;
  }
  
  .modal-content {
    max-width: 95vw;
  }
  
  .close-button {
    top: -35px;
    width: 32px;
    height: 32px;
    font-size: 18px;
  }
}
</style>