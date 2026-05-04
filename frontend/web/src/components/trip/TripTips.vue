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
  margin-bottom: 1.5rem;
}

h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.6rem;
}

.tips-list li {
  padding: 0.7rem 0.9rem;
  background: linear-gradient(135deg, #fff9e6 0%, #fff3cc 100%);
  border: 2px solid #ffc107;
  border-radius: 6px;
  font-size: 0.85rem;
  line-height: 1.5;
  color: #333;
  box-shadow: 0 1px 4px rgba(255, 193, 7, 0.2);
}

@media (max-width: 768px) {
  .tips-list {
    grid-template-columns: 1fr;
  }
  .tips-list li {
    font-size: 0.8rem;
  }
}
</style>

