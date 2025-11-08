<template>
  <div id="app">
    <router-view/>
    
    <!-- 全局 Ralendar 悬浮窗（移动端） -->
    <GlobalRalendarButton v-if="showGlobalFloating" />
    
    <!-- 全局右侧栏（桌面端） -->
    <GlobalSidebar 
      :show="showGlobalSidebar"
      @close="showGlobalSidebar = false"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, provide } from 'vue'
import { useUserStore } from '@/stores/user'
import GlobalRalendarButton from '@/components/events/GlobalRalendarButton.vue'
import GlobalSidebar from '@/components/events/GlobalSidebar.vue'

export default {
  name: 'App',
  
  components: {
    GlobalRalendarButton,
    GlobalSidebar
  },
  
  setup() {
    const userStore = useUserStore()
    const floatingEnabled = ref(false)
    const showGlobalSidebar = ref(false)
    const windowWidth = ref(window.innerWidth)
    
    // 检查是否为移动端
    const isMobile = computed(() => windowWidth.value <= 768)
    
    // 检查是否显示全局悬浮窗（仅移动端）
    const showGlobalFloating = computed(() => {
      return userStore.isLoggedIn && floatingEnabled.value && isMobile.value
    })
    
    // 切换右侧栏显示
    const toggleSidebar = () => {
      showGlobalSidebar.value = !showGlobalSidebar.value
    }
    
    // 提供给子组件使用
    provide('toggleRalendarSidebar', toggleSidebar)
    
    // 加载设置
    onMounted(() => {
      const saved = localStorage.getItem('ralendar_floating_enabled')
      floatingEnabled.value = saved === 'true'
      
      // 监听窗口大小变化
      const handleResize = () => {
        windowWidth.value = window.innerWidth
      }
      window.addEventListener('resize', handleResize)
      
      // 监听设置变化
      window.addEventListener('storage', (e) => {
        if (e.key === 'ralendar_floating_enabled') {
          floatingEnabled.value = e.newValue === 'true'
        }
      })
    })
    
    return {
      showGlobalFloating,
      showGlobalSidebar
    }
  }
}
</script>

<style>
</style>
