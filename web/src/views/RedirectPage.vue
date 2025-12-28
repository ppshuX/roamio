<template>
  <div class="redirect-page">
    <div class="container">
      <div class="redirect-container">
        <!-- 微信浏览器提示 -->
        <div v-if="isWeChat" class="wechat-prompt">
          <div class="redirect-icon wechat-icon">
            <i class="bi bi-wechat" style="font-size: 64px; color: #09BB07;"></i>
          </div>
          
          <h2 class="redirect-title">检测到微信浏览器</h2>
          
          <p class="redirect-description">
            为了更好的体验，建议使用外部浏览器打开此链接
          </p>
          
          <div class="wechat-actions">
            <button 
              @click="handleOpenInBrowser" 
              class="btn btn-success btn-lg"
            >
              <i class="bi bi-browser-chrome me-2"></i>
              在浏览器中打开
            </button>
            
            <button 
              @click="handleCopyLink" 
              class="btn btn-outline-primary btn-lg"
            >
              <i class="bi bi-clipboard me-2"></i>
              复制链接
            </button>
            
            <button 
              @click="handleDirectRedirect" 
              class="btn btn-outline-secondary"
            >
              <i class="bi bi-arrow-right me-2"></i>
              继续在微信中打开
            </button>
          </div>
          
          <div class="wechat-tips mt-4">
            <div class="tip-item">
              <i class="bi bi-info-circle me-2"></i>
              <small>点击右上角"..." → 选择"在浏览器中打开"</small>
            </div>
          </div>
        </div>
        
        <!-- 普通浏览器界面 -->
        <div v-else>
          <div class="redirect-icon">
            <i class="bi bi-box-arrow-up-right" style="font-size: 64px;"></i>
          </div>
          
          <h2 class="redirect-title">跳转到年度总结网站</h2>
          
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'RedirectPage',
  setup() {
    const router = useRouter()
    const isRedirecting = ref(false)
    const isWeChat = ref(false)
    const targetUrl = 'https://app7581.acapp.acwing.com.cn/'
    const copySuccess = ref(false)
    
    // 检测是否在微信浏览器中
    const detectWeChat = () => {
      const ua = navigator.userAgent.toLowerCase()
      return ua.indexOf('micromessenger') !== -1
    }
    
    onMounted(() => {
      isWeChat.value = detectWeChat()
    })
    
    // 普通浏览器直接跳转
    const handleRedirect = () => {
      isRedirecting.value = true
      setTimeout(() => {
        window.location.href = targetUrl
      }, 300)
    }
    
    // 微信中直接跳转（如果用户选择继续）
    const handleDirectRedirect = () => {
      window.location.href = targetUrl
    }
    
    // 在浏览器中打开（微信中调用）
    const handleOpenInBrowser = () => {
      // 尝试使用微信的 WeixinJSBridge API（需要等待微信JS-SDK初始化）
      if (typeof window.WeixinJSBridge !== 'undefined') {
        // 直接调用 openUrlByExtBrowser（已过时，但仍然可用）
        try {
          window.WeixinJSBridge.invoke('openUrlByExtBrowser', {
            url: targetUrl
          }, () => {
            // 如果调用失败，降级到手动提示
            alert('请点击右上角"..."按钮，选择"在浏览器中打开"')
          })
        } catch (e) {
          // 如果API调用失败，提示用户手动操作
          alert('请点击右上角"..."按钮，选择"在浏览器中打开"')
        }
      } else {
        // WeixinJSBridge 未加载，提示用户手动操作
        alert('请点击右上角"..."按钮，选择"在浏览器中打开"')
      }
    }
    
    // 复制链接
    const handleCopyLink = async () => {
      try {
        // 使用现代的 Clipboard API
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(targetUrl)
          copySuccess.value = true
          alert('链接已复制到剪贴板！')
          setTimeout(() => {
            copySuccess.value = false
          }, 2000)
        } else {
          // 降级方案：使用传统方法
          const textArea = document.createElement('textarea')
          textArea.value = targetUrl
          textArea.style.position = 'fixed'
          textArea.style.opacity = '0'
          document.body.appendChild(textArea)
          textArea.select()
          try {
            document.execCommand('copy')
            copySuccess.value = true
            alert('链接已复制到剪贴板！')
            setTimeout(() => {
              copySuccess.value = false
            }, 2000)
          } catch (err) {
            alert('复制失败，请手动复制：' + targetUrl)
          }
          document.body.removeChild(textArea)
        }
      } catch (err) {
        console.error('复制失败:', err)
        alert('复制失败，请手动复制：' + targetUrl)
      }
    }
    
    const handleCancel = () => {
      router.push('/')
    }
    
    return {
      isRedirecting,
      isWeChat,
      targetUrl,
      copySuccess,
      handleRedirect,
      handleDirectRedirect,
      handleOpenInBrowser,
      handleCopyLink,
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

.redirect-page .container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
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

/* 微信浏览器样式 */
.wechat-prompt {
  text-align: center;
}

.wechat-icon {
  color: #09BB07;
}

.wechat-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.wechat-actions .btn {
  width: 100%;
}

.btn-success {
  background-color: #09BB07;
  border-color: #09BB07;
}

.btn-success:hover {
  background-color: #08A806;
  border-color: #08A806;
}

.wechat-tips {
  background: #f0f7ff;
  border-radius: 10px;
  padding: 1rem;
  border-left: 4px solid #09BB07;
}

.tip-item {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
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

