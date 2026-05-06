/**
 * API配置
 * 
 * 前后端分离架构：
 * - 开发环境：通过 Vite dev server 代理访问本地后端（http://localhost:8000）
 * - 生产环境：通过环境变量配置独立 API 域名（https://api.roamio.com）
 * 
 * 环境变量配置：
 * - VITE_API_BASE_URL: API 基础地址
 * - VITE_API_VERSION: API 版本（默认 v1）
 */

// API 版本
export const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1'

// 根据环境获取API基础URL
export const getApiBaseUrl = () => {
    // 开发环境：使用代理，返回空字符串（相对路径）
    if (import.meta.env.DEV) {
        return ''
    }

    // 生产环境：从环境变量读取 API 地址
    // 如果未配置，默认使用当前域名（前后端同域部署）
    return import.meta.env.VITE_API_BASE_URL || ''
}

// 获取完整的 API 前缀（包含版本号）
export const getApiPrefix = () => {
    const baseUrl = getApiBaseUrl()
    return baseUrl ? `${baseUrl}/api/${API_VERSION}` : `/api/${API_VERSION}`
}

// 获取完整URL（处理相对路径）
export const getFullUrl = (path) => {
    if (!path) return null

    // 如果已经是完整URL，直接返回
    if (path.startsWith('http://') || path.startsWith('https://')) {
        return path
    }

    // 获取API基础URL
    const baseUrl = getApiBaseUrl()

    // 如果baseUrl为空，直接返回相对路径（开发环境通过代理，生产环境同域）
    if (!baseUrl) {
        return path
    }

    // 拼接完整URL（生产环境跨域）
    return baseUrl + path
}

// 默认头像（SVG 作为备用方案）
export const DEFAULT_AVATAR_SVG = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"%3E%3Ccircle cx="24" cy="24" r="24" fill="%230f766e"/%3E%3Ccircle cx="24" cy="18" r="8" fill="%23fff"/%3E%3Cpath d="M 8 40 Q 8 28 24 28 Q 40 28 40 40" fill="%23fff"/%3E%3C/svg%3E'

// 获取头像URL
export const getAvatarUrl = (avatarUrl) => {
    // 如果没有头像URL，返回默认SVG头像
    if (!avatarUrl || avatarUrl === '' || avatarUrl === 'null' || avatarUrl === 'undefined') {
        return DEFAULT_AVATAR_SVG
    }
    
    // 如果是完整URL，直接返回
    if (avatarUrl.startsWith('http://') || avatarUrl.startsWith('https://')) {
        return avatarUrl
    }
    
    // 如果是相对路径，返回
    return avatarUrl
}

export default {
    getApiBaseUrl,
    getFullUrl,
    getAvatarUrl
}

