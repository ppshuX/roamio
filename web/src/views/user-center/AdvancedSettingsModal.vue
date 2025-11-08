<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-content-advanced" @click.stop>
      <div class="modal-header">
        <h5 class="modal-title">⚙️ 高级设置</h5>
        <button type="button" class="btn-close" @click="close">✕</button>
      </div>
      <div class="modal-body">
        <div class="alert alert-warning">
          <h6 class="alert-heading">⚠️ 危险操作</h6>
          <p class="mb-0">删除账号将会永久删除您的所有数据，包括：</p>
          <ul class="mb-0 mt-2">
            <li>所有旅行计划</li>
            <li>所有评论和回复</li>
            <li>所有统计数据</li>
            <li>个人资料和头像</li>
          </ul>
          <p class="mb-0 mt-2"><strong>此操作无法撤销！</strong></p>
        </div>
        <button
          class="btn btn-danger w-100"
          @click="$emit('delete-account')"
        >
          🗑️ 删除账号
        </button>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="close">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdvancedSettingsModal',
  
  props: {
    show: {
      type: Boolean,
      required: true
    }
  },
  
  emits: ['close', 'delete-account'],
  
  setup(props, { emit }) {
    const close = () => {
      emit('close')
    }
    
    return {
      close
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content-advanced {
  background: white;
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #000;
}
</style>

