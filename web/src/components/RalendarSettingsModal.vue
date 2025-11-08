<template>
  <transition name="fade">
    <div v-if="show" class="modal-overlay">
      <div class="modal-dialog">
        <!-- 头部 -->
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-calendar-check me-2"></i>
            Ralendar 快捷工具
          </h5>
          <button type="button" class="btn-close" @click="handleClose" aria-label="Close">
            ✕
          </button>
        </div>
        
        <!-- 内容 -->
        <div class="modal-body">
          <!-- 悬浮窗设置 -->
          <div class="setting-item mb-3">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="fw-semibold mb-1">悬浮窗</div>
                <p class="text-muted small mb-0">在所有页面显示快捷按钮</p>
              </div>
              <div class="toggle-switch" @click="toggleSwitch">
                <div class="slider" :class="{ active: floatingEnabled }">
                  <div class="slider-circle"></div>
                </div>
              </div>
            </div>
          </div>
          
          <hr>
          
          <!-- 访问完整版 -->
          <div class="setting-item">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="fw-semibold mb-1">访问完整版</div>
                <p class="text-muted small mb-0">查看月历、设置提醒</p>
              </div>
              <a 
                href="https://ralendar.com" 
                target="_blank" 
                class="btn btn-outline-primary btn-sm"
              >
                <i class="bi bi-box-arrow-up-right"></i>
              </a>
            </div>
          </div>
        </div>
        
        <!-- 底部按钮 -->
        <div class="modal-footer">
          <button 
            type="button"
            class="btn btn-secondary" 
            @click="handleClose"
          >
            取消
          </button>
          <button 
            type="button"
            class="btn btn-primary" 
            @click="handleSave"
            :disabled="saving"
          >
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-check-lg me-1"></i>
            保存
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, watch, defineComponent } from 'vue'

export default defineComponent({
  name: 'RalendarSettingsModal',
  
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['close', 'saved'],
  
  setup(props, { emit }) {
    const floatingEnabled = ref(false)
    const saving = ref(false)
    
    // 监听 show 变化，加载设置
    watch(() => props.show, (newVal) => {
      if (newVal) {
        const saved = localStorage.getItem('ralendar_floating_enabled')
        floatingEnabled.value = saved === 'true'
      }
    })
    
    const handleSave = async () => {
      saving.value = true
      try {
        localStorage.setItem('ralendar_floating_enabled', floatingEnabled.value.toString())
        emit('saved', floatingEnabled.value)
        emit('close')
        window.location.reload()
      } catch (error) {
        alert('保存失败：' + error.message)
      } finally {
        saving.value = false
      }
    }
    
    const handleClose = () => {
      emit('close')
    }
    
    const toggleSwitch = () => {
      floatingEnabled.value = !floatingEnabled.value
      console.log('Toggle clicked, new value:', floatingEnabled.value)
    }
    
    return {
      floatingEnabled,
      saving,
      handleSave,
      handleClose,
      toggleSwitch
    }
  }
})
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
  z-index: 99999;
  padding: 20px;
  pointer-events: auto;
}

.modal-dialog {
  background: white;
  border-radius: 12px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
  position: relative;
  z-index: 100000;
  pointer-events: auto;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.btn-close {
  background: #f0f0f0;
  border: none;
  font-size: 24px;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  padding: 0;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  line-height: 1;
}

.btn-close:hover {
  background: #e0e0e0;
  color: #000;
  transform: scale(1.1);
}

.modal-body {
  padding: 20px;
}

.setting-item {
  margin-bottom: 0;
}

/* iOS 风格滑动开关 */
.toggle-switch {
  display: inline-block;
  width: 50px;
  height: 28px;
  flex-shrink: 0;
  cursor: pointer;
  user-select: none;
}

.slider {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: #ccc;
  border-radius: 28px;
  transition: all 0.3s ease;
}

.slider.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.slider-circle {
  position: absolute;
  height: 22px;
  width: 22px;
  left: 3px;
  top: 3px;
  background-color: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.slider.active .slider-circle {
  transform: translateX(22px);
}

.toggle-switch:active .slider-circle {
  width: 26px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 0 0 12px 12px;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 576px) {
  .modal-dialog {
    max-width: 100%;
    border-radius: 12px 12px 0 0;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
  }
}
</style>
