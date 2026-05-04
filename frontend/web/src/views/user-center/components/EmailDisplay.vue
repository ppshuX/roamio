<template>
  <div>
    <!-- 已验证邮箱显示 -->
    <div v-if="email && verified" class="mb-3">
      <div class="alert alert-success">
        <strong>已绑定邮箱：</strong> {{ email }}
      </div>
      <button class="btn btn-outline-primary btn-sm" @click="emit('change-request')">
        🔄 更改邮箱
      </button>
    </div>
    
    <!-- 未绑定或未验证提示 -->
    <div v-else-if="!verified" class="mb-3">
      <div class="alert alert-warning">
        <strong>⚠️ 邮箱{{ email ? '未验证' : '未绑定' }}</strong>
        <p class="mb-0 small">绑定邮箱可以用于找回密码和接收重要通知</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  email: {
    type: String,
    default: ''
  },
  verified: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['change-request'])
</script>

<style scoped>
.alert {
  border-radius: 12px;
  padding: 1rem;
}
</style>

