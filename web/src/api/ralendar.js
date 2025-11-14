/**
 * Ralendar 集成 API
 * 用于 Roamio 与 Ralendar 日历系统的数据同步
 */
import request from './request'

/**
 * 将 AI 生成的行程同步到 Ralendar 日历
 * @param {string} tripSlug - 旅行计划的 slug
 * @param {Array} events - 事件数组
 * @returns {Promise} API 响应
 */
export const syncTripToCalendar = (tripSlug, events) => {
  return request.post(`/ralendar/trips/${tripSlug}/sync-ai-trip/`, {
    events
  })
}

/**
 * 获取用户的 Ralendar 事件列表
 * @param {Object} params - 查询参数
 * @returns {Promise} API 响应
 */
export const getRalendarEvents = (params = {}) => {
  return request.get('/ralendar/trips/events/', { params })
}

/**
 * 创建单个事件到 Ralendar
 * @param {Object} eventData - 事件数据
 * @returns {Promise} API 响应
 */
export const createRalendarEvent = (eventData) => {
  return request.post('/ralendar/trips/events/create/', eventData)
}

