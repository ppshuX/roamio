import { ref, unref } from 'vue'
import {
  createRalendarEvent,
  deleteRalendarEvent,
  getRalendarEvents,
  updateRalendarEvent
} from '@/api/ralendar'

const RALENDAR_EVENTS_CACHE_KEY = 'ralendar_events'

const saveRalendarEventsCache = (events) => {
  localStorage.setItem(RALENDAR_EVENTS_CACHE_KEY, JSON.stringify(events))
}

const restoreRalendarEventsCache = () => {
  try {
    const stored = localStorage.getItem(RALENDAR_EVENTS_CACHE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (e) {
    return []
  }
}

export function useRalendarEvents({ isLoggedIn, hasRalendarAccount }) {
  const loading = ref(false)
  const allEvents = ref([])

  const loadAllEvents = async () => {
    if (!unref(isLoggedIn) || !unref(hasRalendarAccount)) return

    loading.value = true
    try {
      const data = await getRalendarEvents()
      allEvents.value = data.results || data || []

      saveRalendarEventsCache(allEvents.value)
    } catch (error) {
      const errorData = error.response?.data
      const errorMessage = errorData?.detail || errorData?.error || error.message || '加载失败'

      console.error('加载待办失败:', {
        code: errorData?.code,
        message: errorMessage,
        status: error.response?.status,
        fullError: errorData
      })

      if (errorData?.code === 'NO_RALENDAR_ACCOUNT') {
        console.error('❌ 尚未绑定 Ralendar 账号，请先在个人中心绑定')
      } else if (errorData?.code === 'NO_USER_IDENTIFIER') {
        console.error('❌ 无法识别用户身份，请确保已通过 QQ 登录')
      } else if (errorData?.code === 'TOKEN_EXPIRED') {
        console.error('❌ Ralendar Token 已过期，请重新授权')
      } else {
        console.error('❌ 错误:', errorMessage)
      }

      allEvents.value = restoreRalendarEventsCache()
    } finally {
      loading.value = false
    }
  }

  const formatTime = (timeStr) => {
    if (!timeStr) return ''
    const date = new Date(timeStr)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  }

  const createEvent = async (eventData) => {
    const result = await createRalendarEvent(eventData)
    allEvents.value.unshift(result)
    saveRalendarEventsCache(allEvents.value)
    return result
  }

  const updateEvent = async (eventId, eventData) => {
    const result = await updateRalendarEvent(eventId, eventData)
    const index = allEvents.value.findIndex((event) => event.id === eventId)
    if (index > -1) {
      allEvents.value[index] = result
    }
    saveRalendarEventsCache(allEvents.value)
    return result
  }

  const deleteEvent = async (event) => {
    await deleteRalendarEvent(event.id)

    const index = allEvents.value.findIndex((item) => item.id === event.id)
    if (index > -1) {
      allEvents.value.splice(index, 1)
    }

    saveRalendarEventsCache(allEvents.value)
  }

  return {
    loading,
    allEvents,
    loadAllEvents,
    formatTime,
    createEvent,
    updateEvent,
    deleteEvent
  }
}
