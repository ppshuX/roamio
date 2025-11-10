/**
 * 评论相关API
 */
import request from './request'

/**
 * 获取评论列表
 * @param {Object} params - 查询参数 {page, page_size, user}
 * @param {string} params.page - 旅行页面标识（必需）
 * @param {number} params.page_size - 每页数量
 * @param {number} params.user - 用户ID过滤
 */
export const getCommentList = async (params) => {
    return request.get('/comments/', { params })
}

/**
 * 创建评论
 * @param {Object|FormData} data - 评论数据（普通对象或包含文件的FormData）
 * @param {Function} onUploadProgress - 上传进度回调函数
 */
export const createComment = (data, onUploadProgress) => {
    const config = {
        timeout: 300000 // 5分钟超时
    }
    
    // 只有当 data 是 FormData 时才设置 multipart/form-data
    // 否则让 request 自动设置 application/json
    if (data instanceof FormData) {
        config.headers = {
            'Content-Type': 'multipart/form-data'
        }
        if (onUploadProgress) {
            config.onUploadProgress = onUploadProgress
        }
    }
    
    return request.post('/comments/', data, config)
}

/**
 * 删除评论
 * @param {number} id - 评论ID
 */
export const deleteComment = (id) => {
    return request.delete(`/comments/${id}/`)
}

/**
 * 获取评论详情
 * @param {number} id - 评论ID
 */
export const getCommentDetail = (id) => {
    return request.get(`/comments/${id}/`)
}

/**
 * 为评论添加图片
 * @param {number} id - 评论ID
 * @param {FormData} data - 表单数据（包含图片文件）
 * @param {Function} onUploadProgress - 上传进度回调函数
 */
export const addCommentImage = (id, data, onUploadProgress) => {
    return request.post(`/comments/${id}/add_image/`, data, {
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        timeout: 300000, // 5分钟超时
        onUploadProgress: onUploadProgress
    })
}

/**
 * 更新评论内容
 * @param {number} id - 评论ID
 * @param {Object} data - 评论数据 {content}
 * @param {Function} onUploadProgress - 上传进度回调函数（如果包含文件）
 */
export const updateComment = (id, data, onUploadProgress) => {
    const config = {
        timeout: 300000 // 5分钟超时
    }

    // 如果是 FormData，添加进度回调
    if (data instanceof FormData && onUploadProgress) {
        config.onUploadProgress = onUploadProgress
    }

    return request.patch(`/comments/${id}/`, data, config)
}

/**
 * 获取评论的回复列表
 * @param {number} id - 评论ID
 */
export const getCommentReplies = (id) => {
    return request.get(`/comments/${id}/replies/`)
}

/**
 * 点赞/取消点赞评论
 * @param {number} id - 评论ID
 */
export const likeComment = (id) => {
    return request.post(`/comments/${id}/like/`)
}

