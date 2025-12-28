<template>
  <div class="redirect-page">
    <div class="container">
      <div class="redirect-container">
        <div class="redirect-icon">
          <i class="bi bi-box-arrow-up-right" style="font-size: 64px;"></i>
        </div>
        
        <h2 class="redirect-title">跳转到 Ralendar</h2>
        
        <p class="redirect-description">
          即将离开 Roamio，跳转到外部链接
        </p>
        
        <div class="redirect-info">
          <div class="info-item">
            <i class="bi bi-link-45deg me-2"></i>
            <span>{{ targetUrl }}</span>
          </div>
        </div>
        
        <div class="redirect-actions">
          <button 
            @click="handleRedirect" 
            class="btn btn-primary btn-lg"
            :disabled="isRedirecting"
          >
            <span v-if="!isRedirecting">
              <i class="bi bi-box-arrow-up-right me-2"></i>
              点击访问
            </span>
            <span v-else>
              <span class="spinner-border spinner-border-sm me-2"></span>
              正在跳转...
            </span>
          </button>
          
          <button 
            @click="handleCancel" 
            class="btn btn-outline-secondary btn-lg"
            :disabled="isRedirecting"
          >
            <i class="bi bi-x-circle me-2"></i>
            取消
          </button>
        </div>
        
        <div class="redirect-warning mt-3">
          <i class="bi bi-shield-exclamation me-2"></i>
          <small class="text-muted">请注意：您将离开 Roamio 网站</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'RedirectPage',
  setup() {
    const router = useRouter()
    const isRedirecting = ref(false)
    const targetUrl = 'https://app7581.acapp.acwing.com.cn/'
    
    const handleRedirect = () => {
      isRedirecting.value = true
      // 延迟一下，让用户看到"正在跳转"的状态
      setTimeout(() => {
        window.location.href = targetUrl
      }, 300)
    }
    
    const handleCancel = () => {
      router.push('/')
    }
    
    return {
      isRedirecting,
      targetUrl,
      handleRedirect,
      handleCancel
    }
  }
}
</script>

<style scoped>
.redirect-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.redirect-container {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.redirect-icon {
  margin-bottom: 1.5rem;
  color: #667eea;
}

.redirect-title {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 1rem;
}

.redirect-description {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 2rem;
}

.redirect-info {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #495057;
  word-break: break-all;
}

.redirect-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.redirect-actions .btn {
  min-width: 150px;
}

.redirect-warning {
  color: #6c757d;
  font-size: 0.9rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-outline-secondary:hover:not(:disabled) {
  transform: translateY(-2px);
}

@media (max-width: 576px) {
  .redirect-container {
    padding: 2rem 1.5rem;
  }
  
  .redirect-title {
    font-size: 1.5rem;
  }
  
  .redirect-actions {
    flex-direction: column;
  }
  
  .redirect-actions .btn {
    width: 100%;
  }
}
</style>

