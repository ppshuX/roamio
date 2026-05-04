<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">📧 邮箱绑定</h5>
      <span v-if="emailVerified" class="badge bg-success">
        ✅ 已验证
      </span>
    </div>
    
    <div class="card-body">
      <!-- 邮箱显示组件 -->
      <EmailDisplay
        v-if="!isChangingEmail"
        :email="currentEmail"
        :verified="emailVerified"
        @change-request="startChangeEmail"
      />
      
      <!-- 邮箱更改表单 -->
      <EmailChangeForm
        v-if="isChangingEmail"
        :current-email="currentEmail"
        :sending="sendingCode"
        :processing="changing"
        :code-sent="codeSent"
        :countdown="countdown"
        @send-code="handleSendChangeCode"
        @change="handleChangeEmail"
        @cancel="cancelChangeEmail"
        @error="handleError"
      />
      
      <!-- 邮箱绑定表单 -->
      <EmailBindForm
        v-if="(!emailVerified || !currentEmail) && !isChangingEmail"
        :current-email="currentEmail"
        :sending="sendingCode"
        :processing="binding"
        :code-sent="codeSent"
        :countdown="countdown"
        @send-code="handleSendCode"
        @bind="handleBindEmail"
        @cancel="handleCancel"
      />
      
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

<script setup>
import { ref } from 'vue'
import { sendVerificationCode, verifyCode } from '@/api/auth'
import { bindEmail, changeEmail } from '@/api/user'
import EmailDisplay from './components/EmailDisplay.vue'
import EmailBindForm from './components/EmailBindForm.vue'
import EmailChangeForm from './components/EmailChangeForm.vue'

const props = defineProps({
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
})

const emit = defineEmits(['email-bound', 'update'])

const sendingCode = ref(false)
const binding = ref(false)
const changing = ref(false)
const codeSent = ref(false)
const countdown = ref(0)
const errorMessage = ref('')
const successMessage = ref('')
const isChangingEmail = ref(false)

let countdownTimer = null

// 验证邮箱格式
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
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

// 清除倒计时
const clearCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
    countdown.value = 0
  }
}

// 重置状态
const resetState = () => {
  codeSent.value = false
  errorMessage.value = ''
  successMessage.value = ''
  clearCountdown()
}

// 发送绑定邮箱验证码
const handleSendCode = async (email) => {
  errorMessage.value = ''
  successMessage.value = ''
  
  if (!validateEmail(email)) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }
  
  sendingCode.value = true
  
  try {
    await sendVerificationCode({
      email: email,
      type: 'bind_email'
    })
    
    codeSent.value = true
    countdown.value = 60
    startCountdown()
    successMessage.value = '验证码已发送，请查收邮箱'
  } catch (error) {
    console.error('发送验证码失败:', error)
    errorMessage.value = error.response?.data?.error || '发送验证码失败，请稍后重试'
  } finally {
    sendingCode.value = false
  }
}

// 绑定邮箱
const handleBindEmail = async ({ email, code }) => {
  errorMessage.value = ''
  successMessage.value = ''
  
  binding.value = true
  
  try {
    // 1. 先验证验证码
    const verifyResponse = await verifyCode({
      email: email,
      code: code,
      type: 'bind_email'
    })
    
    if (!verifyResponse.success || !verifyResponse.verification_token) {
      errorMessage.value = '验证码验证失败，请检查验证码是否正确'
      binding.value = false
      return
    }
    
    // 2. 绑定邮箱
    await bindEmail({
      email: email,
      verification_token: verifyResponse.verification_token
    })
    
    // 3. 触发更新事件
    emit('email-bound', {
      email: email,
      verified: true
    })
    emit('update')
    
    successMessage.value = '邮箱绑定成功！'
    resetState()
  } catch (error) {
    console.error('绑定邮箱失败:', error)
    errorMessage.value = error.response?.data?.error || '绑定邮箱失败，请稍后重试'
  } finally {
    binding.value = false
  }
}

// 取消绑定
const handleCancel = () => {
  resetState()
}

// 开始更改邮箱
const startChangeEmail = () => {
  isChangingEmail.value = true
  resetState()
}

// 发送更改邮箱验证码
const handleSendChangeCode = async (newEmail) => {
  errorMessage.value = ''
  successMessage.value = ''
  
  if (!validateEmail(newEmail)) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }
  
  if (newEmail.toLowerCase() === props.currentEmail.toLowerCase()) {
    errorMessage.value = '新邮箱不能与当前邮箱相同'
    return
  }
  
  sendingCode.value = true
  
  try {
    await sendVerificationCode({
      email: newEmail,
      type: 'change_email'
    })
    
    codeSent.value = true
    countdown.value = 60
    startCountdown()
    successMessage.value = '验证码已发送到新邮箱，请查收'
  } catch (error) {
    console.error('发送验证码失败:', error)
    errorMessage.value = error.response?.data?.error || '发送验证码失败，请稍后重试'
  } finally {
    sendingCode.value = false
  }
}

// 更改邮箱
const handleChangeEmail = async ({ newEmail, code }) => {
  errorMessage.value = ''
  successMessage.value = ''
  
  changing.value = true
  
  try {
    // 1. 先验证验证码
    const verifyResponse = await verifyCode({
      email: newEmail,
      code: code,
      type: 'change_email'
    })
    
    if (!verifyResponse.success || !verifyResponse.verification_token) {
      errorMessage.value = '验证码验证失败，请检查验证码是否正确'
      changing.value = false
      return
    }
    
    // 2. 更改邮箱
    await changeEmail({
      new_email: newEmail,
      verification_token: verifyResponse.verification_token
    })
    
    // 3. 触发更新事件
    emit('email-bound', {
      email: newEmail,
      verified: true
    })
    emit('update')
    
    successMessage.value = '邮箱更改成功！'
    isChangingEmail.value = false
    resetState()
  } catch (error) {
    console.error('更改邮箱失败:', error)
    errorMessage.value = error.response?.data?.error || '更改邮箱失败，请稍后重试'
  } finally {
    changing.value = false
  }
}

// 取消更改邮箱
const cancelChangeEmail = () => {
  isChangingEmail.value = false
  resetState()
}

// 处理错误
const handleError = (message) => {
  errorMessage.value = message
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
