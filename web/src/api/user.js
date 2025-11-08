/**
 * 用户相关API
 */
import request from './request'

/**
 * 获取用户信息
 * @param {number} userId - 用户ID
 */
export const getUser = (userId) => {
    return request.get(`/users/${userId}/`)
}

/**
 * 更新用户信息
 * @param {number} userId - 用户ID
 * @param {Object} data - 用户数据
 */
export const updateUser = (userId, data) => {
    return request.patch(`/users/${userId}/`, data)
}

/**
 * 上传头像
 * @param {number} userId - 用户ID
 * @param {File} avatar - 头像文件
 */
export const uploadAvatar = (userId, avatar) => {
    const formData = new FormData()
    formData.append('avatar', avatar)
    return request.post(`/users/${userId}/upload_avatar/`, formData)
}

/**
 * 更新个人资料（bio, tags, visited_countries）
 * @param {Object} data - { bio, tags, visited_countries }
 */
export const updateProfile = (data) => {
    return request.patch('/users/update_profile/', data)
}

/**
 * 获取用户统计信息
 * @param {number} userId - 用户ID
 */
export const getUserStats = (userId) => {
    return request.get(`/users/${userId}/stats/`)
}

/**
 * 删除用户账号
 * @param {number} userId - 用户ID
 */
export const deleteUser = (userId) => {
    return request.delete(`/users/${userId}/`)
}

/**
 * 绑定邮箱（需要验证码验证）
 * @param {Object} data - {email, verification_token}
 */
export const bindEmail = (data) => {
    return request.post('/users/bind_email/', data)
}

/**
 * 获取用户公开资料（包含统计信息）
 * @param {number} userId - 用户ID
 */
export const getUserProfile = (userId) => {
    return request.get(`/users/${userId}/profile/`)
}
