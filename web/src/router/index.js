import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/TripListView.vue'),
    meta: { title: '旅行大厅' }
  },
  {
    path: '/login/',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '用户登录' }
  },
  {
    path: '/register/',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { title: '用户注册' }
  },
  {
    path: '/forgot-password/',
    name: 'forgot-password',
    component: () => import('@/views/auth/ForgotPasswordView.vue'),
    meta: { title: '找回密码' }
  },
  {
    path: '/user/center/',
    name: 'user-center',
    component: () => import('@/views/user-center/UserCenterView.vue'),
    meta: {
      title: '个人中心',
      requiresAuth: true
    }
  },
  {
    path: '/trip/:slug/',
    name: 'trip-detail',
    component: () => import('@/views/TripDetailView.vue'),
    meta: { title: '旅行详情', dynamicTitle: true }
  },
  {
    path: '/my-trips/',
    name: 'my-trips',
    component: () => import('@/views/MyTripsView.vue'),
    meta: {
      title: '我的旅行',
      requiresAuth: true
    }
  },
  {
    path: '/editor/',
    redirect: '/my-trips/'
  },
  {
    path: '/editor/new/',
    name: 'trip-editor-new',
    component: () => import('@/views/TripEditorView.vue'),
    meta: {
      title: '创建旅行计划',
      requiresAuth: true
    }
  },
  {
    path: '/editor/:slug/',
    name: 'trip-editor',
    component: () => import('@/views/TripEditorView.vue'),
    meta: {
      title: '编辑旅行计划',
      requiresAuth: true
    }
  },
  {
    path: '/settings/qq/receive_code',
    name: 'qq-callback',
    component: () => import('@/views/auth/QQCallbackView.vue'),
    meta: {
      title: 'QQ登录回调',
      requiresAuth: false
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题（不带平台后缀）
  document.title = to.meta.title || ''

  // 权限检查
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) {
    // 需要登录但未登录，跳转到登录页
    next({
      path: '/login/',
      query: { redirect: to.fullPath }  // 保存原本要去的页面
    })
  } else if ((to.path === '/login/' || to.path === '/register/' || to.path === '/forgot-password/') && token) {
    // 已登录用户访问登录/注册/忘记密码页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
