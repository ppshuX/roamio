import { ref, unref } from 'vue'
import { getRalendarAccounts, getRalendarAuthorizeUrl } from '@/api/ralendarOAuth'

export function useRalendarAccount({ isLoggedIn }) {
  const hasRalendarAccount = ref(false)
  const checkingAccount = ref(false)
  const connecting = ref(false)

  const checkRalendarAccount = async ({ onAccountReady } = {}) => {
    if (!unref(isLoggedIn)) return

    checkingAccount.value = true
    try {
      const response = await getRalendarAccounts()
      hasRalendarAccount.value = (response.accounts || []).length > 0

      if (hasRalendarAccount.value && onAccountReady) {
        await onAccountReady()
      }
    } catch (err) {
      console.error('检查 Ralendar 账号失败:', err)
      hasRalendarAccount.value = false
    } finally {
      checkingAccount.value = false
    }
  }

  const handleConnectRalendar = async () => {
    connecting.value = true
    try {
      const response = await getRalendarAuthorizeUrl()
      const { authorize_url } = response

      if (authorize_url) {
        sessionStorage.setItem('ralendar_auth_origin', window.location.pathname)
        sessionStorage.setItem('ralendar_auth_from', 'sidebar')

        window.location.href = authorize_url
      } else {
        alert('获取授权链接失败')
      }
    } catch (err) {
      console.error('连接 Ralendar 失败:', err)
      alert(err.response?.data?.error || '连接失败，请重试')
    } finally {
      connecting.value = false
    }
  }

  return {
    hasRalendarAccount,
    checkingAccount,
    connecting,
    checkRalendarAccount,
    handleConnectRalendar
  }
}
