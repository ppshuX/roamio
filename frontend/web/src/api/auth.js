/**
 * 认证相关API
 */
import request from './request'

/**
 * 用户注册
 * @param {Object} data - {username, password, password2, email}
 */
export const register = (data) => {
    return request.post('/auth/register/', data)
}

/**
 * 用户登录
 * @param {Object} data - {username, password}
 */
export const login = (data) => {
    return request.post('/auth/login/', data)
}

/**
 * 用户登出
 */
export const logout = () => {
    const refresh = localStorage.getItem('refresh_token')
    return request.post('/auth/logout/', { refresh })
}

/**
 * 获取当前用户信息
 */
export const getCurrentUser = () => {
    return request.get('/auth/me/')
}

/**
 * 刷新Token
 * @param {string} refresh - refresh token
 */
export const refreshToken = (refresh) => {
    return request.post('/token/refresh/', { refresh })
}

/**
 * 发送邮箱验证码
 * @param {Object} data - {email, type}
 */
export const sendVerificationCode = (data) => {
    return request.post('/auth/send_verification_code/', data)
}

/**
 * 验证邮箱验证码
 * @param {Object} data - {email, code, type}
 */
export const verifyCode = (data) => {
    return request.post('/auth/verify_code/', data)
}

/**
 * 获取QQ登录URL
 */
export const getQQLoginUrl = async () => {
    return request.get('/auth/qq_login_url/')
}

/**
 * QQ登录回调处理
 * @param {Object} data - {code, state}
 */
export const qqCallback = async (data) => {
    return request.post('/auth/qq_callback/', data)
}

/**
 * QQ账号绑定（首次登录）
 * @param {Object} data - {code, state, email, verification_token}
 */
export const qqBind = async (data) => {
    return request.post('/auth/qq_bind/', data)
}

/**
 * QQ账号绑定（已有账号）
 * @param {Object} data - {code, state}
 */
export const qqBindExisting = async (data) => {
    return request.post('/auth/qq_bind_existing/', data)
}

/**
 * 解绑QQ账号
 */
export const qqUnbind = async () => {
    return request.delete('/auth/qq_unbind/')
}

/**
 * 重置密码
 * @param {Object} data - {email, verification_token, new_password, new_password2}
 */
export const resetPassword = (data) => {
    return request.post('/auth/reset_password/', data)
}

