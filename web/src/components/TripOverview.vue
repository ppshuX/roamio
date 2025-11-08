<template>
  <div class="card">
    <div class="card-body">
      <h3 class="mb-3">📋 {{ title }}</h3>
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TripOverview',
  
  props: {
    title: {
      type: String,
      default: '行程概览'
    }
  }
}
</script>

<style scoped>
.card {
  background: #fff;
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.card-body {
  padding: 2rem;
}

.card-body h3 {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 0.8rem;
  margin-bottom: 1.5rem;
}

/* 为内部内容提供默认样式 */
:deep(h4) {
  color: #34495e;
  font-size: 1.1rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

:deep(p) {
  line-height: 1.8;
  color: #555;
  margin-bottom: 1rem;
}

:deep(ul), :deep(ol) {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

:deep(li) {
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

:deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

:deep(table), :deep(th), :deep(td) {
  border: 1px solid #ddd;
}

:deep(th), :deep(td) {
  padding: 0.75rem;
  text-align: left;
}

:deep(th) {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #2c3e50;
}

:deep(tr:hover) {
  background-color: #f9f9f9;
}

@media (max-width: 768px) {
  .card-body {
    padding: 1.5rem;
  }
  
  .card-body h3 {
    font-size: 1.1rem;
  }
}
</style>

