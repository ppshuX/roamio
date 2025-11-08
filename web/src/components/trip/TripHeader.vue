<template>
  <div class="card shadow-lg mb-4">
    <div class="card-body p-5">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <h1 class="mb-0">{{ title }}</h1>
        <!-- Ralendar 集成按钮 -->
        <AddToCalendarButton
          v-if="showCalendarButton"
          :trip-slug="tripSlug"
          :trip-title="title"
          :events="events"
        />
      </div>
      <p class="text-muted mb-0">{{ description }}</p>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import AddToCalendarButton from '@/components/AddToCalendarButton.vue'

export default defineComponent({
  name: 'TripHeader',

  components: {
    AddToCalendarButton
  },

  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    tripSlug: {
      type: String,
      required: true
    },
    showCalendarButton: {
      type: Boolean,
      default: false
    },
    events: {
      type: Array,
      default: () => []
    }
  }
})
</script>

<style scoped>
h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
}

.text-muted {
  font-size: 1.1rem;
  line-height: 1.6;
}

@media (max-width: 768px) {
  h1 {
    font-size: 1.8rem;
  }
}
</style>

