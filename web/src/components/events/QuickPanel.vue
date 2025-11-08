<template>
  <transition name="slide-up">
    <div v-if="show" class="quick-panel">
      <div class="panel-header">
        <h5>
          <img 
            src="/static/images/ralendar_logo_final.png" 
            alt="Ralendar"
            class="panel-logo"
          >
          {{ title }}
        </h5>
        <button @click="$emit('close')" class="btn-close">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      
      <div class="panel-body">
        <slot></slot>
      </div>
    </div>
  </transition>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuickPanel',
  
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '今日事项'
    }
  },
  
  emits: ['close']
})
</script>

<style scoped>
.quick-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 60vh;
  background: white;
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -4px 30px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 9999;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px 20px 0 0;
}

.panel-header h5 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.panel-logo {
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.btn-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.3s ease;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.slide-up-enter-active {
  transition: transform 0.3s ease-out;
}

.slide-up-leave-active {
  transition: transform 0.3s ease-in;
}

.slide-up-enter-from {
  transform: translateY(100%);
}

.slide-up-leave-to {
  transform: translateY(100%);
}
</style>

