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

  // 页面刷新后优先通过 HttpOnly refresh cookie 自动恢复 access token
  await userStore.restoreAccessToken()

  app.mount('#app')
}

bootstrap().catch((error) => {
  console.error('应用启动失败，降级为直接挂载:', error)
  app.mount('#app')
})
