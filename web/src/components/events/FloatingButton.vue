<template>
  <div
    ref="floatingBtn"
    class="floating-btn"
    :class="{ 'dragging': isDragging, 'near-trash': isNearTrash }"
    :style="buttonStyle"
    @touchstart="$emit('touchstart', $event)"
    @touchmove="$emit('touchmove', $event)"
    @touchend="$emit('touchend', $event)"
    @mousedown="$emit('mousedown', $event)"
    @click="$emit('click', $event)"
  >
    <img 
      :src="iconSrc" 
      :alt="iconAlt"
      class="icon"
    >
    
    <!-- 徽章 -->
    <span v-if="badge > 0" class="badge">
      {{ badge > 99 ? '99+' : badge }}
    </span>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'FloatingButton',
  
  props: {
    position: {
      type: Object,
      required: true
    },
    isDragging: {
      type: Boolean,
      default: false
    },
    isNearTrash: {
      type: Boolean,
      default: false
    },
    badge: {
      type: Number,
      default: 0
    },
    iconSrc: {
      type: String,
      default: '/static/images/ralendar_logo_final.png'
    },
    iconAlt: {
      type: String,
      default: 'Ralendar'
    }
  },
  
  emits: ['touchstart', 'touchmove', 'touchend', 'mousedown', 'click'],
  
  setup(props) {
    const buttonStyle = {
      left: `${props.position.x}px`,
      top: `${props.position.y}px`
    }
    
    return {
      buttonStyle
    }
  }
})
</script>

<style scoped>
.floating-btn {
  position: fixed;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease, opacity 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  z-index: 9998;
  opacity: 0.9;
}

.floating-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
  opacity: 1;
}

.floating-btn:active {
  transform: scale(0.95);
}

.floating-btn.dragging {
  transition: none;
  opacity: 0.8;
  transform: scale(1.15);
}

.floating-btn.near-trash {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  animation: shake 0.3s ease-in-out infinite;
}

.icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4757;
  color: white;
  font-size: 11px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(255, 71, 87, 0.4);
}

@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}
</style>

