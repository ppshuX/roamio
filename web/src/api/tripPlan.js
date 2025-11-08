/**
 * 旅行计划API
 * 用于编辑器的CRUD操作
 */
import request from './request'

/**
 * 获取我的旅行列表
 */
export const getMyTrips = (params) => {
    return request.get('/trip-plans/my_trips/', { params })
}

/**
 * 获取旅行计划详情
 * @param {string} slug - 旅行标识符
 */
export const getTripPlan = (slug) => {
    return request.get(`/trip-plans/${slug}/`)
}

/**
 * 创建旅行计划
 * @param {object} data - 旅行数据
 */
export const createTripPlan = (data) => {
    return request.post('/trip-plans/', data)
}

/**
 * 更新旅行计划
 * @param {string} slug - 旅行标识符
 * @param {object} data - 更新的数据
 */
export const updateTripPlan = (slug, data) => {
    return request.patch(`/trip-plans/${slug}/`, data)
}

/**
 * 删除旅行计划
 * @param {string} slug - 旅行标识符
 */
export const deleteTripPlan = (slug) => {
    return request.delete(`/trip-plans/${slug}/`)
}

/**
 * 复制旅行计划
 * @param {string} slug - 源旅行标识符
 */
export const cloneTripPlan = (slug) => {
    return request.post(`/trip-plans/${slug}/clone/`)
}

/**
 * 发布旅行计划
 * @param {string} slug - 旅行标识符
 */
export const publishTripPlan = (slug) => {
    return updateTripPlan(slug, { status: 'published' })
}

/**
 * 设置旅行为公开
 * @param {string} slug - 旅行标识符
 */
export const makePublic = (slug) => {
    return updateTripPlan(slug, { visibility: 'public' })
}

/**
 * 设置旅行为私有
 * @param {string} slug - 旅行标识符
 */
export const makePrivate = (slug) => {
    return updateTripPlan(slug, { visibility: 'private' })
}

/**
 * 将旅行计划添加到旅行树
 * @param {string} slug - 旅行标识符
 */
export const addTripToTree = (slug) => {
    return request.post(`/trip-plans/${slug}/add_to_tree/`)
}

/**
 * 从旅行树移除旅行计划
 * @param {string} slug - 旅行标识符
 */
export const removeTripFromTree = (slug) => {
    return request.post(`/trip-plans/${slug}/remove_from_tree/`)
}

