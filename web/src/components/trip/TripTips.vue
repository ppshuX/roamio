<template>
  <div v-if="tips && tips.length" class="tips-section">
    <h4>💡 实用提示</h4>
    <ul class="tips-list">
      <li v-for="(tip, index) in tips" :key="index">
        {{ tip }}
      </li>
    </ul>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TripTips',

  props: {
    tips: {
      type: Array,
      default: () => []
    }
  }
})
</script>

<style scoped>
.tips-section {
  margin-bottom: 2rem;
}

h4 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  position: relative;
  padding: 1rem 1rem 1rem 3rem;
  margin-bottom: 0.8rem;
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
  border-left: 4px solid #ffc107;
  border-radius: 8px;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #2c3e50;
  transition: all 0.3s ease;
}

.tips-list li:hover {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.1) 100%);
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
}

.tips-list li::before {
  content: '💡';
  position: absolute;
  left: 0.8rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.3rem;
}

@media (max-width: 768px) {
  .tips-list li {
    padding: 0.8rem 0.8rem 0.8rem 2.5rem;
    font-size: 0.9rem;
  }

  .tips-list li::before {
    left: 0.5rem;
    font-size: 1.1rem;
  }
}
</style>

