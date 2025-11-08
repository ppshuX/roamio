<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">✨ 旅行者资料</h5>
      <button
        v-if="!isEditing"
        class="btn btn-sm btn-outline-primary"
        @click="startEdit"
      >
        ✏️ 编辑
      </button>
    </div>
    
    <div class="card-body">
      <!-- 用户等级 -->
      <div class="mb-3">
        <label class="form-label">🎖️ 当前等级</label>
        <div>
          <span :class="'badge level-badge ' + getLevelClass(profileData.level)">
            {{ getLevelText(profileData.level) }}
          </span>
        </div>
        <small class="text-muted">根据旅行和评论数量自动计算</small>
      </div>
      
      <!-- 只读显示 -->
      <template v-if="!isEditing">
        <div class="info-display">
          <div class="info-card mb-3">
            <label class="info-label">📝 个人简介</label>
            <p class="info-content">{{ profileData.bio || '还没有写个人简介' }}</p>
          </div>
          <div class="info-card mb-3">
            <label class="info-label">🏷️ 个人标签</label>
            <div v-if="profileData.tags">
              <span 
                v-for="(tag, index) in profileData.tags.split(',')" 
                :key="index"
                class="badge bg-light text-dark me-1"
              >
                {{ tag.trim() }}
              </span>
            </div>
            <p v-else class="info-content text-muted">还没有添加标签</p>
          </div>
          <div class="info-card">
            <label class="info-label">🌍 访问过的国家</label>
            <p class="info-content">{{ profileData.visited_countries || '还没有记录' }}</p>
          </div>
        </div>
      </template>
      
      <!-- 编辑表单 -->
      <form v-else @submit.prevent="handleSave">
        <!-- 个人简介 -->
        <div class="mb-3">
          <label class="form-label">📝 个人简介</label>
          <textarea
            class="form-control"
            v-model="formData.bio"
            rows="4"
            maxlength="500"
            placeholder="介绍一下自己吧..."
          ></textarea>
          <small class="text-muted">{{ formData.bio?.length || 0 }}/500</small>
        </div>
        
        <!-- 用户标签 -->
        <div class="mb-3">
          <label class="form-label">🏷️ 个人标签</label>
          <input
            type="text"
            class="form-control"
            v-model="formData.tags"
            placeholder="例如：摄影爱好者,美食达人,户外运动"
            maxlength="200"
          />
          <small class="text-muted">逗号分隔，最多10个标签，每个不超过20字</small>
        </div>
        
        <!-- 访问过的国家 -->
        <div class="mb-3">
          <label class="form-label">🌍 访问过的国家</label>
          <input
            type="text"
            class="form-control"
            v-model="formData.visited_countries"
            placeholder="例如：中国,日本,泰国"
            maxlength="200"
          />
          <small class="text-muted">逗号分隔的国家列表</small>
        </div>
        
        <div class="d-flex gap-2">
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="updating"
          >
            <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
            {{ updating ? '保存中...' : '💾 保存' }}
          </button>
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="handleCancel"
            :disabled="updating"
          >
            取消
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'

export default {
  name: 'ProfileEditor',
  
  props: {
    bio: {
      type: String,
      default: ''
    },
    tags: {
      type: String,
      default: ''
    },
    visitedCountries: {
      type: String,
      default: ''
    },
    level: {
      type: String,
      default: 'novice'
    },
    updating: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['update', 'cancel'],
  
  setup(props, { emit }) {
    const isEditing = ref(false)
    const formData = ref({
      bio: '',
      tags: '',
      visited_countries: '',
      level: 'novice'
    })
    
    const profileData = computed(() => ({
      bio: props.bio,
      tags: props.tags,
      visited_countries: props.visitedCountries,
      level: props.level
    }))
    
    // 监听props变化，更新表单数据
    watch(() => [props.bio, props.tags, props.visitedCountries], ([bio, tags, visitedCountries]) => {
      formData.value.bio = bio || ''
      formData.value.tags = tags || ''
      formData.value.visited_countries = visitedCountries || ''
    }, { immediate: true })
    
    // 等级文本
    const getLevelText = (level) => {
      const levels = {
        'novice': '新手',
        'explorer': '探索者',
        'wanderer': '漫游者',
        'adventurer': '冒险家',
        'master': '旅行大师'
      }
      return levels[level] || '新手'
    }
    
    // 等级样式类
    const getLevelClass = (level) => {
      const classes = {
        'novice': 'level-novice',
        'explorer': 'level-explorer',
        'wanderer': 'level-wanderer',
        'adventurer': 'level-adventurer',
        'master': 'level-master'
      }
      return classes[level] || 'level-novice'
    }
    
    const startEdit = () => {
      formData.value = {
        bio: props.bio || '',
        tags: props.tags || '',
        visited_countries: props.visitedCountries || '',
        level: props.level || 'novice'
      }
      isEditing.value = true
    }
    
    const handleSave = () => {
      emit('update', {
        bio: formData.value.bio,
        tags: formData.value.tags,
        visited_countries: formData.value.visited_countries
      })
    }
    
    const handleCancel = () => {
      formData.value = {
        bio: props.bio || '',
        tags: props.tags || '',
        visited_countries: props.visitedCountries || '',
        level: props.level || 'novice'
      }
      isEditing.value = false
      emit('cancel')
    }
    
    // 当更新完成时，退出编辑模式
    watch(() => props.updating, (newVal) => {
      if (!newVal && isEditing.value) {
        isEditing.value = false
      }
    })
    
    return {
      isEditing,
      formData,
      profileData,
      startEdit,
      handleSave,
      handleCancel,
      getLevelText,
      getLevelClass
    }
  }
}
</script>

<style scoped>
/* 复用UserCenterView的样式 */
.info-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  transition: all 0.3s ease;
}

.info-label {
  font-size: 0.85rem;
  color: #6c757d;
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-content {
  color: #2c3e50;
  font-size: 1rem;
  line-height: 1.8;
  margin: 0;
  white-space: pre-wrap;
}

.badge.bg-light {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
  border: 1px solid #dee2e6;
  padding: 0.4rem 0.8rem;
  border-radius: 15px;
}

.level-badge {
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
  border-radius: 25px;
  font-weight: 700;
}

.level-novice {
  background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
  color: #666;
}

.level-explorer {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
  color: #ffffff !important;
  border: 1px solid #0d47a1 !important;
}

.level-wanderer {
  background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%) !important;
  color: #388e3c !important;
}

.level-adventurer {
  background: linear-gradient(135deg, #fff9c4 0%, #fff59d 100%) !important;
  color: #f57f17 !important;
}

.level-master {
  background: linear-gradient(135deg, #ffeb3b 0%, #ffc107 100%) !important;
  color: #f57f17 !important;
}
</style>

