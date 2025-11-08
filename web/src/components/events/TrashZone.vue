<template>
  <transition name="fade">
    <div v-if="show" class="trash-zone" :class="{ 'active': isActive }">
      <i class="bi bi-trash3"></i>
      <span>拖到这里隐藏</span>
    </div>
  </transition>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TrashZone',
  
  props: {
    show: {
      type: Boolean,
      default: false
    },
    isActive: {
      type: Boolean,
      default: false
    }
  }
})
</script>

<style scoped>
.trash-zone {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  width: 120px;
  height: 120px;
  background: rgba(255, 107, 107, 0.9);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  box-shadow: 0 4px 20px rgba(255, 107, 107, 0.4);
  transition: all 0.3s ease;
  z-index: 9997;
}

.trash-zone.active {
  transform: translateX(-50%) scale(1.2);
  background: rgba(238, 90, 111, 1);
  box-shadow: 0 6px 30px rgba(238, 90, 111, 0.6);
}

.trash-zone i {
  font-size: 32px;
  margin-bottom: 8px;
}

.trash-zone span {
  font-size: 12px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

