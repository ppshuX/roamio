<template>
  <div class="qq-callback-container">
    <div class="loading-spinner">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">处理中...</span>
      </div>
      <p class="mt-3">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import { qqCallback } from '@/api/auth'

export default {
  name: 'QQCallbackView',
  
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userStore = useUserStore()
    
    const message = ref('正在处理QQ登录...')
    
    onMounted(async () => {
      try {
        // 获取URL参数
        const code = route.query.code
        const state = route.query.state
        
        if (!code || !state) {
          message.value = '缺少必要的参数，请重新登录'
          setTimeout(() => {
            router.push('/login/')
          }, 2000)
          return
        }
        
        // 调用后端API处理QQ登录
        message.value = '正在验证QQ登录信息...'
        const response = await qqCallback({ code, state })
        
        if (response.success && response.access) {
          // 登录成功
          userStore.token = response.access
          userStore.refreshToken = response.refresh
          userStore.userInfo = response.user
          
          localStorage.setItem('access_token', response.access)
          localStorage.setItem('refresh_token', response.refresh)
          localStorage.setItem('user_info', JSON.stringify(response.user))
          
          // 如果邮箱为空，提示用户后续绑定
          if (response.email_optional && !response.user?.email) {
            message.value = '登录成功！建议在个人中心绑定邮箱以便接收重要通知'
          } else {
            message.value = '登录成功！正在跳转...'
          }
          
          setTimeout(() => {
            router.push('/')
          }, response.email_optional ? 2500 : 1000)
        } else {
          message.value = response.error || 'QQ登录失败，请重试'
          setTimeout(() => {
            router.push('/login/')
          }, 2000)
        }
        
      } catch (error) {
        console.error('QQ登录处理失败:', error)
        message.value = error.response?.data?.error || error.message || 'QQ登录失败，请重试'
        
        setTimeout(() => {
          router.push('/login/')
        }, 2000)
      }
    })
    
    return {
      message
    }
  }
}
</script>

<style scoped>
.qq-callback-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading-spinner {
  text-align: center;
  color: white;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

.loading-spinner p {
  font-size: 1.1rem;
  margin-top: 1rem;
}
</style>

