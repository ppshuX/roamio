<template>
  <div class="forgot-password-container">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow">
            <div class="card-body p-5">
              <h2 class="text-center mb-4">🔑 找回密码</h2>
              
              <!-- 错误提示 -->
              <div v-if="errorMessage" class="alert alert-danger">
                {{ errorMessage }}
              </div>
              
              <!-- 成功提示 -->
              <div v-if="successMessage" class="alert alert-success">
                {{ successMessage }}
              </div>
              
              <!-- 步骤1: 输入邮箱和发送验证码 -->
              <template v-if="step === 1">
                <p class="text-muted mb-4">请输入您的注册邮箱，我们将发送验证码到您的邮箱</p>
                
                <form @submit.prevent="handleSendCode">
                  <!-- 邮箱 -->
                  <div class="mb-3">
                    <label for="email" class="form-label">邮箱地址 <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <input
                        type="email"
                        class="form-control"
                        id="email"
                        v-model="formData.email"
                        required
                        :disabled="submitting || sendingCode"
                        placeholder="请输入注册邮箱"
                      />
                      <button
                        type="submit"
                        class="btn btn-primary"
                        :disabled="!formData.email || sendingCode || countdown > 0"
                      >
                        <span v-if="sendingCode" class="spinner-border spinner-border-sm me-1"></span>
                        <span v-else-if="countdown > 0">{{ countdown }}s</span>
                        <span v-else>发送验证码</span>
                      </button>
                    </div>
                    <div v-if="errors.email" class="text-danger small mt-1">
                      {{ errors.email }}
                    </div>
                    <div v-if="codeSent" class="text-success small mt-1">
                      ✅ 验证码已发送到您的邮箱，请查收
                    </div>
                  </div>
                  
                  <button
                    v-if="codeSent"
                    type="button"
                    class="btn btn-outline-primary w-100"
                    @click="step = 2"
                  >
                    下一步：验证验证码
                  </button>
                </form>
              </template>
              
              <!-- 步骤2: 验证验证码 -->
              <template v-if="step === 2">
                <p class="text-muted mb-4">请输入发送到 <strong>{{ formData.email }}</strong> 的验证码</p>
                
                <form @submit.prevent="handleVerifyCode">
                  <!-- 验证码 -->
                  <div class="mb-3">
                    <label for="verification_code" class="form-label">验证码 <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <input
                        type="text"
                        class="form-control"
                        id="verification_code"
                        v-model="formData.verification_code"
                        required
                        :disabled="submitting || verifyingCode || codeVerified"
                        placeholder="请输入6位验证码"
                        maxlength="6"
                      />
                      <button
                        type="submit"
                        class="btn btn-primary"
                        :disabled="!formData.verification_code || verifyingCode || codeVerified"
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
                      ✅ 验证成功！
                    </div>
                  </div>
                  
                  <div class="d-flex gap-2">
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="step = 1"
                    >
                      返回上一步
                    </button>
                    <button
                      v-if="codeVerified"
                      type="button"
                      class="btn btn-primary flex-grow-1"
                      @click="step = 3"
                    >
                      下一步：设置新密码
                    </button>
                  </div>
                </form>
              </template>
              
              <!-- 步骤3: 设置新密码 -->
              <template v-if="step === 3">
                <p class="text-muted mb-4">请设置您的新密码</p>
                
                <form @submit.prevent="handleResetPassword">
                  <!-- 新密码 -->
                  <div class="mb-3">
                    <label for="new_password" class="form-label">新密码 <span class="text-danger">*</span></label>
                    <input
                      type="password"
                      class="form-control"
                      id="new_password"
                      v-model="formData.new_password"
                      required
                      :disabled="submitting"
                      placeholder="请输入新密码（至少8位）"
                      minlength="8"
                    />
                    <div v-if="errors.new_password" class="text-danger small mt-1">
                      {{ errors.new_password }}
                    </div>
                    <small class="text-muted">密码至少8位，建议包含字母和数字</small>
                  </div>
                  
                  <!-- 确认新密码 -->
                  <div class="mb-4">
                    <label for="new_password2" class="form-label">确认新密码 <span class="text-danger">*</span></label>
                    <input
                      type="password"
                      class="form-control"
                      id="new_password2"
                      v-model="formData.new_password2"
                      required
                      :disabled="submitting"
                      placeholder="请再次输入新密码"
                      minlength="8"
                    />
                    <div v-if="errors.new_password2" class="text-danger small mt-1">
                      {{ errors.new_password2 }}
                    </div>
                  </div>
                  
                  <!-- 提交按钮 -->
                  <button
                    type="submit"
                    class="btn btn-primary w-100 mb-3"
                    :disabled="submitting"
                  >
                    <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                    {{ submitting ? '重置中...' : '重置密码' }}
                  </button>
                  
                  <button
                    type="button"
                    class="btn btn-outline-secondary w-100"
                    @click="step = 2"
                    :disabled="submitting"
                  >
                    返回上一步
                  </button>
                </form>
              </template>
              
              <!-- 步骤4: 重置成功 -->
              <template v-if="step === 4">
                <div class="text-center">
                  <div class="mb-4">
                    <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
                  </div>
                  <h3 class="mb-3">密码重置成功！</h3>
                  <p class="text-muted mb-4">您可以使用新密码登录了</p>
                  <button
                    type="button"
                    class="btn btn-primary w-100"
                    @click="goToLogin"
                  >
                    前往登录
                  </button>
                </div>
              </template>
              
              <!-- 返回登录链接 -->
              <div class="text-center mt-4">
                <span class="text-muted">想起密码了？</span>
                <router-link to="/login/" class="text-decoration-none ms-1">
                  返回登录
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { sendVerificationCode, verifyCode, resetPassword } from '@/api/auth'

const router = useRouter()

const step = ref(1) // 1: 输入邮箱, 2: 验证码, 3: 设置密码, 4: 成功
const formData = ref({
  email: '',
  verification_code: '',
  verification_token: '',
  new_password: '',
  new_password2: ''
})

const errors = ref({})
const errorMessage = ref('')
const successMessage = ref('')
const submitting = ref(false)
const sendingCode = ref(false)
const verifyingCode = ref(false)
const codeSent = ref(false)
const codeVerified = ref(false)
const countdown = ref(0)
let countdownTimer = null

// 发送验证码
const handleSendCode = async () => {
  errors.value = {}
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
      type: 'reset_password'
    })

    codeSent.value = true
    countdown.value = 60 // 60秒倒计时
    startCountdown()
    successMessage.value = '验证码已发送到您的邮箱'

    // 清除成功消息（3秒后）
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
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
  errors.value = {}
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
      type: 'reset_password'
    })

    if (response.success && response.verification_token) {
      formData.value.verification_token = response.verification_token
      codeVerified.value = true
      successMessage.value = '验证成功！'

      // 自动进入下一步
      setTimeout(() => {
        step.value = 3
      }, 1000)
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

// 重置密码
const handleResetPassword = async () => {
  errors.value = {}
  errorMessage.value = ''

  if (!formData.value.new_password) {
    errors.value.new_password = '请输入新密码'
    return
  }

  if (formData.value.new_password.length < 8) {
    errors.value.new_password = '密码长度至少为8位'
    return
  }

  if (formData.value.new_password !== formData.value.new_password2) {
    errors.value.new_password2 = '两次输入的密码不一致'
    return
  }

  submitting.value = true

  try {
    await resetPassword({
      email: formData.value.email,
      verification_token: formData.value.verification_token,
      new_password: formData.value.new_password,
      new_password2: formData.value.new_password2
    })

    // 重置成功
    step.value = 4
  } catch (error) {
    console.error('重置密码失败:', error)
    if (error.response?.data) {
      const data = error.response.data

      if (data.new_password) {
        errors.value.new_password = Array.isArray(data.new_password) ? data.new_password[0] : data.new_password
      }
      if (data.new_password2) {
        errors.value.new_password2 = Array.isArray(data.new_password2) ? data.new_password2[0] : data.new_password2
      }
      if (data.verification_token) {
        errorMessage.value = '验证token无效，请重新验证邮箱'
      }
      if (data.error) {
        errorMessage.value = data.error
      }

      if (!errorMessage.value && !errors.value.new_password && !errors.value.new_password2) {
        errorMessage.value = '重置密码失败，请稍后重试'
      }
    } else {
      errorMessage.value = '网络错误，请检查网络连接'
    }
  } finally {
    submitting.value = false
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

// 跳转到登录页
const goToLogin = () => {
  router.push('/login/')
}

// 清理定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.forgot-password-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.card {
  border: none;
  border-radius: 16px;
}

.card-body {
  background: white;
}

.alert {
  border-radius: 8px;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  transform: none;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.text-danger {
  color: #dc3545 !important;
}

.text-success {
  color: #28a745 !important;
}
</style>

