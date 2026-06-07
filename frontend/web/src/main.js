import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import { useUserStore } from './stores'

// 导入Bootstrap样式
import 'bootstrap/dist/css/bootstrap.min.css'
import './styles/roamio-theme.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

const app = createApp(App)

app.use(pinia)
app.use(router)

const bootstrap = async () => {
  const userStore = useUserStore(pinia)
  userStore.migrateLegacyTokens()
  app.mount('#app')

  // 页面先渲染，再通过 HttpOnly refresh cookie 尝试恢复 access token。
  // 生产代理或网络异常不应阻塞整个 Vue 应用挂载。
  userStore.restoreAccessToken().catch((error) => {
    console.error('恢复登录态失败:', error)
  })
}

bootstrap().catch((error) => {
  console.error('应用启动失败:', error)
})
