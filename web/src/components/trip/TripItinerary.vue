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
  margin-bottom: 2rem;
}

h4 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.itinerary-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.itinerary-item {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border-left: 4px solid #764ba2;
  transition: all 0.3s ease;
}

.itinerary-item:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(118, 75, 162, 0.15);
}

.itinerary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.itinerary-day {
  font-size: 1.2rem;
  color: #764ba2;
  font-weight: 700;
}

.itinerary-time {
  font-size: 0.9rem;
  color: #666;
  background: rgba(118, 75, 162, 0.1);
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
}

.itinerary-content {
  font-size: 1rem;
  line-height: 1.7;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.itinerary-highlight {
  font-size: 0.95rem;
  color: #667eea;
  font-weight: 500;
  margin-top: 0.8rem;
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
}

@media (max-width: 768px) {
  .itinerary-item {
    padding: 1rem;
  }

  .itinerary-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .itinerary-day {
    font-size: 1.1rem;
  }

  .itinerary-time {
    font-size: 0.85rem;
  }

  .itinerary-content {
    font-size: 0.95rem;
  }
}
</style>

