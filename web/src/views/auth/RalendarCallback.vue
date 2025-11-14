<template>
  <div class="ralendar-callback-container">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card shadow">
            <div class="card-body text-center py-5">
              <!-- 加载状态 -->
              <div v-if="status === 'loading'">
                <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                  <span class="visually-hidden">处理中...</span>
                </div>
                <h5>正在连接 Ralendar...</h5>
                <p class="text-muted">请稍候</p>
              </div>

              <!-- 成功状态 -->
              <div v-else-if="status === 'success'">
                <i class="bi bi-check-circle-fill text-success mb-3" style="font-size: 4rem;"></i>
                <h5>连接成功！</h5>
                <p class="text-muted">已成功绑定 Ralendar 账号</p>
                <div v-if="accountInfo" class="account-preview mt-4 p-3 bg-light rounded">
                  <div class="d-flex align-items-center justify-content-center">
                    <img 
                      v-if="accountInfo.ralendar_avatar" 
                      :src="accountInfo.ralendar_avatar" 
                      :alt="accountInfo.ralendar_username"
                      class="rounded-circle me-3"
                      style="width: 48px; height: 48px; object-fit: cover;"
                    >
                    <div class="text-start">
                      <div class="fw-bold">{{ accountInfo.ralendar_username }}</div>
                      <div class="text-muted small">{{ accountInfo.ralendar_email }}</div>
                    </div>
                  </div>
                </div>
                <button class="btn btn-primary mt-4" @click="redirectToOrigin">
                  {{ countdown > 0 ? `${countdown} 秒后自动跳转` : '返回' }}
                </button>
              </div>

              <!-- 失败状态 -->
              <div v-else-if="status === 'error'">
                <i class="bi bi-x-circle-fill text-danger mb-3" style="font-size: 4rem;"></i>
                <h5>连接失败</h5>
                <p class="text-muted">{{ errorMessage }}</p>
                <div class="mt-4">
                  <button class="btn btn-primary me-2" @click="retry">
                    重试
                  </button>
                  <button class="btn btn-outline-secondary" @click="redirectToOrigin">
                    返回
                  </button>
                </div>
              </div>

              <!-- 用户取消 -->
              <div v-else-if="status === 'cancelled'">
                <i class="bi bi-info-circle-fill text-warning mb-3" style="font-size: 4rem;"></i>
                <h5>授权已取消</h5>
                <p class="text-muted">您取消了 Ralendar 授权</p>
                <button class="btn btn-primary mt-4" @click="redirectToOrigin">
                  返回
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { handleRalendarCallback } from '@/api/ralendarOAuth'

export default {
  name: 'RalendarCallback',
  setup() {
    const route = useRoute()
    const router = useRouter()

    const status = ref('loading')  // loading, success, error, cancelled
    const errorMessage = ref('')
    const accountInfo = ref(null)
    const countdown = ref(3)
    let countdownTimer = null

    // 处理 OAuth 回调
    const processCallback = async () => {
      const code = route.query.code
      const state = route.query.state
      const error = route.query.error

      // 用户取消授权
      if (error === 'access_denied') {
        status.value = 'cancelled'
        return
      }

      // 缺少必要参数
      if (!code || !state) {
        status.value = 'error'
        errorMessage.value = '缺少必要参数，请重试'
        return
      }

      try {
        // 调用后端处理回调
        const response = await handleRalendarCallback(code, state)
        
        if (response.success) {
          status.value = 'success'
          accountInfo.value = response.account
          
          // 启动倒计时
          startCountdown()
        } else {
          status.value = 'error'
          errorMessage.value = response.message || '连接失败，请重试'
        }
      } catch (err) {
        console.error('处理回调失败:', err)
        status.value = 'error'
        
        const errData = err.response?.data
        if (errData?.code === 'INVALID_STATE') {
          errorMessage.value = '授权已过期，请重新尝试'
        } else if (errData?.code === 'TOKEN_EXCHANGE_FAILED') {
          errorMessage.value = '授权失败，请检查网络连接后重试'
        } else {
          errorMessage.value = errData?.error || '连接失败，请重试'
        }
      }
    }

    // 启动倒计时
    const startCountdown = () => {
      countdownTimer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(countdownTimer)
          redirectToOrigin()
        }
      }, 1000)
    }

    // 重试
    const retry = () => {
      router.push('/user/center')  // 跳转到个人中心重新连接
    }

    // 返回来源页面
    const redirectToOrigin = () => {
      // 优先跳转到 sessionStorage 保存的来源页面
      const origin = sessionStorage.getItem('ralendar_auth_origin') || '/user/center'
      sessionStorage.removeItem('ralendar_auth_origin')
      router.push(origin)
    }

    onMounted(() => {
      processCallback()
    })

    onBeforeUnmount(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
    })

    return {
      status,
      errorMessage,
      accountInfo,
      countdown,
      retry,
      redirectToOrigin
    }
  }
}
</script>

<style scoped>
.ralendar-callback-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  padding: 2rem 0;
}

.card {
  border: none;
  border-radius: 15px;
}

.account-preview {
  border: 1px solid #dee2e6;
}
</style>

