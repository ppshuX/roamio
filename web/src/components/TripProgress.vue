<template>
  <div class="card">
    <div class="card-body">
      <h3 class="mb-3">🌊 旅行进度条</h3>
      <div class="progress-container">
        <div 
          class="progress-bar" 
          :style="{ width: progress + '%' }"
        >
          {{ progress }}%
        </div>
      </div>
      <p v-if="message" class="text-muted text-center mt-3 mb-0">
        {{ message }}
      </p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'TripProgress',
  
  props: {
    startDate: {
      type: String,
      default: null
    },
    endDate: {
      type: String,
      default: null
    }
  },
  
  setup(props) {
    const progress = ref(0)
    const message = ref('')
    
    const calculateProgress = () => {
      if (!props.startDate || !props.endDate) {
        progress.value = 50
        message.value = '旅行进度加载中...'
        return
      }
      
      const now = new Date()
      const start = new Date(props.startDate)
      const end = new Date(props.endDate)
      
      if (now < start) {
        progress.value = 0
        message.value = '旅行即将开始！'
      } else if (now > end) {
        progress.value = 100
        message.value = '旅行已结束，期待下次旅程！'
      } else {
        const total = end - start
        const elapsed = now - start
        progress.value = Math.round((elapsed / total) * 100)
        message.value = `旅行进行中，已完成 ${progress.value}%`
      }
    }
    
    onMounted(() => {
      calculateProgress()
    })
    
    return {
      progress,
      message
    }
  }
}
</script>

<style scoped>
.progress-container {
  background: #e0e0e0;
  border-radius: 20px;
  overflow: hidden;
  height: 28px;
  margin: 1rem 0;
}

.progress-bar {
  background: linear-gradient(90deg, #4caf50 0%, #45a049 100%);
  height: 100%;
  text-align: center;
  color: white;
  line-height: 28px;
  font-size: 14px;
  font-weight: 600;
  transition: width 0.6s ease;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}
</style>

