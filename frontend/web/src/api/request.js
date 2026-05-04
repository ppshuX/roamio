/**
 * 基于fetch的Ajax请求封装
 * 支持文件上传进度回调（使用 XMLHttpRequest）
 */
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// 默认超时时间（毫秒）
const DEFAULT_TIMEOUT = 300000 // 5 分钟（支持大文件上传）

// 创建request函数，模拟axios接口
const request = {
    // GET请求
    async get(url, config = {}) {
        // 处理query参数
        const { params, ...options } = config
        let finalUrl = url
        if (params && Object.keys(params).length > 0) {
            const queryString = new URLSearchParams(params).toString()
            finalUrl = `${url}?${queryString}`
        }
        return this.request(finalUrl, {
            method: 'GET',
            ...options
        })
    },

    // POST请求（支持上传进度）
    async post(url, data, config = {}) {
        // 如果有进度回调且是 FormData，使用 XMLHttpRequest
        if (config.onUploadProgress && data instanceof FormData) {
            return this.uploadWithProgress(url, data, 'POST', config)
        }
        
        return this.request(url, {
            method: 'POST',
            body: data instanceof FormData ? data : JSON.stringify(data),
            ...config
        })
    },

    // PUT请求
    async put(url, data, config = {}) {
        return this.request(url, {
            method: 'PUT',
            body: data instanceof FormData ? data : JSON.stringify(data),
            ...config
        })
    },

    // PATCH请求
    async patch(url, data, config = {}) {
        return this.request(url, {
            method: 'PATCH',
            body: data instanceof FormData ? data : JSON.stringify(data),
            ...config
        })
    },

    // DELETE请求
    async delete(url, config = {}) {
        return this.request(url, {
            method: 'DELETE',
            ...config
        })
    },

    // 使用 XMLHttpRequest 上传文件（支持进度）
    uploadWithProgress(url, formData, method = 'POST', config = {}) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest()
            const fullUrl = url.startsWith('http') ? url : `${baseURL}${url}`
            
            // 打开请求
            xhr.open(method, fullUrl)
            
            // 设置超时（5 分钟）
            xhr.timeout = config.timeout || DEFAULT_TIMEOUT
            
            // 设置请求头
            const token = localStorage.getItem('access_token')
            if (token) {
                xhr.setRequestHeader('Authorization', `Bearer ${token}`)
            }
            
            // 上传进度
            if (xhr.upload && config.onUploadProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = Math.round((e.loaded / e.total) * 100)
                        config.onUploadProgress({ loaded: e.loaded, total: e.total, percent: percentComplete })
                    }
                })
            }
            
            // 请求完成
            xhr.onload = function() {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const data = JSON.parse(xhr.responseText)
                        resolve(data)
                    } catch (e) {
                        resolve(xhr.responseText)
                    }
                } else {
                    try {
                        const errorData = JSON.parse(xhr.responseText)
                        const error = new Error(errorData.detail || errorData.message || `Request failed with status ${xhr.status}`)
                        error.response = { data: errorData }
                        error.status = xhr.status
                        reject(error)
                    } catch (e) {
                        const error = new Error(`Request failed with status ${xhr.status}`)
                        error.status = xhr.status
                        reject(error)
                    }
                }
            }
            
            // 请求错误
            xhr.onerror = function() {
                reject(new Error('Network error'))
            }
            
            // 超时
            xhr.ontimeout = function() {
                reject(new Error('上传超时，请检查网络或文件大小'))
            }
            
            // 发送请求
            xhr.send(formData)
        })
    },

    // 通用请求方法
    async request(url, options = {}) {
        // 构建完整URL
        const fullUrl = url.startsWith('http') ? url : `${baseURL}${url}`

        // 构建headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        }

        // 从localStorage获取token
        const token = localStorage.getItem('access_token')
        if (token) {
            headers.Authorization = `Bearer ${token}`
        }

        // 处理FormData，移除Content-Type让浏览器自动设置
        if (options.body instanceof FormData) {
            delete headers['Content-Type']
        }

        // 构建请求选项
        const fetchOptions = {
            ...options,
            headers,
            credentials: 'same-origin'
        }

        // 发送请求
        const response = await fetch(fullUrl, fetchOptions)

        // 检查响应状态
        if (!response.ok) {
            const error = new Error(`Request failed with status ${response.status}`)
            error.response = response
            error.status = response.status
            error.statusText = response.statusText

            try {
                const errorData = await response.json()
                console.log('[API Error]', url, errorData)
                error.message = errorData.detail || errorData.message || error.message
                error.response.data = errorData
            } catch (e) {
                console.log('[API Error]', url, 'Failed to parse error response')
                error.message = response.statusText || error.message
            }

            // 处理401未授权
            if (response.status === 401) {
                // 清掉本地失效令牌（避免公共页携带坏token导致跳转）
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                localStorage.removeItem('user_info')

                // 仅在需要登录的路由上跳转登录，其余公共页不跳转
                const path = window.location.pathname || ''
                const needAuth = path.startsWith('/user') || path.startsWith('/editor') || path.startsWith('/my-trips')
                if (needAuth && path !== '/login/' && path !== '/login') {
                    window.location.href = '/login/'
                }
            }

            throw error
        }

        // 检查响应是否有内容（204 No Content没有响应体）
        if (response.status === 204 || response.headers.get('content-length') === '0') {
            return null
        }

        // 解析响应数据
        const data = await response.json()
        return data
    }
}

export default request
