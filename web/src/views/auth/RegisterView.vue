<template>
  <div class="auth-wrapper">
    <NavBar />
    <div class="register-container">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow">
            <div class="card-body p-5">
              <h2 class="text-center mb-2">用户注册</h2>
              <p class="register-slogan text-center mb-4">Become a Roamioer today.</p>
              
              <!-- 错误提示 -->
              <div v-if="errorMessage" class="alert alert-danger">
                {{ errorMessage }}
              </div>
              
              <!-- 成功提示 -->
              <div v-if="successMessage" class="alert alert-success">
                {{ successMessage }}
              </div>
              
              <form @submit.prevent="handleRegister">
                <!-- 用户名 -->
                <div class="mb-3">
                  <label for="username" class="form-label">用户名</label>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="formData.username"
                    required
                    :disabled="submitting"
                    placeholder="请输入用户名"
                  />
                  <div v-if="errors.username" class="text-danger small mt-1">
                    {{ errors.username }}
                  </div>
                </div>
                
                <!-- 邮箱 -->
                <div class="mb-3">
                  <label for="email" class="form-label">邮箱 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      type="email"
                      class="form-control"
                      id="email"
                      v-model="formData.email"
                      required
                      :disabled="submitting || codeVerified"
                      placeholder="请输入邮箱"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      :disabled="!formData.email || sendingCode || codeVerified || countdown > 0"
                      @click="handleSendCode"
                    >
                      <span v-if="sendingCode" class="spinner-border spinner-border-sm me-1"></span>
                      <span v-else-if="countdown > 0">{{ countdown }}s</span>
                      <span v-else>发送验证码</span>
                    </button>
                  </div>
                  <div v-if="errors.email" class="text-danger small mt-1">
                    {{ errors.email }}
                  </div>
                  <div v-if="codeSent && !codeVerified" class="text-success small mt-1">
                    验证码已发送，请查收邮箱
                  </div>
                </div>
                
                <!-- 验证码 -->
                <div class="mb-3" v-if="codeSent">
                  <label for="verification_code" class="form-label">验证码 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      type="text"
                      class="form-control"
                      id="verification_code"
                      v-model="formData.verification_code"
                      required
                      :disabled="submitting || codeVerified"
                      placeholder="请输入验证码"
                      maxlength="6"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-primary"
                      :disabled="!formData.verification_code || verifyingCode || codeVerified"
                      @click="handleVerifyCode"
                    >
                      <span v-if="verifyingCode" class="spinner-border spinner-border-sm me-1"></span>
                      <span v-else-if="codeVerified">✓ 已验证</span>
                      <span v-else>验证</span>
                    </button>
                  </div>
                  <div v-if="errors.verification_code" class="text-danger small mt-1">
                    {{ errors.verification_code }}
                  </div>
                  <div v-if="codeVerified" class="text-success small mt-1">
                    ✓ 邮箱验证成功
                  </div>
                </div>
                
                <!-- 密码 -->
                <div class="mb-3">
                  <label for="password" class="form-label">密码</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    v-model="formData.password"
                    required
                    :disabled="submitting"
                    placeholder="请输入密码"
                  />
                  <div v-if="errors.password" class="text-danger small mt-1">
                    {{ errors.password }}
                  </div>
                  <small class="text-muted">
                    密码至少8位，包含字母和数字
                  </small>
                </div>
                
                <!-- 确认密码 -->
                <div class="mb-4">
                  <label for="password2" class="form-label">确认密码</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password2"
                    v-model="formData.password2"
                    required
                    :disabled="submitting"
                    placeholder="请再次输入密码"
                  />
                  <div v-if="errors.password2" class="text-danger small mt-1">
                    {{ errors.password2 }}
                  </div>
                </div>
                
                <!-- 提交按钮 -->
                <button
                  type="submit"
                  class="btn btn-primary w-100 mb-3"
                  :disabled="submitting || !codeVerified"
                >
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  {{ submitting ? '注册中...' : codeVerified ? '完成注册' : '请先验证邮箱' }}
                </button>
                
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
                    <img src="/static/images/qq_login.png" alt="QQ登录" class="qq-login-icon" width="20" height="20">
                    <span v-if="qqLoginLoading">跳转中...</span>
                    <span v-else>使用QQ登录</span>
                  </button>
                </div>
                
                <!-- 登录链接 -->
                <div class="text-center">
                  <span class="text-muted">已有账号？</span>
                  <router-link to="/login" class="text-decoration-none">
                    立即登录
                  </router-link>
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
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { getQQLoginUrl, sendVerificationCode, verifyCode } from '@/api/auth'
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'RegisterView',
  components: { NavBar },
  
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const formData = ref({
      username: '',
      email: '',
      password: '',
      password2: '',
      verification_code: '',
      verification_token: ''
    })
    
    const errors = ref({})
    const errorMessage = ref('')
    const successMessage = ref('')
    const submitting = ref(false)
    const qqLoginLoading = ref(false)
    const sendingCode = ref(false)
    const verifyingCode = ref(false)
    const codeSent = ref(false)
    const codeVerified = ref(false)
    const countdown = ref(0)
    let countdownTimer = null
    
    // 表单验证
    const validateForm = () => {
      errors.value = {}
      
      if (!formData.value.username) {
        errors.value.username = '请输入用户名'
        return false
      }
      
      if (formData.value.username.length < 3) {
        errors.value.username = '用户名至少3个字符'
        return false
      }
      
      if (!formData.value.email) {
        errors.value.email = '请输入邮箱'
        return false
      }
      
      // 验证邮箱格式
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(formData.value.email)) {
        errors.value.email = '请输入有效的邮箱地址'
        return false
      }
      
      if (!codeVerified.value) {
        errors.value.verification_token = '请先完成邮箱验证'
        return false
      }
      
      if (!formData.value.password) {
        errors.value.password = '请输入密码'
        return false
      }
      
      if (formData.value.password.length < 8) {
        errors.value.password = '密码至少8位'
        return false
      }
      
      if (!formData.value.password2) {
        errors.value.password2 = '请再次输入密码'
        return false
      }
      
      if (formData.value.password !== formData.value.password2) {
        errors.value.password2 = '两次密码不一致'
        return false
      }
      
      return true
    }
    
    // 发送验证码
    const handleSendCode = async () => {
      errors.value.email = ''
      errorMessage.value = ''
      
      if (!formData.value.email) {
        errors.value.email = '请先输入邮箱'
        return
      }
      
      // 验证邮箱格式
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(formData.value.email)) {
        errors.value.email = '请输入有效的邮箱地址'
        return
      }
      
      sendingCode.value = true
      
      try {
        await sendVerificationCode({
          email: formData.value.email,
          type: 'register'
        })
        
        codeSent.value = true
        countdown.value = 60 // 60秒倒计时
        startCountdown()
        
      } catch (error) {
        console.error('发送验证码失败:', error)
        if (error.response?.data) {
          const data = error.response.data
          if (data.error) {
            errorMessage.value = data.error
          } else if (data.email) {
            errors.value.email = Array.isArray(data.email) ? data.email[0] : data.email
          } else {
            errorMessage.value = '发送验证码失败，请稍后重试'
          }
        } else {
          errorMessage.value = '网络错误，请检查网络连接'
        }
      } finally {
        sendingCode.value = false
      }
    }
    
    // 验证验证码
    const handleVerifyCode = async () => {
      errors.value.verification_code = ''
      errorMessage.value = ''
      
      if (!formData.value.verification_code) {
        errors.value.verification_code = '请输入验证码'
        return
      }
      
      if (formData.value.verification_code.length !== 6) {
        errors.value.verification_code = '验证码为6位数字'
        return
      }
      
      verifyingCode.value = true
      
      try {
        const response = await verifyCode({
          email: formData.value.email,
          code: formData.value.verification_code,
          type: 'register'
        })
        
        if (response.success && response.verification_token) {
          formData.value.verification_token = response.verification_token
          codeVerified.value = true
          successMessage.value = '邮箱验证成功！可以完成注册了'
        } else {
          errors.value.verification_code = '验证失败，请检查验证码'
        }
        
      } catch (error) {
        console.error('验证码验证失败:', error)
        if (error.response?.data) {
          const data = error.response.data
          if (data.error) {
            errors.value.verification_code = data.error
          } else if (data.code) {
            errors.value.verification_code = Array.isArray(data.code) ? data.code[0] : data.code
          } else {
            errors.value.verification_code = '验证码无效或已过期'
          }
        } else {
          errors.value.verification_code = '验证失败，请稍后重试'
        }
      } finally {
        verifyingCode.value = false
      }
    }
    
    // 倒计时函数
    const startCountdown = () => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
      
      countdownTimer = setInterval(() => {
        if (countdown.value > 0) {
          countdown.value--
        } else {
          clearInterval(countdownTimer)
          countdownTimer = null
        }
      }, 1000)
    }
    
    // 清理定时器
    onUnmounted(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
    })
    
    // 处理注册
    const handleRegister = async () => {
      errorMessage.value = ''
      successMessage.value = ''
      
      if (!validateForm()) {
        return
      }
      
      submitting.value = true
      
      try {
        await userStore.register({
          username: formData.value.username,
          email: formData.value.email,
          password: formData.value.password,
          password2: formData.value.password2,
          verification_token: formData.value.verification_token
        })
        
        successMessage.value = '注册成功！正在跳转...'
        
        // 2秒后跳转到首页
        setTimeout(() => {
          router.push('/')
        }, 2000)
        
      } catch (error) {
        console.error('注册失败:', error)
        
        // 处理错误信息
        if (error.response?.data) {
          const data = error.response.data
          
          // 如果是字段错误
          if (typeof data === 'object') {
            if (data.username) {
              errors.value.username = Array.isArray(data.username) ? data.username[0] : data.username
            }
            if (data.email) {
              errors.value.email = Array.isArray(data.email) ? data.email[0] : data.email
            }
            if (data.password) {
              errors.value.password = Array.isArray(data.password) ? data.password[0] : data.password
            }
            if (data.password2) {
              errors.value.password2 = Array.isArray(data.password2) ? data.password2[0] : data.password2
            }
            if (data.verification_code) {
              errors.value.verification_code = Array.isArray(data.verification_code) ? data.verification_code[0] : data.verification_code
            }
            
            // 处理非字段错误
            if (data.non_field_errors) {
              errorMessage.value = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors
            }
            
            // 处理验证token错误
            if (data.verification_token) {
              errors.value.verification_token = Array.isArray(data.verification_token) ? data.verification_token[0] : data.verification_token
              if (!errorMessage.value) {
                errorMessage.value = '注册需要邮箱验证，请先完成邮箱验证'
              }
            }
            
            // 如果有通用错误消息
            if (!errorMessage.value && (data.detail || data.message || data.error)) {
              errorMessage.value = data.detail || data.message || data.error
            }
            
            if (!errorMessage.value) {
              errorMessage.value = '注册失败，请稍后重试'
            }
          } else {
            errorMessage.value = '注册失败，请稍后重试'
          }
        } else {
          errorMessage.value = '网络错误，请检查网络连接'
        }
      } finally {
        submitting.value = false
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
          errorMessage.value = '获取QQ登录链接失败，请重试'
          qqLoginLoading.value = false
        }
      } catch (err) {
        errorMessage.value = err.response?.data?.error || 'QQ登录失败，请重试'
        qqLoginLoading.value = false
      }
    }
    
    return {
      formData,
      errors,
      errorMessage,
      successMessage,
      submitting,
      qqLoginLoading,
      sendingCode,
      verifyingCode,
      codeSent,
      codeVerified,
      countdown,
      handleRegister,
      handleQQLogin,
      handleSendCode,
      handleVerifyCode
    }
  }
}
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-container {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  padding-top: 20px;
}

.card {
  border: none;
  border-radius: 15px;
}

.card-body {
  background: white;
  border-radius: 15px;
}

h2 {
  color: #333;
  font-weight: 600;
}

.register-slogan {
  color: #6c63ff;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 8px rgba(108, 99, 255, 0.25);
}

.form-label {
  font-weight: 500;
  color: #555;
}

.form-control {
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #ddd;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-weight: 600;
  transition: transform 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alert {
  border-radius: 8px;
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

