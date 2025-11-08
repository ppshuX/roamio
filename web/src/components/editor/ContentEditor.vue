<template>
  <div>
    <!-- 基本信息 -->
    <div v-if="isModuleEnabled('basicInfo')" class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">ℹ️ 基本信息</h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label">出发地</label>
            <input v-model="content.basicInfo.departure" type="text" class="form-control" />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">目的地</label>
            <input v-model="content.basicInfo.destination" type="text" class="form-control" />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">交通方式</label>
            <input v-model="content.basicInfo.transport" type="text" class="form-control" placeholder="例如：高铁往返" />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">住宿安排</label>
            <input v-model="content.basicInfo.accommodation" type="text" class="form-control" />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 行程亮点 -->
    <div v-if="isModuleEnabled('highlights')" class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">✨ 行程亮点</h5>
        <button class="btn btn-sm btn-light" @click="addHighlight">
          ➕ 添加
        </button>
      </div>
      <div class="card-body">
        <div v-for="(highlight, index) in content.highlights" :key="index" class="mb-3">
          <div class="input-group">
            <input
              v-model="content.highlights[index]"
              type="text"
              class="form-control"
              placeholder="例如：🏖️ 厦门植物园 - 热带雨林奇观"
            />
            <button class="btn btn-outline-danger" @click="removeHighlight(index)" title="删除">
              🗑️
            </button>
          </div>
        </div>
        <p v-if="content.highlights.length === 0" class="text-muted text-center py-3 mb-0">
          暂无亮点，点击上方"添加"按钮
        </p>
      </div>
    </div>
    
    <!-- 详细行程 -->
    <div v-if="isModuleEnabled('itinerary')" class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">📅 详细行程</h5>
        <button class="btn btn-sm btn-light" @click="addItinerary">
          ➕ 添加一天
        </button>
      </div>
      <div class="card-body">
        <div v-for="(item, index) in content.itinerary" :key="index" class="itinerary-item mb-4">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6>第{{ index + 1 }}天</h6>
            <button class="btn btn-sm btn-outline-danger" @click="removeItinerary(index)" title="删除">
              🗑️
            </button>
          </div>
          <div class="mb-2">
            <input
              v-model="item.day"
              type="text"
              class="form-control form-control-sm"
              placeholder="例如：第一天（6月22日）"
            />
          </div>
          <div class="mb-2">
            <input
              v-model="item.time"
              type="text"
              class="form-control form-control-sm"
              placeholder="例如：09:00-18:00"
            />
          </div>
          <div class="mb-2">
            <textarea
              v-model="item.content"
              class="form-control form-control-sm"
              rows="3"
              placeholder="详细的行程安排..."
            ></textarea>
          </div>
          <div>
            <input
              v-model="item.highlight"
              type="text"
              class="form-control form-control-sm"
              placeholder="例如：🏖️ 海滩美景"
            />
          </div>
        </div>
        <p v-if="content.itinerary.length === 0" class="text-muted text-center py-3 mb-0">
          暂无行程，点击上方"添加一天"按钮开始规划
        </p>
      </div>
    </div>
    
    <!-- 预算参考 -->
    <div v-if="isModuleEnabled('budget')" class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">💰 预算参考</h5>
        <button class="btn btn-sm btn-light" @click="addBudgetItem">
          ➕ 添加
        </button>
      </div>
      <div class="card-body">
        <div v-for="(item, index) in content.budget.items" :key="index" class="row mb-3">
          <div class="col-md-4">
            <input
              v-model="item.name"
              type="text"
              class="form-control form-control-sm"
              placeholder="项目名称"
            />
          </div>
          <div class="col-md-3">
            <input
              v-model.number="item.amount"
              type="number"
              class="form-control form-control-sm"
              placeholder="金额"
            />
          </div>
          <div class="col-md-4">
            <input
              v-model="item.note"
              type="text"
              class="form-control form-control-sm"
              placeholder="备注"
            />
          </div>
          <div class="col-md-1">
            <button class="btn btn-sm btn-outline-danger w-100" @click="removeBudgetItem(index)" title="删除">
              🗑️
            </button>
          </div>
        </div>
        <div v-if="content.budget.items.length > 0" class="alert alert-info mt-3">
          <strong>总计：</strong>¥{{ budgetTotal }}
        </div>
      </div>
    </div>
    
    <!-- 实用提示 -->
    <div v-if="isModuleEnabled('tips')" class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">💡 实用提示</h5>
        <button class="btn btn-sm btn-light" @click="addTip">
          ➕ 添加
        </button>
      </div>
      <div class="card-body">
        <div v-for="(tip, index) in content.tips" :key="index" class="mb-3">
          <div class="input-group">
            <textarea
              v-model="content.tips[index]"
              class="form-control"
              rows="2"
              placeholder="输入一条实用提示..."
            ></textarea>
            <button class="btn btn-outline-danger" @click="removeTip(index)" title="删除">
              🗑️
            </button>
          </div>
        </div>
        <p v-if="content.tips.length === 0" class="text-muted text-center py-3 mb-0">
          暂无提示，点击上方"添加"按钮
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'ContentEditor',
  
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    enabledModules: {
      type: Array,
      default: () => []
    }
  },
  
  emits: ['update:modelValue'],
  
  setup(props, { emit }) {
    const content = computed({
      get: () => props.modelValue,
      set: (val) => emit('update:modelValue', val)
    })
    
    const isModuleEnabled = (moduleId) => {
      return props.enabledModules.includes(moduleId)
    }
    
    const budgetTotal = computed(() => {
      return content.value.budget.items.reduce((sum, item) => sum + (item.amount || 0), 0)
    })
    
    // 亮点管理
    const addHighlight = () => {
      content.value.highlights.push('')
    }
    
    const removeHighlight = (index) => {
      content.value.highlights.splice(index, 1)
    }
    
    // 行程管理
    const addItinerary = () => {
      content.value.itinerary.push({
        day: '',
        time: '',
        content: '',
        highlight: ''
      })
    }
    
    const removeItinerary = (index) => {
      content.value.itinerary.splice(index, 1)
    }
    
    // 预算管理
    const addBudgetItem = () => {
      content.value.budget.items.push({
        name: '',
        amount: 0,
        note: ''
      })
    }
    
    const removeBudgetItem = (index) => {
      content.value.budget.items.splice(index, 1)
    }
    
    // 提示管理
    const addTip = () => {
      content.value.tips.push('')
    }
    
    const removeTip = (index) => {
      content.value.tips.splice(index, 1)
    }
    
    return {
      content,
      isModuleEnabled,
      budgetTotal,
      addHighlight,
      removeHighlight,
      addItinerary,
      removeItinerary,
      addBudgetItem,
      removeBudgetItem,
      addTip,
      removeTip
    }
  }
}
</script>

<style scoped>
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

.itinerary-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  background: #f8f9fa;
}
</style>

