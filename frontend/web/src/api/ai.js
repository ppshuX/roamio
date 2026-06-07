/**
 * AI 旅行规划 API
 */

import request from './request'

export const AI_GENERATION_TIMEOUT_MS = 60000

/**
 * 生成旅行计划
 * @param {Object} data - 请求数据
 * @param {string} data.prompt - 用户描述
 * @param {Object} data.preferences - 偏好设置
 * @returns {Promise}
 */
export function generateTripPlan(data, config = {}) {
  return request.post('/ai/generate-trip/', data, {
    timeout: AI_GENERATION_TIMEOUT_MS,
    ...config
  })
}

/**
 * 优化旅行计划
 * @param {Object} data - 请求数据
 * @param {Object} data.trip_plan - 现有行程
 * @param {string} data.feedback - 用户反馈
 * @returns {Promise}
 */
export function refineTripPlan(data) {
  return request.post('/ai/refine-trip/', data)
}

/**
 * 获取使用统计
 * @returns {Promise}
 */
export function getUsageStats() {
  return request.get('/ai/usage-stats/')
}

