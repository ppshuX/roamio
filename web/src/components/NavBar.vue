<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm sticky-top">
    <div class="container-fluid">
      <!-- Logo -->
      <router-link to="/" class="navbar-brand d-flex align-items-center">
        <img src="/logo_Roamio.png" alt="Roamio Logo" class="brand-logo me-2">
        <span class="brand-text">Roamio</span>
      </router-link>
      
      <!-- Toggle按钮（移动端） -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
    <!-- 导航项 -->
    <div class="collapse navbar-collapse" id="navbarNav" style="overflow: visible;">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link to="/" class="nav-link">
              <i class="bi bi-house-door me-1"></i>
              旅行大厅
            </router-link>
          </li>
          <li v-if="isLoggedIn" class="nav-item">
            <router-link to="/my-trips/" class="nav-link">
              <i class="bi bi-folder me-1"></i>
              我的旅行
            </router-link>
          </li>
          <li v-if="isLoggedIn" class="nav-item">
            <a href="#" class="nav-link" @click.prevent="handleRalendarClick">
              <i class="bi bi-calendar-check me-1"></i>
              Ralendar
            </a>
          </li>
          <!-- 天气导航项 -->
          <li class="nav-item">
            <WeatherWidget />
          </li>
        </ul>
        
        <!-- 右侧：用户信息 -->
        <div class="d-flex align-items-center">
          <!-- 已登录 -->
          <template v-if="isLoggedIn">
            <div class="dropdown dropdown-end">
              <a
                href="#"
                class="d-flex align-items-center text-white text-decoration-none dropdown-toggle user-dropdown-btn"
                id="dropdownUser"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <img
                  :src="avatar"
                  alt="avatar"
                  width="32"
                  height="32"
                  class="rounded-circle me-2"
                />
                <span>{{ username }}</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end text-small" aria-labelledby="dropdownUser">
                <li>
                  <router-link to="/user/center" class="dropdown-item">
                    <i class="bi bi-person me-2"></i>个人中心
                  </router-link>
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <a href="#" class="dropdown-item" @click.prevent="handleLogout">
                    <i class="bi bi-box-arrow-right me-2"></i>退出登录
                  </a>
                </li>
              </ul>
            </div>
          </template>
          
          <!-- 未登录 -->
          <template v-else>
            <router-link to="/login" class="btn btn-outline-light btn-sm me-2">
              登录
            </router-link>
            <router-link to="/register" class="btn btn-light btn-sm">
              注册
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import WeatherWidget from './WeatherWidget.vue'

export default {
  name: 'NavBar',
  components: {
    WeatherWidget
  },
  
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const toggleRalendarSidebar = inject('toggleRalendarSidebar', null)
    
    const isLoggedIn = computed(() => userStore.isLoggedIn)
    const username = computed(() => userStore.username)
    const avatar = computed(() => userStore.avatar)
    
    const handleLogout = async () => {
      if (!confirm('确定要退出登录吗？')) return
      
      try {
        await userStore.logout()
        router.push('/login')
      } catch (error) {
        console.error('退出失败:', error)
      }
    }
    
    const handleRalendarClick = () => {
      // 统一行为：切换右侧栏（手机端和桌面端都一样）
      if (toggleRalendarSidebar) {
        toggleRalendarSidebar()
      } else {
        console.error('toggleRalendarSidebar not available')
      }
    }
    
    return {
      isLoggedIn,
      username,
      avatar,
      handleRalendarClick,
      handleLogout
    }
  }
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border-bottom: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.navbar-brand {
  font-size: 1.5rem;
  font-weight: 800;
  color: white !important;
  text-decoration: none;
  transition: all 0.3s ease;
  letter-spacing: 2px;
}

.brand-logo {
  height: 36px;
  width: 36px;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.navbar-brand:hover .brand-logo {
  transform: scale(1.1) rotate(5deg);
}

.brand-text {
  background: linear-gradient(45deg, #fff 0%, #f0f0f0 50%, #fff 100%);
  background-size: 200% auto;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  font-size: 1.6rem;
  letter-spacing: 3px;
  text-shadow: 0 3px 8px rgba(255, 255, 255, 0.3);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0%, 100% {
    background-position: 0% center;
  }
  50% {
    background-position: 100% center;
  }
}

.navbar-brand:hover .brand-text {
  background-position: 100% center;
  transform: scale(1.08);
  filter: brightness(1.2);
}

.nav-link {
  color: rgba(255, 255, 255, 0.95) !important;
  font-weight: 500;
  transition: all 0.3s ease;
  border-radius: 8px;
  padding: 0.5rem 1rem !important;
}

.nav-link:hover {
  color: white !important;
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.dropdown-menu {
  min-width: 200px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: none;
  margin-top: 0.5rem;
  max-height: 80vh;
  overflow-y: auto;
}

.dropdown-item {
  padding: 0.75rem 1.25rem;
  transition: all 0.2s ease;
  border-radius: 8px;
  margin: 0.2rem;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateX(3px);
}

.dropdown {
  position: relative;
  z-index: 1050;
}

.user-dropdown-btn {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  padding: 0.5rem 1rem;
  transition: all 0.3s ease;
  white-space: nowrap;
  max-width: 100%;
  cursor: pointer;
}

.user-dropdown-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.user-dropdown-btn[aria-expanded="true"] {
  background: rgba(255, 255, 255, 0.35);
}

.btn-outline-light {
  border: 2px solid rgba(255, 255, 255, 0.8);
  color: white;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: white;
  transform: translateY(-2px);
}

.btn-light {
  background: white;
  color: #667eea;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-light:hover {
  background: rgba(255, 255, 255, 0.95);
  color: #764ba2;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 255, 255, 0.3);
}

/* 移动端优化 */
@media (max-width: 991px) {
  .navbar {
    padding: 0.75rem 0;
  }
  
  .navbar-brand {
    font-size: 1.3rem;
  }
  
  .brand-logo {
    height: 30px;
    width: 30px;
  }
  
  .brand-text {
    font-size: 1.35rem;
    letter-spacing: 2px;
  }
  
  .navbar-nav .nav-link {
    padding: 0.75rem 1rem;
  }
  
  .dropdown-menu {
    min-width: 180px;
    max-width: calc(100vw - 30px);
    position: absolute !important;
    right: 0;
    left: auto;
    margin-top: 0.5rem;
  }
  
  .user-dropdown-btn {
    font-size: 0.9rem;
    z-index: 1051;
  }
  
  /* 确保下拉菜单不会被导航栏遮挡 */
  .dropdown.show {
    overflow: visible;
  }
  
  /* 移动端确保下拉菜单在最上层 */
  .dropdown {
    z-index: 1050;
  }
  
  .navbar-collapse {
    z-index: 1049;
  }
}
</style>

