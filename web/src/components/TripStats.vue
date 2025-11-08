<template>
  <div class="stats-card">
    <div class="stats-container">
      <div class="stat-item">
        <span class="stat-icon">👁️</span>
        <span class="stat-text">浏览量：<strong>{{ views }}</strong></span>
      </div>
      <div class="stat-divider">｜</div>
      <div class="stat-item">
        <span class="stat-icon">❤️</span>
        <span class="stat-text">点赞：<strong>{{ likes }}</strong></span>
      </div>
    </div>
    <button 
      class="like-btn" 
      @click="handleLike"
      :disabled="liking || !canLike"

      title="点赞（仅公开行程可用）"
    >
      <span v-if="liking" class="spinner-border spinner-border-sm me-2"></span>
      👍 {{ liking ? '点赞中...' : '点赞' }}
    </button>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'TripStats',
  
  props: {
    views: {
      type: Number,
      default: 0
    },
    likes: {
      type: Number,
      default: 0
    },
    canLike: {
      type: Boolean,
      default: true
    }
  },
  
  emits: ['like'],
  
  setup(props, { emit }) {
    const liking = ref(false)
    
    const handleLike = async () => {
      liking.value = true
      try {
        await emit('like')
      } finally {
        setTimeout(() => {
          liking.value = false
        }, 500)
      }
    }
    
    return {
      liking,
      handleLike
    }
  }
}
</script>

<style scoped>
.stats-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.stats-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-text {
  color: #555;
}

.stat-text strong {
  color: #2c3e50;
  font-size: 1.2rem;
}

.stat-divider {
  color: #ccc;
  font-size: 1.2rem;
}

.like-btn {
  display: inline-block;
  padding: 0.6rem 1.5rem;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
}

.like-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

.like-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .stats-container {
    font-size: 1rem;
    gap: 1rem;
  }
  
  .stat-icon {
    font-size: 1.3rem;
  }
  
  .like-btn {
    font-size: 0.95rem;
    padding: 0.5rem 1.2rem;
  }
}
</style>

