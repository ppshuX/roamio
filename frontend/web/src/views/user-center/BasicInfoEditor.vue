<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">基本信息</h5>
      <button
        v-if="!isEditing"
        class="btn btn-sm btn-outline-primary"
        @click="startEdit"
      >
        ✏️ 编辑
      </button>
    </div>
    
    <div class="card-body">
      <!-- 只读显示 -->
      <template v-if="!isEditing">
        <div class="info-display">
          <div class="info-card mb-3">
            <label class="info-label">👤 用户名</label>
            <p class="info-content">{{ formData.username || '未设置' }}</p>
          </div>
          <div class="info-card">
            <label class="info-label">🎂 生日</label>
            <p class="info-content">{{ formData.birthday || '未设置' }}</p>
          </div>
        </div>
      </template>
      
      <!-- 编辑表单 -->
      <form v-else @submit.prevent="handleSave">
        <div class="mb-3">
          <label class="form-label">👤 用户名</label>
          <input
            type="text"
            class="form-control"
            v-model="formData.username"
            required
            placeholder="请输入用户名"
          />
        </div>
        
        <div class="mb-3">
          <label class="form-label">🎂 生日</label>
          <input
            type="date"
            class="form-control"
            v-model="formData.birthday"
            placeholder="请选择生日"
          />
        </div>
        
        <div class="d-flex gap-2">
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="updating"
          >
            <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
            {{ updating ? '保存中...' : '💾 保存' }}
          </button>
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="handleCancel"
            :disabled="updating"
          >
            取消
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  username: {
    type: String,
    default: ''
  },
  birthday: {
    type: String,
    default: ''
  },
  updating: {
    type: Boolean,
    default: false
  },
  forceEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update', 'cancel'])

const isEditing = ref(false)
const formData = ref({
  username: '',
  birthday: ''
})

// 监听props变化，更新表单数据
watch([() => props.username, () => props.birthday], ([username, birthday]) => {
  formData.value = { username, birthday }
}, { immediate: true })

// 监听 forceEdit，外部触发编辑模式
watch(() => props.forceEdit, (newVal) => {
  if (newVal && !isEditing.value) {
    startEdit()
  } else if (!newVal && isEditing.value) {
    // 外部取消编辑时，也取消内部编辑
    handleCancel()
  }
})

const startEdit = () => {
  formData.value = {
    username: props.username,
    birthday: props.birthday
  }
  isEditing.value = true
}

const handleSave = () => {
  emit('update', { ...formData.value })
}

const handleCancel = () => {
  formData.value = {
    username: props.username,
    birthday: props.birthday
  }
  isEditing.value = false
  emit('cancel')
}

// 当更新完成时，退出编辑模式
watch(() => props.updating, (newVal) => {
  if (!newVal && isEditing.value) {
    isEditing.value = false
  }
})
</script>

<style scoped>

.info-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  transition: all 0.3s ease;
}

.info-label {
  font-size: 0.85rem;
  color: #6c757d;
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-content {
  color: #2c3e50;
  font-size: 1rem;
  line-height: 1.8;
  margin: 0;
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

.d-flex.gap-2 {
  gap: 0.5rem;
}
</style>

