<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">📧 邮箱绑定</h5>
      <span v-if="emailVerified" class="badge bg-success">
        ✅ 已验证
      </span>
    </div>
    
    <div class="card-body">
      <!-- 当前邮箱显示 -->
      <div v-if="currentEmail && emailVerified" class="mb-3">
        <div class="alert alert-success">
          <strong>已绑定邮箱：</strong> {{ currentEmail }}
        </div>
      </div>
      
      <!-- 未绑定或未验证提示 -->
      <div v-else-if="!emailVerified" class="mb-3">
        <div class="alert alert-warning">
          <strong>⚠️ 邮箱{{ currentEmail ? '未验证' : '未绑定' }}</strong>
          <p class="mb-0 small">绑定邮箱可以用于找回密码和接收重要通知</p>
        </div>
      </div>
      
      <!-- 邮箱绑定表单 -->
      <div v-if="!emailVerified || !currentEmail">
        <form @submit.prevent="handleBindEmail">
          <!-- 邮箱输入 -->
          <div class="mb-3">
            <label class="form-label">📧 邮箱地址 <span class="text-danger">*</span></label>
            <div class="input-group">
              <input
                type="email"
                class="form-control"
                v-model="emailForm.email"
                :disabled="emailVerified && currentEmail"
                placeholder="请输入邮箱地址"
                required
              />
              <button
                v-if="!emailVerified || !currentEmail"
                type="button"
                class="btn btn-outline-primary"
                :disabled="!emailForm.email || sendingCode || countdown > 0 || verifyingCode"
                @click="handleSendCode"
              >
                <span v-if="sendingCode" class="spinner-border spinner-border-sm me-1"></span>
                <span v-else-if="countdown > 0">{{ countdown }}秒</span>
                <span v-else>发送验证码</span>
              </button>
            </div>
            <small v-if="codeSent && !emailVerified" class="text-success">
              验证码已发送，请查收邮箱
            </small>
          </div>
          
          <!-- 验证码输入 -->
          <div class="mb-3" v-if="codeSent">
            <label class="form-label">🔐 验证码 <span class="text-danger">*</span></label>
            <input
              type="text"
              class="form-control"
              v-model="emailForm.code"
              :disabled="emailVerified"
              placeholder="请输入6位验证码"
              maxlength="6"
              required
            />
          </div>
          
          <!-- 操作按钮 -->
          <div class="d-flex gap-2" v-if="codeSent && !emailVerified">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="binding || !emailForm.code || emailForm.code.length !== 6"
            >
              <span v-if="binding" class="spinner-border spinner-border-sm me-2"></span>
              {{ binding ? '绑定中...' : '✅ 绑定邮箱' }}
            </button>
            <button
              type="button"
              class="btn btn-outline-secondary"
              @click="handleCancel"
              :disabled="binding"
            >
              取消
            </button>
          </div>
        </form>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="errorMessage" class="alert alert-danger mt-3">
        {{ errorMessage }}
      </div>
      
      <!-- 成功提示 -->
      <div v-if="successMessage" class="alert alert-success mt-3">
        {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { sendVerificationCode, verifyCode } from '@/api/auth'
import { bindEmail } from '@/api/user'

export default {
  name: 'EmailBindingEditor',
  
  props: {
    currentEmail: {
      type: String,
      default: ''
    },
    emailVerified: {
      type: Boolean,
      default: false
    },
    userId: {
      type: Number,
      required: true
    }
  },
  
  emits: ['email-bound', 'update'],
  
  setup(props, { emit }) {
    const emailForm = ref({
      email: props.currentEmail || '',
      code: ''
    })
    
    const sendingCode = ref(false)
    const binding = ref(false)
    const codeSent = ref(false)
    const countdown = ref(0)
    const errorMessage = ref('')
    const successMessage = ref('')
    
    let countdownTimer = null
    
    // 发送验证码
    const handleSendCode = async () => {
      errorMessage.value = ''
      successMessage.value = ''
      
      if (!emailForm.value.email) {
        errorMessage.value = '请先输入邮箱地址'
        return
      }
      
      // 验证邮箱格式
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(emailForm.value.email)) {
        errorMessage.value = '请输入有效的邮箱地址'
        return
      }
      
      sendingCode.value = true
      
      try {
        await sendVerificationCode({
          email: emailForm.value.email,
          type: 'bind_email'
        })
        
        codeSent.value = true
        countdown.value = 60 // 60秒倒计时
        startCountdown()
        successMessage.value = '验证码已发送，请查收邮箱'
        
      } catch (error) {
        console.error('发送验证码失败:', error)
        if (error.response?.data) {
          const data = error.response.data
          if (data.error) {
            errorMessage.value = data.error
          } else if (data.email) {
            errorMessage.value = Array.isArray(data.email) ? data.email[0] : data.email
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
    
    // 绑定邮箱
    const handleBindEmail = async () => {
      errorMessage.value = ''
      successMessage.value = ''
      
      if (!emailForm.value.code || emailForm.value.code.length !== 6) {
        errorMessage.value = '请输入6位验证码'
        return
      }
      
      binding.value = true
      
      try {
        // 1. 先验证验证码
        const verifyResponse = await verifyCode({
          email: emailForm.value.email,
          code: emailForm.value.code,
          type: 'bind_email'
        })
        
        if (!verifyResponse.success || !verifyResponse.verification_token) {
          errorMessage.value = '验证码验证失败，请检查验证码是否正确'
          binding.value = false
          return
        }
        
        // 2. 绑定邮箱（使用专门的绑定邮箱API，会自动标记为已验证）
        await bindEmail({
          email: emailForm.value.email,
          verification_token: verifyResponse.verification_token
        })
        
        // 3. 触发更新事件
        emit('email-bound', {
          email: emailForm.value.email,
          verified: true
        })
        emit('update')
        
        successMessage.value = '邮箱绑定成功！'
        
        // 清除表单
        emailForm.value.code = ''
        codeSent.value = false
        if (countdownTimer) {
          clearInterval(countdownTimer)
          countdownTimer = null
          countdown.value = 0
        }
        
      } catch (error) {
        console.error('绑定邮箱失败:', error)
        if (error.response?.data) {
          const data = error.response.data
          if (data.error) {
            errorMessage.value = data.error
          } else if (data.code) {
            errorMessage.value = Array.isArray(data.code) ? data.code[0] : data.code
          } else if (data.email) {
            errorMessage.value = Array.isArray(data.email) ? data.email[0] : data.email
          } else {
            errorMessage.value = '绑定邮箱失败，请稍后重试'
          }
        } else {
          errorMessage.value = '网络错误，请检查网络连接'
        }
      } finally {
        binding.value = false
      }
    }
    
    // 取消绑定
    const handleCancel = () => {
      emailForm.value.code = ''
      codeSent.value = false
      errorMessage.value = ''
      successMessage.value = ''
      if (countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
        countdown.value = 0
      }
    }
    
    // 倒计时
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
    
    return {
      emailForm,
      sendingCode,
      binding,
      codeSent,
      countdown,
      errorMessage,
      successMessage,
      handleSendCode,
      handleBindEmail,
      handleCancel
    }
  }
}
</script>

<style scoped>
.card {
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.card-header {
  border-bottom: 2px solid #f0f0f0;
  padding: 1rem 1.5rem;
}

.form-label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.form-control {
  border-radius: 12px;
  border: 2px solid #e9ecef;
  padding: 0.75rem 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.input-group .form-control {
  flex: 1;
}

.input-group .btn {
  white-space: nowrap;
}

.d-flex.gap-2 {
  gap: 0.5rem;
}

.alert {
  border-radius: 12px;
  padding: 1rem;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
}
</style>

