<template>
  <div class="auth-wrapper">
    <NavBar />
    <div class="login-container">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow-lg">
            <div class="card-body p-5">
              <h2 class="text-center mb-2">用户登录</h2>
              <p class="login-slogan text-center mb-4">Hello Roamioer!</p>
              
              <form @submit.prevent="handleLogin">
                <!-- 用户名 -->
                <div class="mb-3">
                  <label for="username" class="form-label">用户名</label>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="form.username"
                    required
                    placeholder="请输入用户名"
                  />
                </div>
                
                <!-- 密码 -->
                <div class="mb-3">
                  <label for="password" class="form-label">密码</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    v-model="form.password"
                    required
                    placeholder="请输入密码"
                  />
                </div>
                
                <!-- 错误提示 -->
                <div v-if="error" class="alert alert-danger" role="alert">
                  {{ error }}
                </div>
                
                <!-- 登录按钮 -->
                <button
                  type="submit"
                  class="btn btn-primary w-100 mb-2"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ loading ? '登录中...' : '登录' }}
                </button>
                
                <!-- 忘记密码 -->
                <div class="text-end mb-3">
                  <router-link to="/forgot-password/" class="text-decoration-none small text-primary">
                    忘记密码？
                  </router-link>
                </div>
                
                <!-- QQ登录 -->
                <div class="text-center mb-3">
                  <div class="divider">
                    <span class="divider-text">或</span>
                  </div>
                  <button
                    type="button"
                    class="btn btn-outline-secondary w-100 qq-login-btn"
                    :disabled="qqLoginLoading"
                    @click="handleQQLogin"
                  >
                    <img src="@/assets/qq_logo.png" alt="QQ登录" class="qq-login-icon" width="20" height="20">
                    <span v-if="qqLoginLoading">跳转中...</span>
                    <span v-else>使用QQ登录</span>
                  </button>
                </div>
                
                <!-- 注册链接 -->
                <div class="text-center">
                  <span class="text-muted">还没有账号？</span>
                  <router-link to="/register" class="text-decoration-none">立即注册</router-link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { getQQLoginUrl } from '@/api/auth'
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'LoginView',
  components: { NavBar },
  
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const form = ref({
      username: '',
      password: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    const qqLoginLoading = ref(false)
    
    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      
      try {
        await userStore.login(form.value)
        
        // 登录成功，跳转到首页
        router.push('/')
      } catch (err) {
        // 优先显示API返回的中文错误信息
        if (err.response?.data) {
          const data = err.response.data
          
          // 处理字段错误
          if (data.username && Array.isArray(data.username)) {
            error.value = data.username[0]
          } else if (data.password && Array.isArray(data.password)) {
            error.value = data.password[0]
          } else if (data.non_field_errors && Array.isArray(data.non_field_errors)) {
            error.value = data.non_field_errors[0]
          } else if (typeof data === 'string') {
            error.value = data
          } else if (data.detail) {
            error.value = data.detail
          } else {
            error.value = '登录失败，请检查用户名和密码'
          }
        } else {
          error.value = err.message || '登录失败，请检查用户名和密码'
        }
      } finally {
        loading.value = false
      }
    }
    
    const handleQQLogin = async () => {
      qqLoginLoading.value = true
      try {
        const response = await getQQLoginUrl()
        if (response.authorize_url && response.state) {
          // 保存state到sessionStorage用于验证
          sessionStorage.setItem('qq_oauth_state', response.state)
          // 跳转到QQ授权页面
          window.location.href = response.authorize_url
        } else {
          error.value = '获取QQ登录链接失败，请重试'
          qqLoginLoading.value = false
        }
      } catch (err) {
        error.value = err.response?.data?.error || 'QQ登录失败，请重试'
        qqLoginLoading.value = false
      }
    }
    
    return {
      form,
      loading,
      error,
      qqLoginLoading,
      handleLogin,
      handleQQLogin
    }
  }
}
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  padding-top: 20px;
}

.card {
  border: none;
  border-radius: 15px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-slogan {
  color: #6c63ff;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 8px rgba(108, 99, 255, 0.25);
}

.divider {
  position: relative;
  text-align: center;
  margin: 20px 0;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 45%;
  height: 1px;
  background: #dee2e6;
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.divider-text {
  background: white;
  padding: 0 10px;
  color: #6c757d;
  font-size: 14px;
}

.qq-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border: 1px solid #dee2e6;
  transition: all 0.3s ease;
}

.qq-login-btn:hover {
  background-color: #f8f9fa;
  border-color: #adb5bd;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.qq-login-icon {
  margin-right: 5px;
}
</style>

