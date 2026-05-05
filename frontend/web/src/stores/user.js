/**
 * 用户状态管理（Vue 3 setup store 风格）
 */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { login as loginApi, register as registerApi, logout as logoutApi, getCurrentUser } from '@/api/auth'
import { getAvatarUrl } from '@/config/api'

export const useUserStore = defineStore('user', () => {
  const ACCESS_TOKEN_KEY = 'roamio_access_token'
  const accessToken = ref(sessionStorage.getItem(ACCESS_TOKEN_KEY) || '')
  // 仅为兼容旧代码保留；refresh token 已迁移到 HttpOnly Cookie
  const refreshToken = ref('')
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))

  // 兼容旧字段名 userStore.token
  const token = computed({
    get: () => accessToken.value,
    set: (value) => {
      accessToken.value = value || ''
    }
  })

  const isLoggedIn = computed(() => !!accessToken.value)
  const username = computed(() => userInfo.value?.username || '')
  const avatar = computed(() => getAvatarUrl(userInfo.value?.profile?.avatar_url))
  const isAdmin = computed(() => {
    const isSuperuser = userInfo.value?.is_superuser || false
    const isStaff = userInfo.value?.is_staff || false
    return isSuperuser || isStaff
  })

  function setAccessToken(nextToken) {
    const normalized = nextToken || ''
    accessToken.value = normalized
    if (normalized) {
      sessionStorage.setItem(ACCESS_TOKEN_KEY, normalized)
    } else {
      sessionStorage.removeItem(ACCESS_TOKEN_KEY)
    }
  }

  function clearAuthState() {
    setAccessToken('')
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('user_info')
  }

  function migrateLegacyTokens() {
    const legacyAccessToken = localStorage.getItem('access_token')
    if (legacyAccessToken && !accessToken.value) {
      accessToken.value = legacyAccessToken
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function restoreAccessToken() {
    if (accessToken.value) {
      return accessToken.value
    }

    migrateLegacyTokens()
    if (accessToken.value) {
      return accessToken.value
    }

    try {
      const { refreshAccessToken } = await import('@/api/api')
      const nextToken = await refreshAccessToken()
      return nextToken || ''
    } catch (error) {
      clearAuthState()
      return ''
    }
  }

  async function login(credentials) {
    try {
      const data = await loginApi(credentials)
      setAccessToken(data.access)
      userInfo.value = data.user
      localStorage.setItem('user_info', JSON.stringify(data.user))
      return data
    } catch (error) {
      console.error('登录失败:', error)
      if (error.response?.data) {
        console.error('错误详情:', error.response.data)
      }
      throw error
    }
  }

  async function register(data) {
    try {
      const result = await registerApi(data)
      setAccessToken(result.access)
      userInfo.value = result.user
      localStorage.setItem('user_info', JSON.stringify(result.user))
      return result
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  }

  async function logout() {
    try {
      await logoutApi()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      clearAuthState()
    }
  }

  // 刷新失败等场景：只清浏览器内状态，不额外请求后端
  function logoutLocal() {
    clearAuthState()
  }

  async function fetchUserInfo() {
    if (!accessToken.value) return null
    try {
      const info = await getCurrentUser()
      userInfo.value = info
      localStorage.setItem('user_info', JSON.stringify(info))
      return info
    } catch (error) {
      console.error('获取用户信息失败:', error)
      const status = error?.response?.status
      // 只有明确鉴权失败时才清理登录态，避免网络抖动/临时 5xx 导致“刷新即掉线”。
      if (status === 401 || status === 403) {
        logoutLocal()
      }
      throw error
    }
  }

  return {
    accessToken,
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    username,
    avatar,
    isAdmin,
    setAccessToken,
    clearAuthState,
    migrateLegacyTokens,
    restoreAccessToken,
    login,
    register,
    logout,
    logoutLocal,
    fetchUserInfo
  }
})

