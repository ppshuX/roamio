/**
 * request 兼容层：
 * 保留旧调用方式，底层切换为统一 axios api 实例。
 */
import api, { uploadWithProgress } from './api'

const parseBody = (body) => {
  if (!body) return undefined
  if (body instanceof FormData) return body
  if (typeof body === 'string') {
    try {
      return JSON.parse(body)
    } catch (error) {
      return body
    }
  }
  return body
}

const request = {
  get(url, config = {}) {
    return api.get(url, config)
  },

  post(url, data, config = {}) {
    if (config.onUploadProgress && data instanceof FormData) {
      return this.uploadWithProgress(url, data, 'POST', config)
    }
    return api.post(url, data, config)
  },

  put(url, data, config = {}) {
    return api.put(url, data, config)
  },

  patch(url, data, config = {}) {
    return api.patch(url, data, config)
  },

  delete(url, config = {}) {
    return api.delete(url, config)
  },

  uploadWithProgress(url, formData, method = 'POST', config = {}) {
    return uploadWithProgress(url, formData, {
      ...config,
      method
    })
  },

  request(url, options = {}) {
    const method = options.method || 'GET'
    return api.request({
      url,
      method,
      headers: options.headers,
      params: options.params,
      data: parseBody(options.body),
      timeout: options.timeout,
      skipAuthRefresh: options.skipAuthRefresh
    })
  }
}

export default request
