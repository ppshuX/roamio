<template>
  <div class="action-buttons">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="$emit('back')" title="返回首页">
      🏠
    </button>
    
    <!-- 跳转到评论按钮 -->
    <button class="scroll-btn" @click="$emit('scroll-to-comments')" title="跳到评论区">
      ⬇️
    </button>
    
    <!-- 背景音乐按钮 -->
    <button 
      class="music-btn" 
      @click="$emit('toggle-music')" 
      :title="isPlaying ? '暂停音乐' : '播放音乐'"
    >
      {{ isPlaying ? '🔊' : '🔇' }}
    </button>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TripActionButtons',

  props: {
    isPlaying: {
      type: Boolean,
      default: false
    }
  },

  emits: ['back', 'scroll-to-comments', 'toggle-music']
})
</script>

<style scoped>
/* 返回按钮 */
.back-btn {
  position: fixed;
  top: 100px;
  left: 20px;
  background: var(--roamio-primary);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 1.8rem;
  cursor: pointer;
  z-index: 1000;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  opacity: 0.7;
}

.back-btn:hover {
  background: var(--roamio-primary-active);
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(var(--bs-primary-rgb), 0.4);
  opacity: 1;
}

/* 音乐按钮 */
.music-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
}

.music-btn:hover {
  background: white;
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  opacity: 1;
}

/* 跳转到评论按钮 */
.scroll-btn {
  position: fixed;
  top: 100px;
  right: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f7f7ff 100%);
  border: 2px solid rgba(0, 0, 0, 0.05);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 1.8rem;
  cursor: pointer;
  z-index: 1000;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  opacity: 0.7;
}

.scroll-btn:hover {
  background: linear-gradient(135deg, #ffffff 0%, #f0f0ff 100%);
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
  opacity: 1;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .back-btn,
  .scroll-btn {
    width: 45px;
    height: 45px;
    font-size: 1.5rem;
    top: 80px;
  }

  .back-btn {
    left: 15px;
  }

  .scroll-btn {
    right: 15px;
  }

  .music-btn {
    width: 50px;
    height: 50px;
    font-size: 20px;
    bottom: 20px;
    right: 20px;
  }
}
</style>

