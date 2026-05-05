import axios from 'axios'
import { toValue } from 'vue'
import pinia from '@/stores'
import { useUserStore } from '@/stores/user'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const DEFAULT_TIMEOUT = 300000

const api = axios.create({
  baseURL,
  timeout: DEFAULT_TIMEOUT,
  withCredentials: true
})

const refreshClient = axios.create({
  baseURL,
  timeout: DEFAULT_TIMEOUT,
  withCredentials: true
})

let isRefreshing = false
let refreshQueue = []

const needsAuthRedirect = () => {
  const path = window.location.pathname || ''
  return path.startsWith('/user') || path.startsWith('/editor') || path.startsWith('/my-trips')
}

const redirectToLoginIfNeeded = () => {
  const path = window.location.pathname || ''
  if (needsAuthRedirect() && path !== '/login/' && path !== '/login') {
    window.location.href = '/login/'
  }
}

const resolveRefreshQueue = (error, token = '') => {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  refreshQueue = []
}

export const refreshAccessToken = async () => {
  const userStore = useUserStore(pinia)

  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      refreshQueue.push({ resolve, reject })
    })
  }

  isRefreshing = true

  try {
    // refreshClient 未挂 response.data 解包拦截器，必须用 response.data
    const { data } = await refreshClient.post('/auth/refresh/')
    const nextAccessToken = typeof data?.access === 'string' ? data.access : ''
    if (!nextAccessToken) {
      const err = new Error('Refresh succeeded but missing access token in body')
      err.response = { status: 502, data }
      throw err
    }
    userStore.setAccessToken(nextAccessToken)
    resolveRefreshQueue(null, nextAccessToken)
    return nextAccessToken
  } catch (error) {
    const status = error?.response?.status
    // 超时/断网等非 HTTP 应答：不误清登录态（access 仍可续期或由用户重试）
    if (status === 401 || status === 403) {
      userStore.logoutLocal()
    }
    resolveRefreshQueue(error)
    throw error
  } finally {
    isRefreshing = false
  }
}

api.interceptors.request.use(
  (config) => {
    const userStore = useUserStore(pinia)
    const token = toValue(userStore.accessToken) || ''
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const status = error.response?.status
    const originalRequest = error.config || {}
    const userStore = useUserStore(pinia)

    if (
      status === 401 &&
      !originalRequest._retry &&
      !originalRequest.skipAuthRefresh &&
      !String(originalRequest.url || '').includes('/auth/refresh/')
    ) {
      originalRequest._retry = true

      try {
        const nextToken = await refreshAccessToken()
        if (nextToken) {
          originalRequest.headers = originalRequest.headers || {}
          originalRequest.headers.Authorization = `Bearer ${nextToken}`
        }
        return api(originalRequest)
      } catch (refreshError) {
        const rs = refreshError?.response?.status
        if (rs === 401 || rs === 403) {
          userStore.logoutLocal()
          redirectToLoginIfNeeded()
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export const uploadWithProgress = (url, formData, config = {}) => {
  return api.request({
    url,
    method: config.method || 'POST',
    data: formData,
    headers: {
      ...(config.headers || {}),
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: config.onUploadProgress,
    timeout: config.timeout || DEFAULT_TIMEOUT,
    skipAuthRefresh: config.skipAuthRefresh
  })
}

export default api
