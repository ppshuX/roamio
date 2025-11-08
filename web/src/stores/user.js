/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { login, register, logout, getCurrentUser } from '@/api/auth'
import { getAvatarUrl } from '@/config/api'

export const useUserStore = defineStore('user', {
    state: () => ({
        token: localStorage.getItem('access_token') || '',
        refreshToken: localStorage.getItem('refresh_token') || '',
        userInfo: JSON.parse(localStorage.getItem('user_info') || 'null'),
    }),

    getters: {
        // 是否已登录
        isLoggedIn: (state) => !!state.token,

        // 用户名
        username: (state) => state.userInfo?.username || '',

        // 用户头像
        avatar: (state) => getAvatarUrl(state.userInfo?.profile?.avatar_url),

        // 是否是管理员
        isAdmin: (state) => {
            const isSuperuser = state.userInfo?.is_superuser || false
            const isStaff = state.userInfo?.is_staff || false
            return isSuperuser || isStaff
        },
    },

    actions: {
        // 用户登录
        async login(credentials) {
            try {
                const data = await login(credentials)

                this.token = data.access
                this.refreshToken = data.refresh
                this.userInfo = data.user

                // 保存到localStorage
                localStorage.setItem('access_token', data.access)
                localStorage.setItem('refresh_token', data.refresh)
                localStorage.setItem('user_info', JSON.stringify(data.user))

                return data
            } catch (error) {
                console.error('登录失败:', error)
                if (error.response?.data) {
                    console.error('错误详情:', error.response.data)
                }
                throw error
            }
        },

        // 用户注册
        async register(data) {
            try {
                const result = await register(data)

                this.token = result.access
                this.refreshToken = result.refresh
                this.userInfo = result.user

                // 保存到localStorage
                localStorage.setItem('access_token', result.access)
                localStorage.setItem('refresh_token', result.refresh)
                localStorage.setItem('user_info', JSON.stringify(result.user))

                return result
            } catch (error) {
                console.error('注册失败:', error)
                throw error
            }
        },

        // 用户登出
        async logout() {
            try {
                await logout()
            } catch (error) {
                console.error('登出失败:', error)
            } finally {
                // 清除状态
                this.token = ''
                this.refreshToken = ''
                this.userInfo = null

                // 清除localStorage
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                localStorage.removeItem('user_info')
            }
        },

        // 获取用户信息
        async fetchUserInfo() {
            if (!this.token) return

            try {
                const userInfo = await getCurrentUser()
                this.userInfo = userInfo
                localStorage.setItem('user_info', JSON.stringify(userInfo))
                return userInfo
            } catch (error) {
                console.error('获取用户信息失败:', error)
                // 如果获取失败，清除登录状态
                this.logout()
                throw error
            }
        },
    }
})

