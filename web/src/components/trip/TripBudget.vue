<template>
  <div v-if="budget && budget.items && budget.items.length" class="budget-section">
    <h4>💰 预算参考</h4>
    <div class="table-responsive">
      <table class="budget-table">
        <thead>
          <tr>
            <th>项目</th>
            <th>金额（元）</th>
            <th>备注</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in budget.items" :key="index">
            <td>{{ item.name }}</td>
            <td class="amount">¥{{ item.amount }}</td>
            <td class="note">{{ item.note }}</td>
          </tr>
          <tr class="total-row">
            <td><strong>总计</strong></td>
            <td class="amount"><strong>¥{{ budget.total }}</strong></td>
            <td class="note">人均预算</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TripBudget',

  props: {
    budget: {
      type: Object,
      default: null
    }
  }
})
</script>

<style scoped>
.budget-section {
  margin-bottom: 2rem;
}

h4 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.table-responsive {
  overflow-x: auto;
}

.budget-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.budget-table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.budget-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 1rem;
}

.budget-table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  font-size: 0.95rem;
}

.budget-table tbody tr:hover {
  background: rgba(102, 126, 234, 0.05);
}

.budget-table .amount {
  font-weight: 600;
  color: #667eea;
  text-align: right;
}

.budget-table .note {
  color: #666;
  font-size: 0.9rem;
}

.budget-table .total-row {
  background: rgba(102, 126, 234, 0.1);
  font-weight: 700;
}

.budget-table .total-row td {
  border-bottom: none;
  padding: 1.2rem 1rem;
}

.budget-table .total-row .amount {
  color: #764ba2;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .budget-table th,
  .budget-table td {
    padding: 0.8rem 0.5rem;
    font-size: 0.9rem;
  }

  .budget-table .total-row .amount {
    font-size: 1rem;
  }
}
</style>

