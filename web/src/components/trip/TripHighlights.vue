<template>
  <div v-if="highlights && highlights.length" class="highlights-section">
    <h4>📍 行程亮点</h4>
    <ul class="highlights-list">
      <li v-for="(highlight, index) in highlights" :key="index">
        {{ highlight }}
      </li>
    </ul>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TripHighlights',

  props: {
    highlights: {
      type: Array,
      default: () => []
    }
  }
})
</script>

<style scoped>
.highlights-section {
  margin-bottom: 2rem;
}

h4 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.highlights-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.highlights-list li {
  position: relative;
  padding: 1rem 1.2rem;
  margin-bottom: 0.8rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  border-left: 4px solid #667eea;
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.6;
  transition: all 0.3s ease;
}

.highlights-list li:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.highlights-list li::before {
  content: '✨';
  position: absolute;
  left: -0.5rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
}

@media (max-width: 768px) {
  .highlights-list li {
    padding: 0.8rem 1rem;
    font-size: 0.95rem;
  }
}
</style>

