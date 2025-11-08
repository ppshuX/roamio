<template>
  <div class="comment-form mb-4">
    <h5 class="mb-3">记录一下</h5>
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <textarea
          v-model="formData.content"
          class="form-control"
          rows="4"
          placeholder="分享你的旅行故事..."
          required
        ></textarea>
      </div>
      
      <div class="row mb-3">
        <div class="col-md-6 mb-2">
          <label class="form-label">上传图片</label>
          <input
            type="file"
            class="form-control"
            accept="image/*"
            @change="handleImageChange"
          />
        </div>
        <div class="col-md-6 mb-2">
          <label class="form-label">上传视频</label>
          <input
            type="file"
            class="form-control"
            accept="video/*"
            @change="handleVideoChange"
          />
        </div>
      </div>
      
      <!-- 上传进度条 -->
      <div v-if="uploadProgress > 0 && uploadProgress < 100" class="mb-3">
        <div class="progress">
          <div
            class="progress-bar progress-bar-striped progress-bar-animated"
            role="progressbar"
            :style="{ width: uploadProgress + '%' }"
            :aria-valuenow="uploadProgress"
            aria-valuemin="0"
            aria-valuemax="100"
          >
            {{ uploadProgress }}%
          </div>
        </div>
        <small class="text-muted">{{ uploadMessage }}</small>
      </div>
      
      <button
        type="submit"
        class="btn btn-primary"
        :disabled="submitting"
      >
        <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
        {{ submitting ? '记录中...' : '记录一下' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'CommentForm',
  
  props: {
    submitting: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['submit', 'upload-progress'],
  
  setup(props, { emit }) {
    const formData = ref({
      content: '',
      image: null,
      video: null
    })
    
    const uploadProgress = ref(0)
    const uploadMessage = ref('')
    
    const handleImageChange = (event) => {
      formData.value.image = event.target.files[0]
    }
    
    const handleVideoChange = (event) => {
      formData.value.video = event.target.files[0]
    }
    
    const handleSubmit = () => {
      // 先保存表单数据引用（因为后面会重置）
      const submitData = {
        content: formData.value.content,
        image: formData.value.image,
        video: formData.value.video
      }
      
      // 重置表单（让用户可以继续输入）
      formData.value = {
        content: '',
        image: null,
        video: null
      }
      
      // 提交数据
      emit('submit', submitData, (progressEvent) => {
        // 进度回调 - progressEvent 格式: { loaded, total, percent }
        const progress = progressEvent.percent || 0
        uploadProgress.value = progress
        
        if (progress < 30) {
          uploadMessage.value = '准备上传...'
        } else if (progress < 70) {
          uploadMessage.value = '上传中...'
        } else if (progress < 100) {
          uploadMessage.value = '即将完成...'
        } else {
          // 上传完成，但后端还在处理
          uploadMessage.value = '处理中，请稍候...'
        }
      })
    }
    
    // 暴露重置进度条的方法（供父组件调用）
    const resetProgress = () => {
      uploadProgress.value = 0
      uploadMessage.value = ''
    }
    
    return {
      formData,
      uploadProgress,
      uploadMessage,
      handleImageChange,
      handleVideoChange,
      handleSubmit,
      resetProgress
    }
  }
}
</script>

<style scoped>
.comment-form {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
}

@media (max-width: 768px) {
  .comment-form {
    padding: 1rem;
  }
  
  .comment-form textarea {
    font-size: 14px;
    min-height: 80px;
  }
  
  .comment-form input[type="file"] {
    font-size: 14px;
  }
}
</style>
