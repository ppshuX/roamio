<template>
  <!-- 悬浮按钮（仅移动端显示） -->
  <div v-if="isVisible && isMobile" class="floating-ralendar">
    <!-- 主按钮 -->
    <div
      ref="floatingBtn"
      class="floating-btn"
      :class="{ 'dragging': isDragging, 'near-trash': isNearTrash }"
      :style="buttonStyle"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
      @mousedown="handleMouseDown"
      @click="handleClick"
    >
      <img 
        src="/static/images/ralendar_logo_final.png" 
        alt="Ralendar"
        class="ralendar-icon"
      >
      
      <!-- 事项数量徽章 -->
      <span v-if="eventCount > 0" class="event-badge">
        {{ eventCount > 99 ? '99+' : eventCount }}
      </span>
    </div>
    
    <!-- 垃圾桶区域（拖拽时显示） -->
    <transition name="fade">
      <div v-if="isDragging" class="trash-zone" :class="{ 'active': isNearTrash }">
        <i class="bi bi-trash3"></i>
        <span>拖到这里隐藏</span>
      </div>
    </transition>
    
    <!-- 事项面板（展开时显示） -->
    <transition name="slide-up">
      <div v-if="isPanelOpen" class="events-panel">
        <div class="panel-header">
          <h5>
            <img 
              src="/static/images/ralendar_logo_final.png" 
              alt="Ralendar"
              class="panel-logo"
            >
            旅行事项
          </h5>
          <button @click="closePanel" class="btn-close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <div class="panel-body">
          <EventsSidebar :trip-id="tripId" @update-count="updateEventCount" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, defineComponent } from 'vue'
import EventsSidebar from './EventsSidebar.vue'

export default defineComponent({
  name: 'FloatingRalendarButton',
  
  components: {
    EventsSidebar
  },
  
  props: {
    tripId: {
      type: Number,
      required: true
    }
  },
  
  emits: ['toggle'],
  
  setup(props, { emit }) {
    const floatingBtn = ref(null)
    const isVisible = ref(true)
    const isPanelOpen = ref(false)
    const isDragging = ref(false)
    const isNearTrash = ref(false)
    const eventCount = ref(0)
    
    // 按钮位置
    const position = ref({
      x: window.innerWidth - 80, // 默认右下角
      y: window.innerHeight - 150
    })
    
    // 拖拽起始位置
    const dragStart = ref({ x: 0, y: 0 })
    
    // 检测是否为移动端
    const isMobile = computed(() => {
      return window.innerWidth <= 768
    })
    
    // 按钮样式
    const buttonStyle = computed(() => ({
      left: `${position.value.x}px`,
      top: `${position.value.y}px`
    }))
    
    /**
     * 更新事项数量
     */
    const updateEventCount = (count) => {
      eventCount.value = count
    }
    
    /**
     * 处理触摸开始（移动端）
     */
    const handleTouchStart = (e) => {
      if (isPanelOpen.value) return
      
      isDragging.value = true
      const touch = e.touches[0]
      dragStart.value = {
        x: touch.clientX - position.value.x,
        y: touch.clientY - position.value.y
      }
      e.preventDefault()
    }
    
    /**
     * 处理触摸移动（移动端）
     */
    const handleTouchMove = (e) => {
      if (!isDragging.value) return
      
      const touch = e.touches[0]
      position.value = {
        x: touch.clientX - dragStart.value.x,
        y: touch.clientY - dragStart.value.y
      }
      
      // 检测是否接近垃圾桶区域（底部中央）
      checkNearTrash(touch.clientX, touch.clientY)
      e.preventDefault()
    }
    
    /**
     * 处理触摸结束（移动端）
     */
    const handleTouchEnd = (e) => {
      if (!isDragging.value) return
      
      isDragging.value = false
      
      // 如果在垃圾桶区域，隐藏按钮
      if (isNearTrash.value) {
        hideButton()
      } else {
        // 吸附到边缘
        snapToEdge()
      }
      
      isNearTrash.value = false
      e.preventDefault()
    }
    
    /**
     * 处理鼠标按下（桌面端测试）
     */
    const handleMouseDown = (e) => {
      if (isPanelOpen.value) return
      
      isDragging.value = true
      dragStart.value = {
        x: e.clientX - position.value.x,
        y: e.clientY - position.value.y
      }
      
      const handleMouseMove = (e) => {
        if (!isDragging.value) return
        
        position.value = {
          x: e.clientX - dragStart.value.x,
          y: e.clientY - dragStart.value.y
        }
        
        checkNearTrash(e.clientX, e.clientY)
      }
      
      const handleMouseUp = () => {
        isDragging.value = false
        
        if (isNearTrash.value) {
          hideButton()
        } else {
          snapToEdge()
        }
        
        isNearTrash.value = false
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
      
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }
    
    /**
     * 检测是否接近垃圾桶
     */
    const checkNearTrash = (x, y) => {
      const trashZone = {
        x: window.innerWidth / 2 - 100,
        y: window.innerHeight - 150,
        width: 200,
        height: 100
      }
      
      isNearTrash.value = (
        x >= trashZone.x &&
        x <= trashZone.x + trashZone.width &&
        y >= trashZone.y &&
        y <= trashZone.y + trashZone.height
      )
    }
    
    /**
     * 吸附到边缘
     */
    const snapToEdge = () => {
      const btnWidth = 60
      const btnHeight = 60
      const margin = 20
      
      // 限制在屏幕范围内
      let x = Math.max(margin, Math.min(position.value.x, window.innerWidth - btnWidth - margin))
      let y = Math.max(margin, Math.min(position.value.y, window.innerHeight - btnHeight - margin))
      
      // 吸附到左右边缘
      if (x < window.innerWidth / 2) {
        x = margin // 吸附到左边
      } else {
        x = window.innerWidth - btnWidth - margin // 吸附到右边
      }
      
      position.value = { x, y }
      
      // 保存位置到 localStorage
      localStorage.setItem('ralendar_button_position', JSON.stringify(position.value))
    }
    
    /**
     * 隐藏按钮
     */
    const hideButton = () => {
      isVisible.value = false
      localStorage.setItem('ralendar_button_visible', 'false')
      emit('toggle', false)
    }
    
    /**
     * 显示按钮（从导航栏调用）
     */
    const showButton = () => {
      isVisible.value = true
      localStorage.setItem('ralendar_button_visible', 'true')
      emit('toggle', true)
    }
    
    /**
     * 点击按钮
     */
    const handleClick = () => {
      if (isDragging.value) return
      isPanelOpen.value = true
    }
    
    /**
     * 关闭面板
     */
    const closePanel = () => {
      isPanelOpen.value = false
    }
    
    /**
     * 处理窗口大小变化
     */
    const handleResize = () => {
      // 确保按钮在屏幕范围内
      snapToEdge()
    }
    
    /**
     * 初始化
     */
    onMounted(() => {
      // 恢复保存的位置
      const savedPosition = localStorage.getItem('ralendar_button_position')
      if (savedPosition) {
        position.value = JSON.parse(savedPosition)
      }
      
      // 恢复可见性
      const savedVisible = localStorage.getItem('ralendar_button_visible')
      if (savedVisible !== null) {
        isVisible.value = savedVisible === 'true'
      }
      
      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })
    
    return {
      floatingBtn,
      isVisible,
      isPanelOpen,
      isDragging,
      isNearTrash,
      eventCount,
      isMobile,
      buttonStyle,
      updateEventCount,
      handleTouchStart,
      handleTouchMove,
      handleTouchEnd,
      handleMouseDown,
      handleClick,
      closePanel,
      showButton
    }
  }
})
</script>

<style scoped>
/* 悬浮按钮容器 */
.floating-ralendar {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
}

.floating-ralendar > * {
  pointer-events: auto;
}

/* 主按钮 */
.floating-btn {
  position: fixed;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.floating-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
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

/* Ralendar 图标 */
.ralendar-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

/* 事项数量徽章 */
.event-badge {
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

/* 垃圾桶区域 */
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

/* 事项面板 */
.events-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 80vh;
  background: white;
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -4px 30px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 10000;
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
  padding: 0;
}

/* 动画 */
@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
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

/* 桌面端隐藏 */
@media (min-width: 769px) {
  .floating-ralendar {
    display: none;
  }
}
</style>

