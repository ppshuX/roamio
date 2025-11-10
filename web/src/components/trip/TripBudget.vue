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
  margin-bottom: 1.5rem;
}

h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.table-responsive {
  overflow-x: auto;
}

.budget-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border: 2px solid #4caf50;
  border-radius: 8px;
  overflow: hidden;
}

.budget-table thead {
  background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
  color: white;
}

.budget-table th {
  padding: 0.7rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
}

.budget-table td {
  padding: 0.7rem;
  border-bottom: 1px solid #e0e0e0;
  font-size: 0.85rem;
}

.budget-table .amount {
  font-weight: 600;
  color: #4caf50;
  text-align: right;
}

.budget-table .note {
  color: #666;
  font-size: 0.8rem;
}

.budget-table .total-row {
  background: #e8f5e9;
  font-weight: 700;
}

.budget-table .total-row td {
  border-bottom: none;
  padding: 0.8rem 0.7rem;
}

.budget-table .total-row .amount {
  color: #2e7d32;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .budget-table th,
  .budget-table td {
    padding: 0.6rem 0.4rem;
    font-size: 0.8rem;
  }
}
</style>

