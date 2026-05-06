<template>
  <div v-if="basicInfo" class="basic-info-section">
    <h4>🧭 基本信息</h4>
    <div class="info-grid">
      <div v-if="basicInfo.participants" class="info-item">
        <span class="info-label">👥 Roamioer：</span>
        <span class="info-value">{{ basicInfo.participants }}</span>
      </div>
      <div v-if="basicInfo.departure" class="info-item">
        <span class="info-label">🚩 出发地：</span>
        <span class="info-value">{{ basicInfo.departure }}</span>
      </div>
      <div v-if="basicInfo.destination" class="info-item">
        <span class="info-label">🎯 目的地：</span>
        <span class="info-value">{{ basicInfo.destination }}</span>
      </div>
      <div v-if="basicInfo.transport" class="info-item">
        <span class="info-label">🚗 交通方式：</span>
        <span class="info-value">{{ basicInfo.transport }}</span>
      </div>
      <div v-if="basicInfo.accommodation" class="info-item">
        <span class="info-label">🏨 住宿：</span>
        <span class="info-value">{{ basicInfo.accommodation }}</span>
      </div>
      <div v-if="basicInfo.duration" class="info-item">
        <span class="info-label">⏱️ 行程时长：</span>
        <span class="info-value">{{ basicInfo.duration }}</span>
      </div>
      <div v-if="basicInfo.budget" class="info-item">
        <span class="info-label">💰 预算：</span>
        <span class="info-value">{{ basicInfo.budget }}</span>
      </div>
      <div v-if="basicInfo.theme" class="info-item">
        <span class="info-label">🎨 主题：</span>
        <span class="info-value">{{ basicInfo.theme }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TripBasicInfo',

  props: {
    basicInfo: {
      type: Object,
      default: null
    }
  }
})
</script>

<style scoped>
.basic-info-section {
  margin-bottom: 1.5rem;
}

h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  background: #f5f7fa;
  border-radius: 6px;
  border-left: 3px solid var(--roamio-primary);
  border: 1px solid #e8eaf0;
}

.info-label {
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
}

.info-value {
  font-size: 0.95rem;
  font-weight: 500;
  color: #333;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>

