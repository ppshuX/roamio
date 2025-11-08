/**
 * 事件 API
 * 
 * 提供旅行事件的 CRUD 操作
 */

import request from './request'

/**
 * 获取事件列表
 * @param {Number} tripId - 旅行 ID
 * @returns {Promise} API 响应
 */
export const getEvents = (tripId) => {
  return request.get(`/trip-plans/${tripId}/events/`)
}

/**
 * 获取事件详情
 * @param {Number} tripId - 旅行 ID
 * @param {Number} eventId - 事件 ID
 * @returns {Promise} API 响应
 */
export const getEvent = (tripId, eventId) => {
  return request.get(`/trip-plans/${tripId}/events/${eventId}/`)
}

/**
 * 创建事件
 * @param {Number} tripId - 旅行 ID
 * @param {Object} data - 事件数据
 * @param {String} data.title - 事件标题（必填）
 * @param {String} data.description - 事件描述（选填）
 * @param {String} data.eventTime - 事件时间（选填）
 * @param {Object} data.location - 地点信息（选填）
 * @param {Object} data.reminder - 提醒信息（选填）
 * @returns {Promise} API 响应
 */
export const createEvent = (tripId, data) => {
  return request.post(`/trip-plans/${tripId}/events/`, data)
}

/**
 * 更新事件
 * @param {Number} tripId - 旅行 ID
 * @param {Number} eventId - 事件 ID
 * @param {Object} data - 要更新的数据
 * @returns {Promise} API 响应
 */
export const updateEvent = (tripId, eventId, data) => {
  return request.put(`/trip-plans/${tripId}/events/${eventId}/`, data)
}

/**
 * 删除事件
 * @param {Number} tripId - 旅行 ID
 * @param {Number} eventId - 事件 ID
 * @returns {Promise} API 响应
 */
export const deleteEvent = (tripId, eventId) => {
  return request.delete(`/trip-plans/${tripId}/events/${eventId}/`)
}

/**
 * 批量导入本地事项
 * @param {Number} tripId - 旅行 ID
 * @param {Array} events - 事项数组
 * @returns {Promise} API 响应
 */
export const batchCreateFromLocal = (tripId, events) => {
  return request.post(`/trip-plans/${tripId}/events/batch_create_from_local/`, {
    events
  })
}

/**
 * 同步到 Ralendar
 * @param {Number} tripId - 旅行 ID
 * @param {Number} eventId - 事件 ID
 * @returns {Promise} API 响应
 */
export const syncToRalendar = (tripId, eventId) => {
  return request.post(`/trip-plans/${tripId}/events/${eventId}/sync_to_ralendar/`)
}

/**
 * 切换完成状态
 * @param {Number} tripId - 旅行 ID
 * @param {Number} eventId - 事件 ID
 * @returns {Promise} API 响应
 */
export const toggleComplete = (tripId, eventId) => {
  return request.post(`/trip-plans/${tripId}/events/${eventId}/toggle_complete/`)
}


