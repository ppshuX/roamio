import api, { refreshAccessToken } from './api'
import pinia from '@/stores'
import { useUserStore } from '@/stores/user'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const buildStreamUrl = (url) => {
  if (url.startsWith('http')) {
    return url
  }
  return `${baseURL}${url}`
}

const buildHeaders = (customHeaders = {}) => {
  const userStore = useUserStore(pinia)
  const headers = {
    ...customHeaders
  }

  if (userStore.accessToken) {
    headers.Authorization = `Bearer ${userStore.accessToken}`
  }

  return headers
}

const parseBody = (body) => {
  if (!body) return undefined
  if (body instanceof FormData) return body
  if (typeof body === 'string') return body
  return JSON.stringify(body)
}

const streamFetch = async (url, options = {}, retry = true) => {
  const response = await fetch(buildStreamUrl(url), {
    method: options.method || 'GET',
    headers: buildHeaders(options.headers),
    body: parseBody(options.body),
    credentials: 'include',
    signal: options.signal
  })

  if (response.status === 401 && retry) {
    await refreshAccessToken()
    return streamFetch(url, options, false)
  }

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.error || errorMessage
    } catch (e) {
      // ignore parse failure
    }
    throw new Error(errorMessage)
  }

  return response
}

const readTextStream = async (response, onChunk) => {
  if (!response.body) {
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')

  let done = false
  while (!done) {
    const result = await reader.read()
    done = result.done
    if (done) break
    const chunk = decoder.decode(result.value, { stream: true })
    if (onChunk) {
      onChunk(chunk)
    }
  }
}

const streamApi = {
  async request(url, options = {}) {
    return streamFetch(url, options)
  },

  async text(url, options = {}) {
    const response = await streamFetch(url, options)
    return response.text()
  },

  async consume(url, options = {}) {
    const response = await streamFetch(url, options)
    await readTextStream(response, options.onChunk)
    return response
  },

  // 需要上传进度时仍建议走 axios api
  api
}

export default streamApi
