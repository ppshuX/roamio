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
  margin-bottom: 1.5rem;
}

h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.highlights-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.highlights-list li {
  padding: 0.7rem 1rem;
  background: linear-gradient(135deg, #fff5e6 0%, #ffe8cc 100%);
  border-left: 4px solid #ff9800;
  border-radius: 6px;
  font-size: 0.9rem;
  line-height: 1.5;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

@media (max-width: 768px) {
  .highlights-list li {
    padding: 0.6rem 0.8rem;
    font-size: 0.85rem;
  }
}
</style>

