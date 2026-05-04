<template>
  <div class="card shadow-lg mb-4">
    <div class="card-body p-5">
      <h1 class="mb-3">{{ title }}</h1>
      <p class="text-muted mb-0">{{ description }}</p>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TripHeader',

  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
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

