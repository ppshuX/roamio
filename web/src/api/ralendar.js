/**
 * Ralendar 集成 API
 * 用于 Roamio 与 Ralendar 日历系统的数据同步
 */

import request from './index'

/**
 * 将旅行计划添加到 Ralendar 日历
 * @param {string} tripSlug - 旅行计划的 slug
 * @param {Array} events - 事件列表
 * @returns {Promise}
 */
export const addTripToCalendar = (tripSlug, events) => {
    return request.post(`/ralendar/trips/${tripSlug}/add-to-calendar/`, {
        events
    })
}

/**
 * 获取旅行计划关联的日历事件
 * @param {string} tripSlug - 旅行计划的 slug
 * @returns {Promise}
 */
export const getTripCalendarEvents = (tripSlug) => {
    return request.get(`/ralendar/trips/${tripSlug}/calendar-events/`)
}

/**
 * 删除旅行计划关联的所有日历事件
 * @param {string} tripSlug - 旅行计划的 slug
 * @returns {Promise}
 */
export const deleteTripCalendarEvents = (tripSlug) => {
    return request.delete(`/ralendar/trips/${tripSlug}/calendar-events/`)
}

/**
 * 检查 Ralendar 连接状态
 * @returns {Promise}
 */
export const checkRalendarConnection = () => {
    return request.get('/ralendar/status/')
        .catch(() => {
            // 如果请求失败，返回未连接状态
            return { connected: false }
        })
}

/**
 * 获取用户的 Ralendar 设置
 * @returns {Promise}
 */
export const getRalendarSettings = () => {
    return request.get('/ralendar/settings/')
        .catch(() => {
            // 如果请求失败，返回默认设置
            return {
                enabled: false,
                auto_sync: false,
                default_reminder: 'email'
            }
        })
}

/**
 * 更新用户的 Ralendar 设置
 * @param {Object} settings - 设置对象
 * @returns {Promise}
 */
export const updateRalendarSettings = (settings) => {
    return request.put('/ralendar/settings/', settings)
}

