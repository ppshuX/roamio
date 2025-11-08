<template>
  <div v-if="isVisible" class="global-ralendar">
    <!-- 悬浮按钮 -->
    <FloatingButton
      :position="position"
      :is-dragging="isDragging"
      :is-near-trash="isNearTrash"
      :badge="todayEventCount"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
      @mousedown="handleMouseDown"
      @click="handleClick"
    />
    
    <!-- 垃圾桶 -->
    <TrashZone 
      :show="isDragging"
      :is-active="isNearTrash"
    />
    
    <!-- 快捷面板 -->
    <QuickPanel 
      :show="isPanelOpen"
      title="今日事项"
      @close="closePanel"
    >
      <p class="text-muted text-center py-4">
        快捷添加功能开发中...
      </p>
      <div class="text-center">
        <a 
          href="https://ralendar.com" 
          target="_blank" 
          class="btn btn-primary btn-sm"
        >
          <i class="bi bi-box-arrow-up-right me-1"></i>
          访问 Ralendar 完整版
        </a>
      </div>
    </QuickPanel>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, defineComponent } from 'vue'
import FloatingButton from './FloatingButton.vue'
import TrashZone from './TrashZone.vue'
import QuickPanel from './QuickPanel.vue'

export default defineComponent({
  name: 'GlobalRalendarButton',
  
  components: {
    FloatingButton,
    TrashZone,
    QuickPanel
  },
  
  setup() {
    const isVisible = ref(true)
    const isPanelOpen = ref(false)
    const isDragging = ref(false)
    const isNearTrash = ref(false)
    const todayEventCount = ref(0)
    
    // 按钮位置
    const position = ref({
      x: typeof window !== 'undefined' ? window.innerWidth - 80 : 0,
      y: typeof window !== 'undefined' ? window.innerHeight - 150 : 0
    })
    
    // 拖拽起始位置
    const dragStart = ref({ x: 0, y: 0 })
    
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
      
      checkNearTrash(touch.clientX, touch.clientY)
      e.preventDefault()
    }
    
    /**
     * 处理触摸结束（移动端）
     */
    const handleTouchEnd = (e) => {
      if (!isDragging.value) return
      
      isDragging.value = false
      
      if (isNearTrash.value) {
        hideButton()
      } else {
        snapToEdge()
      }
      
      isNearTrash.value = false
      e.preventDefault()
    }
    
    /**
     * 处理鼠标按下（桌面端）
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
      
      let x = Math.max(margin, Math.min(position.value.x, window.innerWidth - btnWidth - margin))
      let y = Math.max(margin, Math.min(position.value.y, window.innerHeight - btnHeight - margin))
      
      if (x < window.innerWidth / 2) {
        x = margin
      } else {
        x = window.innerWidth - btnWidth - margin
      }
      
      position.value = { x, y }
      localStorage.setItem('global_ralendar_position', JSON.stringify(position.value))
    }
    
    /**
     * 隐藏按钮
     */
    const hideButton = () => {
      isVisible.value = false
      localStorage.setItem('ralendar_floating_enabled', 'false')
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
      snapToEdge()
    }
    
    /**
     * 初始化
     */
    onMounted(() => {
      const savedPosition = localStorage.getItem('global_ralendar_position')
      if (savedPosition) {
        position.value = JSON.parse(savedPosition)
      }
      
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })
    
    return {
      position,
      isVisible,
      isPanelOpen,
      isDragging,
      isNearTrash,
      todayEventCount,
      handleTouchStart,
      handleTouchMove,
      handleTouchEnd,
      handleMouseDown,
      handleClick,
      closePanel
    }
  }
})
</script>

<style scoped>
.global-ralendar {
  position: fixed;
  z-index: 9998;
  pointer-events: none;
}

.global-ralendar > * {
  pointer-events: auto;
}
</style>

