<template>
  <div class="card shadow-sm mt-3">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">📊 我的统计</h5>
      <button class="btn btn-sm btn-outline-secondary" @click="emit('refresh')" title="刷新统计">
        🔄
      </button>
    </div>
    <div class="card-body">
      <div class="row text-center">
        <div class="col-12 mb-3">
          <div class="stat-box-small">
            <h4 class="text-primary mb-1">{{ stats.comments_count || 0 }}</h4>
            <p class="text-muted mb-0 small">评论数</p>
          </div>
        </div>
        <div class="col-6 mb-3">
          <div class="stat-box-small">
            <h4 class="text-success mb-1">{{ stats.trips_count || 0 }}</h4>
            <p class="text-muted mb-0 small">总旅行数</p>
          </div>
        </div>
        <div class="col-6 mb-3">
          <div class="stat-box-small">
            <h4 class="text-warning mb-1">{{ stats.public_trips_count || 0 }}</h4>
            <p class="text-muted mb-0 small">公开旅行（算等级）</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      comments_count: 0,
      trips_count: 0,
      public_trips_count: 0
    })
  }
})

const emit = defineEmits(['refresh'])
</script>

<style scoped>
.stat-box-small {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-box-small:hover {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>

