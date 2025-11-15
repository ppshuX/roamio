/**
 * Ralendar OAuth API
 * 处理 Ralendar 账号的 OAuth 授权
 */
import request from './request'

/**
 * 获取 Ralendar OAuth 授权 URL
 * @returns {Promise} 授权 URL 和 state
 */
export function getRalendarAuthorizeUrl() {
  return request({
    url: '/api/v1/ralendar-oauth/authorize-url/',
    method: 'get'
  })
}

/**
 * 处理 Ralendar OAuth 回调
 * @param {string} code - 授权码
 * @param {string} state - 状态参数
 * @returns {Promise} 绑定结果
 */
export function handleRalendarCallback(code, state) {
  return request({
    url: '/api/v1/ralendar-oauth/callback/',
    method: 'post',
    data: {
      code,
      state
    }
  })
}

/**
 * 获取用户的所有 Ralendar 账号
 * @returns {Promise} 账号列表
 */
export function getRalendarAccounts() {
  return request({
    url: '/api/v1/ralendar-oauth/accounts/',
    method: 'get'
  })
}

/**
 * 设置默认 Ralendar 账号
 * @param {number} accountId - 账号 ID
 * @returns {Promise}
 */
export function setDefaultRalendarAccount(accountId) {
  return request({
    url: `/api/v1/ralendar-oauth/${accountId}/set-default/`,
    method: 'post'
  })
}

/**
 * 解绑 Ralendar 账号
 * @param {number} accountId - 账号 ID
 * @returns {Promise}
 */
export function unbindRalendarAccount(accountId) {
  return request({
    url: `/api/v1/ralendar-oauth/${accountId}/unbind/`,
    method: 'delete'
  })
}

