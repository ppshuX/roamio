<template>
  <div v-if="itinerary && itinerary.length" class="itinerary-section">
    <h4>🗓️ 详细行程</h4>
    <div class="itinerary-list">
      <div v-for="(item, index) in itinerary" :key="index" class="itinerary-item">
        <div class="itinerary-header">
          <strong class="itinerary-day">{{ item.day }}</strong>
          <span v-if="item.time" class="itinerary-time">⏰ {{ item.time }}</span>
        </div>
        <div class="itinerary-content">{{ item.content }}</div>
        <div v-if="item.highlight" class="itinerary-highlight">
          ✨ {{ item.highlight }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TripItinerary',

  props: {
    itinerary: {
      type: Array,
      default: () => []
    }
  }
})
</script>

<style scoped>
.itinerary-section {
  margin-bottom: 1.5rem;
}

h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.itinerary-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.itinerary-item {
  padding: 1rem;
  background: linear-gradient(135deg, #f0e6ff 0%, #e6d9ff 100%);
  border: 2px solid #9c27b0;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(156, 39, 176, 0.15);
}

.itinerary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.itinerary-day {
  font-size: 1rem;
  color: #9c27b0;
  font-weight: 600;
}

.itinerary-time {
  font-size: 0.8rem;
  color: #666;
  background: rgba(156, 39, 176, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
}

.itinerary-content {
  font-size: 0.85rem;
  line-height: 1.6;
  color: #333;
  white-space: pre-line;
}

.itinerary-highlight {
  font-size: 0.8rem;
  color: #9c27b0;
  font-weight: 500;
  margin-top: 0.6rem;
  padding: 0.4rem 0.8rem;
  background: rgba(156, 39, 176, 0.1);
  border-radius: 6px;
}

@media (max-width: 768px) {
  .itinerary-item {
    padding: 0.8rem;
  }
  .itinerary-content {
    font-size: 0.8rem;
  }
}
</style>

