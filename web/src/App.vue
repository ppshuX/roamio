<template>
  <div id="app">
    <router-view/>
    
    <!-- 全局 Ralendar 悬浮窗（仅移动端，且用户已开启） -->
    <!-- 电脑端不显示悬浮窗 -->
    
    <!-- 全局右侧栏（桌面端） -->
    <GlobalSidebar 
      :show="showGlobalSidebar"
      @close="showGlobalSidebar = false"
    />
  </div>
</template>

<script>
import { ref, provide } from 'vue'
import GlobalSidebar from '@/components/events/GlobalSidebar.vue'

export default {
  name: 'App',
  
  components: {
    GlobalSidebar
  },
  
  setup() {
    const showGlobalSidebar = ref(false)
    
    // 切换右侧栏显示（提供给 NavBar 使用）
    const toggleSidebar = () => {
      showGlobalSidebar.value = !showGlobalSidebar.value
    }
    
    provide('toggleRalendarSidebar', toggleSidebar)
    
    return {
      showGlobalSidebar
    }
  }
}
</script>

<style>
</style>
