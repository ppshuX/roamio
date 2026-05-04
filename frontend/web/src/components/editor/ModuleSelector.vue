<template>
  <div class="card mb-4">
    <div class="card-header">
      <h5 class="mb-0">🧩 选择模块</h5>
    </div>
    <div class="card-body">
      <p class="text-muted mb-3">选择你想在旅行计划中展示的内容模块</p>
      <div class="modules-grid">
        <div
          v-for="module in modules"
          :key="module.id"
          class="module-card"
          :class="{ active: isEnabled(module.id) }"
          @click="$emit('toggle', module.id)"
        >
          <div class="module-icon">{{ module.icon }}</div>
          <div class="module-name">{{ module.name }}</div>
          <div class="module-desc">{{ module.description }}</div>
          <div class="module-check">
            <i v-if="isEnabled(module.id)" class="bi bi-check-circle-fill text-success"></i>
            <i v-else class="bi bi-circle text-muted"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModuleSelector',
  
  props: {
    modules: {
      type: Array,
      required: true
    },
    enabledModules: {
      type: Array,
      default: () => []
    }
  },
  
  emits: ['toggle'],
  
  setup(props) {
    const isEnabled = (moduleId) => {
      return props.enabledModules.includes(moduleId)
    }
    
    return {
      isEnabled
    }
  }
}
</script>

<style scoped>
.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.module-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.module-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.module-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.module-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.module-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.module-desc {
  font-size: 0.85rem;
  color: #666;
}

.module-check {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  font-size: 1.2rem;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 1.5rem;
}

.card-header h5 {
  margin: 0;
  font-weight: 600;
}
</style>

