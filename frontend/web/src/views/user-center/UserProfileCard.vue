<template>
  <div class="card shadow-sm">
    <div class="card-body text-center p-4">
      <!-- 头像 -->
      <div class="avatar-container mb-3">
        <img
          :src="avatar"
          alt="头像"
          class="rounded-circle"
          width="120"
          height="120"
        />
        <button
          class="btn btn-sm btn-light avatar-upload-btn"
          @click="triggerFileInput"
        >
          📷
        </button>
        <input
          ref="avatarInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleAvatarChange"
        />
      </div>
      
      <!-- 用户名 -->
      <h4 class="username-display mb-1">{{ username }}</h4>
      <p class="email-display mb-3">{{ email || '未设置邮箱' }}</p>
      
      <!-- 标签和等级 -->
      <div class="mb-3 d-flex gap-2 justify-content-center align-items-center flex-wrap">
        <span v-if="isAdmin" class="badge bg-danger">管理员</span>
        <span v-else class="badge bg-primary">普通用户</span>
        <span v-if="level" :class="'badge level-badge-small ' + getLevelClass(level)">
          {{ getLevelText(level) }}
        </span>
        <span v-else class="badge level-badge-small level-novice">
          未知等级
        </span>
      </div>
      
      <!-- 注册时间 -->
      <small class="text-muted">
        注册时间：{{ formatDate(dateJoined) }}
      </small>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  username: {
    type: String,
    required: true
  },
  email: {
    type: String,
    default: ''
  },
  avatar: {
    type: String,
    required: true
  },
  isAdmin: {
    type: Boolean,
    default: false
  },
  level: {
    type: String,
    required: true
  },
  dateJoined: {
    type: String,
    required: true
  },
  getLevelText: {
    type: Function,
    required: true
  },
  getLevelClass: {
    type: Function,
    required: true
  },
  formatDate: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['avatar-change'])

const avatarInput = ref(null)

const triggerFileInput = () => {
  avatarInput.value.click()
}

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    emit('avatar-change', file)
  }
}
</script>

<style scoped>
.avatar-container {
  position: relative;
  display: inline-block;
}

.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.username-display {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.email-display {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.level-badge-small {
  font-size: 0.8rem !important;
  padding: 0.5rem 1rem !important;
  border-radius: 20px !important;
  font-weight: 600 !important;
  display: inline-block !important;
  border: 1px solid transparent !important;
}

.level-badge-small.level-novice {
  background: var(--bs-secondary-bg-subtle, #f8fafc) !important;
  color: var(--bs-secondary-text-emphasis, #475569) !important;
  border-color: var(--bs-secondary-border-subtle, #e2e8f0) !important;
}

.level-badge-small.level-explorer {
  background: var(--bs-primary-bg-subtle, var(--roamio-primary-muted)) !important;
  color: var(--roamio-primary-active) !important;
  border-color: var(--bs-primary-border-subtle, #99f6e4) !important;
}

.level-badge-small.level-wanderer {
  background: var(--bs-success-bg-subtle, #f0fdf4) !important;
  color: var(--bs-success-text-emphasis, #166534) !important;
  border-color: var(--bs-success-border-subtle, #bbf7d0) !important;
}

.level-badge-small.level-adventurer {
  background: var(--bs-warning-bg-subtle, #fffbeb) !important;
  color: var(--bs-warning-text-emphasis, #92400e) !important;
  border-color: var(--bs-warning-border-subtle, #fde68a) !important;
}

.level-badge-small.level-master {
  background: #fff7ed !important;
  color: #9a3412 !important;
  border-color: #fed7aa !important;
}
</style>

