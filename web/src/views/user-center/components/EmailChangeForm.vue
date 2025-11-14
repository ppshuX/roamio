<template>
  <div>
    <div class="alert alert-info">
      <strong>当前邮箱：</strong> {{ currentEmail }}
    </div>
    
    <form @submit.prevent="handleSubmit">
      <!-- 验证码输入组件 -->
      <VerificationCodeInput
        v-model:email="localNewEmail"
        v-model:code="localCode"
        :sending="sending"
        :code-sent="codeSent"
        :countdown="countdown"
        :disabled="processing"
        label="新邮箱地址"
        placeholder="请输入新邮箱地址"
        success-message="验证码已发送到新邮箱，请查收"
        @send-code="handleSendCode"
      />
      
      <!-- 操作按钮 -->
      <div class="d-flex gap-2" v-if="codeSent">
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="processing || !localCode || localCode.length !== 6"
        >
          <span v-if="processing" class="spinner-border spinner-border-sm me-2"></span>
          {{ processing ? '更改中...' : '✅ 确认更改' }}
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="$emit('cancel')"
          :disabled="processing"
        >
          取消
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import VerificationCodeInput from './VerificationCodeInput.vue'

export default {
  name: 'EmailChangeForm',
  
  components: {
    VerificationCodeInput
  },
  
  props: {
    currentEmail: {
      type: String,
      required: true
    },
    sending: {
      type: Boolean,
      default: false
    },
    processing: {
      type: Boolean,
      default: false
    },
    codeSent: {
      type: Boolean,
      default: false
    },
    countdown: {
      type: Number,
      default: 0
    }
  },
  
  emits: ['send-code', 'change', 'cancel'],
  
  setup(props, { emit }) {
    const localNewEmail = ref('')
    const localCode = ref('')
    
    const handleSendCode = () => {
      if (!localNewEmail.value) {
        return
      }
      
      // 检查新邮箱是否与当前邮箱相同
      if (localNewEmail.value.toLowerCase() === props.currentEmail.toLowerCase()) {
        emit('error', '新邮箱不能与当前邮箱相同')
        return
      }
      
      emit('send-code', localNewEmail.value)
    }
    
    const handleSubmit = () => {
      if (!localCode.value || localCode.value.length !== 6) {
        return
      }
      emit('change', {
        newEmail: localNewEmail.value,
        code: localCode.value
      })
    }
    
    return {
      localNewEmail,
      localCode,
      handleSendCode,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.alert {
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.d-flex.gap-2 {
  gap: 0.5rem;
}
</style>

