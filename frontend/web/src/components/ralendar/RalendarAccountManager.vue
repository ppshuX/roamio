<template>
  <div class="ralendar-account-manager">
    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>

    <!-- 已绑定账号列表 -->
    <div v-else-if="accounts.length > 0" class="accounts-list">
      <h6 class="mb-3">已绑定的 Ralendar 账号</h6>
      
      <div 
        v-for="account in accounts" 
        :key="account.id"
        class="account-card"
        :class="{ 'default': account.is_default }"
      >
        <div class="account-info">
          <!-- 头像 -->
          <img 
            v-if="account.ralendar_avatar" 
            :src="account.ralendar_avatar" 
            :alt="account.ralendar_username"
            class="account-avatar"
          >
          <div v-else class="account-avatar-placeholder">
            {{ account.ralendar_username.charAt(0) }}
          </div>

          <!-- 账号信息 -->
          <div class="account-details">
            <div class="account-name">
              {{ account.ralendar_username }}
              <span v-if="account.is_default" class="badge bg-primary ms-2">默认</span>
              <span v-if="account.is_token_expired" class="badge bg-warning ms-2">已过期</span>
            </div>
            <div class="account-email text-muted">
              {{ account.ralendar_email || '无邮箱' }}
            </div>
            <div class="account-meta">
              <small class="text-muted">
                绑定时间: {{ formatDate(account.created_at) }}
              </small>
              <small v-if="account.last_synced_at" class="text-muted ms-3">
                最后同步: {{ formatDate(account.last_synced_at) }}
              </small>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="account-actions">
          <button
            v-if="!account.is_default"
            class="btn btn-sm btn-outline-primary"
            @click="setDefault(account.id)"
            :disabled="actionLoading"
          >
            设为默认
          </button>
          <button
            class="btn btn-sm btn-outline-danger"
            @click="unbind(account.id)"
            :disabled="actionLoading"
          >
            解绑
          </button>
        </div>
      </div>

      <!-- 添加更多账号 -->
      <button
        class="btn btn-outline-secondary w-100 mt-3"
        @click="connectRalendar"
        :disabled="actionLoading"
      >
        <i class="bi bi-plus-circle me-2"></i>
        添加其他 Ralendar 账号
      </button>
    </div>

    <!-- 无账号状态 -->
    <div v-else class="no-accounts text-center py-4">
      <i class="bi bi-calendar-x" style="font-size: 3rem; color: #ccc;"></i>
      <p class="mt-3 text-muted">尚未绑定 Ralendar 账号</p>
      <button
        class="btn btn-primary"
        @click="connectRalendar"
        :disabled="actionLoading"
      >
        <i class="bi bi-calendar-plus me-2"></i>
        连接 Ralendar
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { 
  getRalendarAuthorizeUrl,
  getRalendarAccounts, 
  setDefaultRalendarAccount, 
  unbindRalendarAccount 
} from '@/api/ralendarOAuth'

export default {
  name: 'RalendarAccountManager',
  emits: ['connect', 'update'],
  setup(props, { emit }) {
    const accounts = ref([])
    const loading = ref(true)
    const actionLoading = ref(false)
    const error = ref('')

    // 加载账号列表
    const loadAccounts = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await getRalendarAccounts()
        accounts.value = response.accounts || []
      } catch (err) {
        console.error('加载 Ralendar 账号失败:', err)
        error.value = err.response?.data?.error || '加载失败，请重试'
      } finally {
        loading.value = false
      }
    }

    // 设为默认账号
    const setDefault = async (accountId) => {
      actionLoading.value = true
      error.value = ''
      
      try {
        await setDefaultRalendarAccount(accountId)
        await loadAccounts()
        emit('update')
      } catch (err) {
        console.error('设置默认账号失败:', err)
        error.value = err.response?.data?.error || '操作失败，请重试'
      } finally {
        actionLoading.value = false
      }
    }

    // 解绑账号
    const unbind = async (accountId) => {
      if (!confirm('确定要解绑该 Ralendar 账号吗？')) {
        return
      }

      actionLoading.value = true
      error.value = ''
      
      try {
        await unbindRalendarAccount(accountId)
        await loadAccounts()
        emit('update')
      } catch (err) {
        console.error('解绑账号失败:', err)
        error.value = err.response?.data?.error || '操作失败，请重试'
      } finally {
        actionLoading.value = false
      }
    }

    // 连接 Ralendar（跳转到授权页面）
    const connectRalendar = async () => {
      actionLoading.value = true
      error.value = ''
      
      try {
        // 获取授权 URL
        const response = await getRalendarAuthorizeUrl()
        const { authorize_url } = response
        
        if (authorize_url) {
          // 保存来源页面（用于授权后返回）
          sessionStorage.setItem('ralendar_auth_origin', window.location.pathname)
          
          // 跳转到 Ralendar 授权页面
          window.location.href = authorize_url
        } else {
          error.value = '获取授权链接失败'
          alert('获取授权链接失败')
        }
      } catch (err) {
        console.error('连接 Ralendar 失败:', err)
        error.value = err.response?.data?.error || '连接失败，请重试'
        alert(error.value)
      } finally {
        actionLoading.value = false
      }
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      loadAccounts()
    })

    return {
      accounts,
      loading,
      actionLoading,
      error,
      setDefault,
      unbind,
      connectRalendar,
      formatDate,
      // 暴露 loadAccounts 方法供父组件调用
      loadAccounts
    }
  }
}
</script>

<style scoped>
.ralendar-account-manager {
  padding: 1rem;
}

.account-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  margin-bottom: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.account-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.account-card.default {
  border-color: #0d6efd;
  background-color: #f8f9ff;
}

.account-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.account-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 1rem;
}

.account-avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin-right: 1rem;
}

.account-details {
  flex: 1;
}

.account-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.account-email {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.account-meta {
  font-size: 0.75rem;
}

.account-actions {
  display: flex;
  gap: 0.5rem;
}

.no-accounts i {
  display: block;
  margin-bottom: 1rem;
}

@media (max-width: 576px) {
  .account-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .account-actions {
    margin-top: 1rem;
    width: 100%;
  }

  .account-actions button {
    flex: 1;
  }
}
</style>

