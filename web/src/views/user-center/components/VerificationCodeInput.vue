<template>
  <div>
    <!-- 邮箱输入 -->
    <div class="mb-3">
      <label class="form-label">
        📧 {{ label }} <span class="text-danger">*</span>
      </label>
      <div class="input-group">
        <input
          type="email"
          class="form-control"
          :value="email"
          @input="$emit('update:email', $event.target.value)"
          :disabled="disabled"
          :placeholder="placeholder"
          required
        />
        <button
          type="button"
          class="btn btn-outline-primary"
          :disabled="!email || sending || countdown > 0 || disabled"
          @click="$emit('send-code')"
        >
          <span v-if="sending" class="spinner-border spinner-border-sm me-1"></span>
          <span v-else-if="countdown > 0">{{ countdown }}秒</span>
          <span v-else>发送验证码</span>
        </button>
      </div>
      <small v-if="codeSent && successMessage" class="text-success">
        {{ successMessage }}
      </small>
    </div>
    
    <!-- 验证码输入 -->
    <div class="mb-3" v-if="codeSent">
      <label class="form-label">🔐 验证码 <span class="text-danger">*</span></label>
      <input
        type="text"
        class="form-control"
        :value="code"
        @input="$emit('update:code', $event.target.value)"
        :disabled="disabled"
        placeholder="请输入6位验证码"
        maxlength="6"
        required
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'VerificationCodeInput',
  
  props: {
    email: {
      type: String,
      default: ''
    },
    code: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: '邮箱地址'
    },
    placeholder: {
      type: String,
      default: '请输入邮箱地址'
    },
    sending: {
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
    },
    disabled: {
      type: Boolean,
      default: false
    },
    successMessage: {
      type: String,
      default: '验证码已发送，请查收邮箱'
    }
  },
  
  emits: ['update:email', 'update:code', 'send-code']
}
</script>

<style scoped>
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
</style>

