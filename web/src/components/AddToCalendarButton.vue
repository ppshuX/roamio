<template>
  <div class="add-to-calendar">
    <!-- 添加到日历按钮 -->
    <button
      v-if="!loading && !synced"
      class="btn btn-outline-primary"
      @click="handleAddToCalendar"
      :disabled="processing"
    >
      <span v-if="processing" class="spinner-border spinner-border-sm me-2"></span>
      <i v-else class="bi bi-calendar-plus me-2"></i>
      添加到 Ralendar
    </button>

    <!-- 已同步状态 -->
    <div v-if="synced" class="synced-status">
      <button class="btn btn-success" disabled>
        <i class="bi bi-check-circle me-2"></i>
        已同步到日历
      </button>
      <button
        class="btn btn-outline-danger btn-sm ms-2"
        @click="handleRemoveFromCalendar"
        :disabled="processing"
      >
        <i class="bi bi-trash me-1"></i>
        移除
      </button>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="text-muted">
      <span class="spinner-border spinner-border-sm me-2"></span>
      检查同步状态...
    </div>
  </div>
</template>

<script>
import { ref, onMounted, defineComponent } from 'vue'
import { addTripToCalendar, getTripCalendarEvents, deleteTripCalendarEvents } from '@/api/ralendar'
import { ElMessage, ElMessageBox } from 'element-plus'

export default defineComponent({
  name: 'AddToCalendarButton',

  props: {
    tripSlug: {
      type: String,
      required: true
    },
    tripTitle: {
      type: String,
      required: true
    },
    events: {
      type: Array,
      default: () => []
    }
  },

  setup(props) {
    const loading = ref(false)
    const processing = ref(false)
    const synced = ref(false)

    // 检查是否已同步
    const checkSyncStatus = async () => {
      loading.value = true
      try {
        const response = await getTripCalendarEvents(props.tripSlug)
        synced.value = response.events && response.events.length > 0
      } catch (error) {
        console.error('检查同步状态失败:', error)
        synced.value = false
      } finally {
        loading.value = false
      }
    }

    // 添加到日历
    const handleAddToCalendar = async () => {
      if (!props.events || props.events.length === 0) {
        ElMessage.warning('当前旅行计划没有事件，请先添加行程安排')
        return
      }

      // 确认对话框
      const confirmed = await ElMessageBox.confirm(
        `确定要将「${props.tripTitle}」的 ${props.events.length} 个行程添加到 Ralendar 日历吗？`,
        '添加到日历',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      ).catch(() => false)

      if (!confirmed) return

      processing.value = true

      try {
        // 转换事件格式
        const formattedEvents = props.events.map(event => ({
          title: event.title,
          description: event.description || '',
          start_time: event.event_time,
          end_time: event.event_time, // 如果没有结束时间，使用开始时间
          location: event.location?.name || '',
          latitude: event.location?.lat,
          longitude: event.location?.lng,
          email_reminder: event.reminder?.enabled || false
        }))

        const response = await addTripToCalendar(props.tripSlug, formattedEvents)

        if (response.success) {
          ElMessage.success(`成功添加 ${response.created_count} 个事件到日历`)
          synced.value = true
        } else {
          ElMessage.error('添加到日历失败')
        }
      } catch (error) {
        console.error('添加到日历失败:', error)
        ElMessage.error(error.response?.data?.error || '添加到日历失败，请稍后重试')
      } finally {
        processing.value = false
      }
    }

    // 从日历移除
    const handleRemoveFromCalendar = async () => {
      const confirmed = await ElMessageBox.confirm(
        `确定要从 Ralendar 日历中移除「${props.tripTitle}」的所有事件吗？`,
        '移除事件',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).catch(() => false)

      if (!confirmed) return

      processing.value = true

      try {
        const response = await deleteTripCalendarEvents(props.tripSlug)

        if (response.success) {
          ElMessage.success(`已移除 ${response.deleted_count} 个事件`)
          synced.value = false
        } else {
          ElMessage.error('移除失败')
        }
      } catch (error) {
        console.error('移除事件失败:', error)
        ElMessage.error(error.response?.data?.error || '移除失败，请稍后重试')
      } finally {
        processing.value = false
      }
    }

    onMounted(() => {
      checkSyncStatus()
    })

    return {
      loading,
      processing,
      synced,
      handleAddToCalendar,
      handleRemoveFromCalendar
    }
  }
})
</script>

<style scoped>
.add-to-calendar {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.synced-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn {
  transition: all 0.3s ease;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>

