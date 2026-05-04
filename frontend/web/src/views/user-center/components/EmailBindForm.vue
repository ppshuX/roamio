<template>
  <div>
    <form @submit.prevent="handleSubmit">
      <!-- 验证码输入组件 -->
      <VerificationCodeInput
        v-model:email="localEmail"
        v-model:code="localCode"
        :sending="sending"
        :code-sent="codeSent"
        :countdown="countdown"
        :disabled="processing"
        label="邮箱地址"
        placeholder="请输入邮箱地址"
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
          {{ processing ? '绑定中...' : '✅ 绑定邮箱' }}
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="emit('cancel')"
          :disabled="processing"
        >
          取消
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import VerificationCodeInput from './VerificationCodeInput.vue'

const props = defineProps({
  currentEmail: {
    type: String,
    default: ''
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
})

const emit = defineEmits(['send-code', 'bind', 'cancel'])

const localEmail = ref(props.currentEmail || '')
const localCode = ref('')

// 监听 props 变化
watch(() => props.currentEmail, (newVal) => {
  localEmail.value = newVal || ''
})

const handleSendCode = () => {
  if (!localEmail.value) {
    return
  }
  emit('send-code', localEmail.value)
}

const handleSubmit = () => {
  if (!localCode.value || localCode.value.length !== 6) {
    return
  }
  emit('bind', {
    email: localEmail.value,
    code: localCode.value
  })
}
</script>

<style scoped>
.d-flex.gap-2 {
  gap: 0.5rem;
}
</style>

