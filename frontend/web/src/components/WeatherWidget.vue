<template>
  <div class="dropdown">
    <a
      href="#"
      class="nav-link dropdown-toggle"
      id="dropdownWeather"
      data-bs-toggle="dropdown"
      aria-expanded="false"
      @click.prevent="ensureWeatherLoaded"
    >
      <i class="bi bi-cloud-sun me-1"></i>
      查看天气
    </a>
      
    <!-- 详细天气信息下拉菜单 -->
    <ul class="dropdown-menu dropdown-menu-end weather-dropdown" aria-labelledby="dropdownWeather">
      <li>
        <!-- 未查询状态 -->
        <div v-if="!requested" class="weather-detail text-center">
          <i class="bi bi-cloud-sun" style="font-size: 2rem; color: var(--roamio-primary);"></i>
          <p class="mt-2 mb-2 text-muted">天气功能暂未开放</p>
        </div>

        <!-- 加载中状态 -->
        <div v-else-if="loading" class="weather-detail text-center">
          <i class="bi bi-hourglass-split" style="font-size: 2rem; color: var(--roamio-primary);"></i>
          <p class="mt-2 mb-0 text-muted">加载中...</p>
        </div>
        
        <!-- 加载失败状态 -->
        <div v-else-if="error" class="weather-detail text-center">
          <i class="bi bi-exclamation-circle" style="font-size: 2rem; color: #dc3545;"></i>
          <p class="mt-2 mb-2 text-muted">{{ errorMessage || '加载失败' }}</p>
          <button v-if="!weatherDisabled" @click="fetchWeather" class="btn btn-sm btn-primary">
            <i class="bi bi-arrow-clockwise me-1"></i>重试
          </button>
        </div>
        
        <!-- 天气信息 -->
        <div v-else class="weather-detail">
          <!-- 顶部：城市、天气和设置按钮 -->
          <div class="weather-header">
            <div class="header-left">
              <h5 class="city-name">
                <i class="bi bi-geo-alt-fill me-1"></i>{{ weather.city }}
              </h5>
              <p class="weather-desc">{{ weather.weather }}</p>
            </div>
            <button @click.stop="showSettings = !showSettings" class="settings-btn" title="设置默认城市">
              <i class="bi bi-gear-fill"></i>
            </button>
          </div>
          
          <!-- 主要天气信息 -->
          <div class="weather-main">
            <i :class="getWeatherIcon(weather.weather)" class="weather-icon"></i>
            <div class="temp-display">
              <span class="temp-number">{{ weather.temperature }}</span>
              <span class="temp-unit">°C</span>
            </div>
          </div>
          
          <!-- 详细数据 -->
          <div class="weather-stats">
            <div class="stat-item">
              <i class="bi bi-wind"></i>
              <div>
                <div class="stat-label">风力</div>
                <div class="stat-value">{{ weather.windDirection }} {{ weather.windPower }}级</div>
              </div>
            </div>
            <div class="stat-item">
              <i class="bi bi-droplet-fill"></i>
              <div>
                <div class="stat-label">湿度</div>
                <div class="stat-value">{{ weather.humidity }}%</div>
              </div>
            </div>
          </div>
          
          <!-- 城市设置面板（点击齿轮后显示） -->
          <transition name="slide">
            <div v-if="showSettings" class="settings-panel">
              <div class="panel-header">
                <h6><i class="bi bi-geo-alt-fill me-1"></i>设置默认城市</h6>
                <transition name="fade">
                  <small v-if="savedNotice" class="saved-badge">
                    <i class="bi bi-check-circle-fill me-1"></i>已保存
                  </small>
                </transition>
              </div>
              
              <!-- 搜索框 -->
              <div class="search-box">
                <input 
                  v-model="customCity"
                  type="text" 
                  class="search-input" 
                  placeholder="输入城市名称..."
                  @keyup.enter="changeCity(customCity)"
                />
                <button 
                  @click.stop="changeCity(customCity)" 
                  class="search-button"
                  :disabled="!customCity.trim()"
                >
                  <i class="bi bi-search"></i>
                </button>
              </div>
              
              <!-- 热门城市 -->
              <div class="hot-cities">
                <small class="hot-label">热门城市</small>
                <div class="city-grid">
                  <button 
                    v-for="city in hotCities" 
                    :key="city"
                    :class="['city-tag', { active: weather.city === city }]"
                    @click.stop="changeCity(city)"
                  >
                    {{ city }}
                  </button>
                </div>
              </div>
            </div>
          </transition>
          
          <!-- 底部：更新时间和刷新按钮 -->
          <div class="weather-footer">
            <small class="update-time">
              <i class="bi bi-clock me-1"></i>{{ weather.reportTime }}
            </small>
            <button @click.stop="fetchWeather" class="refresh-btn" title="刷新">
              <i class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLocationByIP, getWeatherByCity } from '@/api/weather'

const weatherFeatureEnabled = import.meta.env.VITE_WEATHER_ENABLED === 'true'
const requested = ref(false)
const loading = ref(false)
const error = ref(false)
const errorMessage = ref('')
const weatherDisabled = ref(false)
const weather = ref({
  city: '',
  weather: '',
  temperature: '',
  windDirection: '',
  windPower: '',
  humidity: '',
  reportTime: ''
})

// 热门城市列表
const hotCities = ['北京', '上海', '广州', '深圳', '成都', '杭州', '西安', '南京']

// 自定义城市输入
const customCity = ref('')

// 保存成功提示
const savedNotice = ref(false)

// 显示设置面板
const showSettings = ref(false)

// 获取天气图标
const getWeatherIcon = (weatherText) => {
  if (!weatherText) return 'bi bi-cloud'
  
  const text = weatherText.toLowerCase()
  if (text.includes('晴')) return 'bi bi-brightness-high'
  if (text.includes('云') || text.includes('阴')) return 'bi bi-cloud'
  if (text.includes('雨')) return 'bi bi-cloud-rain'
  if (text.includes('雪')) return 'bi bi-cloud-snow'
  if (text.includes('雷')) return 'bi bi-cloud-lightning'
  if (text.includes('雾') || text.includes('霾')) return 'bi bi-cloud-haze'
  return 'bi bi-cloud'
}

const markWeatherDisabled = () => {
  requested.value = true
  loading.value = false
  weatherDisabled.value = true
  errorMessage.value = '天气功能暂未开放'
  error.value = true
}

const ensureWeatherLoaded = () => {
  if (requested.value) return

  if (!weatherFeatureEnabled) {
    markWeatherDisabled()
    return
  }

  fetchWeather()
}

// 获取天气数据（调用后端API）
const fetchWeather = async () => {
  if (!weatherFeatureEnabled) {
    markWeatherDisabled()
    return
  }

  requested.value = true
  loading.value = true
  error.value = false
  errorMessage.value = ''
  weatherDisabled.value = false
  
  try {
    // 1. 先尝试从localStorage获取缓存的城市
    let city = localStorage.getItem('weatherCity')
    
    // 立即验证 city 是否为有效字符串
    if (city && typeof city === 'string' && city.trim() !== '') {
      // 使用缓存的城市
      city = city.trim()
    } else {
      // 缓存无效，清除并重新获取
      city = null
      localStorage.removeItem('weatherCity')
      localStorage.removeItem('weatherCacheTime')
    }
    
    // 2. 如果没有有效缓存，调用后端IP定位接口获取城市
    if (!city) {
      try {
        const locationData = await getLocationByIP()

        if (locationData.code === 'WEATHER_DISABLED') {
          weatherDisabled.value = true
          errorMessage.value = '天气功能暂未开放'
          error.value = true
          return
        }
        
        if (locationData.success && locationData.data && locationData.data.city) {
          city = String(locationData.data.city).trim()
          if (city) {
            // 缓存位置信息（24小时）
            localStorage.setItem('weatherCity', city)
            localStorage.setItem('weatherCacheTime', Date.now().toString())
          }
        }
      } catch (err) {
        const status = err.response?.status
        if (status !== 503 && status !== 429) {
          console.warn('IP定位失败:', err)
        }
      }
    }
    
    // 3. 最后的保底：如果还是没有有效城市，使用默认值
    if (!city) {
      city = '北京'
      localStorage.setItem('weatherCity', city)
      localStorage.setItem('weatherCacheTime', Date.now().toString())
    }
    
    // 4. 调用后端天气接口获取天气信息
    const weatherData = await getWeatherByCity(city)

    if (weatherData.code === 'WEATHER_DISABLED') {
      weatherDisabled.value = true
      errorMessage.value = '天气功能暂未开放'
      error.value = true
      return
    }
    
    if (weatherData.success) {
      const data = weatherData.data
      weather.value = {
        city: data.location,
        weather: data.weather,
        temperature: data.temperature,
        windDirection: data.windDir,
        windPower: data.windScale,
        humidity: data.humidity,
        reportTime: data.updateTime
      }
    } else {
      throw new Error(weatherData.message || '无法获取天气信息')
    }
  } catch (err) {
    const status = err.response?.status
    if (status === 503) {
      weatherDisabled.value = true
      errorMessage.value = '天气功能暂未开放'
    } else if (status === 429) {
      errorMessage.value = '请求过于频繁，请稍后再试'
    } else {
      errorMessage.value = '加载失败'
      console.error('获取天气失败:', err)
    }
    error.value = true
    // 清除可能已损坏的缓存
    localStorage.removeItem('weatherCity')
    localStorage.removeItem('weatherCacheTime')
  } finally {
    loading.value = false
  }
}

// 检查缓存是否过期（24小时）
const isCacheExpired = () => {
  const cacheTime = localStorage.getItem('weatherCacheTime')
  if (!cacheTime) return true
  const now = Date.now()
  const diff = now - parseInt(cacheTime)
  return diff > 24 * 60 * 60 * 1000 // 24小时
}

// 切换城市
const changeCity = (city) => {
  if (!city || typeof city !== 'string' || city.trim() === '') {
    return
  }
  
  city = city.trim()
  
  // 更新缓存（保存为默认城市）
  localStorage.setItem('weatherCity', city)
  localStorage.setItem('weatherCacheTime', Date.now().toString())
  
  // 清空输入框
  customCity.value = ''
  
  // 显示保存成功提示
  savedNotice.value = true
  setTimeout(() => {
    savedNotice.value = false
  }, 2000)
  
  // 重新获取天气
  fetchWeather()
}

onMounted(() => {
  // 清理旧版本的缓存键（兼容性清理）
  localStorage.removeItem('weatherAdcode')
  
  // 检查缓存是否过期
  if (isCacheExpired()) {
    localStorage.removeItem('weatherCity')
    localStorage.removeItem('weatherCacheTime')
  }
  
  if (!weatherFeatureEnabled) {
    localStorage.removeItem('weatherCity')
    localStorage.removeItem('weatherCacheTime')
  }
})
</script>

<style scoped>
/* 下拉菜单 */
.weather-dropdown {
  min-width: 320px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: none;
}

.weather-dropdown > li {
  list-style: none;
  padding: 0;
}

/* 天气详情容器 - 白色背景 */
.weather-detail {
  padding: 1.25rem;
  background: white;
  color: #333;
}

/* 顶部 - 城市和设置按钮 */
.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.header-left {
  flex: 1;
}

.city-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--roamio-primary);
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
}

.weather-desc {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.settings-btn {
  background: var(--roamio-primary);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(var(--bs-primary-rgb), 0.3);
}

.settings-btn i {
  display: block;
  line-height: 1;
}

.settings-btn:hover {
  background: var(--roamio-primary-active);
  transform: rotate(90deg);
  box-shadow: 0 4px 12px rgba(var(--bs-primary-rgb), 0.4);
}

/* 主要天气显示 */
.weather-main {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 1.5rem 0;
  background: var(--roamio-primary-muted);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.weather-icon {
  font-size: 4rem;
  color: var(--roamio-primary);
}

.temp-display {
  display: flex;
  align-items: flex-start;
}

.temp-number {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
  color: #333;
}

.temp-unit {
  font-size: 1.2rem;
  font-weight: 400;
  margin-top: 0.5rem;
  color: #666;
}

/* 详细数据 */
.weather-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 10px;
}

.stat-item i {
  font-size: 1.5rem;
  color: var(--roamio-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: #999;
  margin-bottom: 0.125rem;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

/* 设置面板 */
.settings-panel {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-header h6 {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--roamio-primary);
  margin: 0;
  display: flex;
  align-items: center;
}

.saved-badge {
  font-size: 0.75rem;
  color: #4caf50;
  background: #4caf5020;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
}

/* 搜索框 */
.search-box {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
  background: white;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  color: #333;
  font-size: 0.85rem;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: var(--roamio-primary);
}

.search-button {
  background: var(--roamio-primary);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-button:hover:not(:disabled) {
  background: var(--roamio-primary-active);
}

.search-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 热门城市 */
.hot-cities {
  margin-top: 1rem;
}

.hot-label {
  font-size: 0.75rem;
  color: #999;
  display: block;
  margin-bottom: 0.5rem;
}

.city-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.city-tag {
  background: white;
  border: 1px solid #ddd;
  color: #333;
  padding: 0.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.city-tag:hover {
  border-color: var(--roamio-primary);
  color: var(--roamio-primary);
}

.city-tag.active {
  background: var(--roamio-primary);
  border-color: var(--roamio-primary);
  color: white;
  font-weight: 600;
}

/* 底部 */
.weather-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.update-time {
  font-size: 0.75rem;
  color: #999;
  display: flex;
  align-items: center;
}

.refresh-btn {
  background: var(--roamio-primary);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  box-shadow: 0 2px 6px rgba(var(--bs-primary-rgb), 0.2);
}

.refresh-btn i {
  display: block;
  line-height: 1;
}

.refresh-btn:hover {
  background: var(--roamio-primary-active);
  transform: rotate(180deg);
  box-shadow: 0 4px 10px rgba(var(--bs-primary-rgb), 0.3);
}

/* 动画 */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
  max-height: 300px;
  overflow: hidden;
}

.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 移动端优化 - 全部缩小 */
@media (max-width: 768px) {
  .weather-dropdown {
    min-width: 90vw;
    max-width: 90vw;
    font-size: 0.85rem;
  }
  
  .weather-detail {
    padding: 0.875rem;
  }
  
  .weather-header {
    margin-bottom: 0.875rem;
  }
  
  .city-name {
    font-size: 0.95rem;
  }
  
  .weather-desc {
    font-size: 0.8rem;
  }
  
  .settings-btn {
    width: 28px;
    height: 28px;
    font-size: 0.9rem;
  }
  
  .weather-main {
    padding: 1rem 0;
    gap: 1rem;
  }
  
  .weather-icon {
    font-size: 2.5rem;
  }
  
  .temp-number {
    font-size: 2rem;
  }
  
  .temp-unit {
    font-size: 0.9rem;
    margin-top: 0.3rem;
  }
  
  .weather-stats {
    gap: 0.5rem;
  }
  
  .stat-item {
    padding: 0.5rem;
  }
  
  .stat-item i {
    font-size: 1.2rem;
  }
  
  .stat-label {
    font-size: 0.65rem;
  }
  
  .stat-value {
    font-size: 0.8rem;
  }
  
  .settings-panel {
    padding: 0.75rem;
  }
  
  .panel-header h6 {
    font-size: 0.85rem;
  }
  
  .saved-badge {
    font-size: 0.65rem;
    padding: 0.2rem 0.4rem;
  }
  
  .search-box {
    margin-bottom: 0.75rem;
  }
  
  .search-input {
    font-size: 0.8rem;
    padding: 0.4rem 0.875rem;
  }
  
  .search-button {
    width: 36px;
    height: 36px;
    font-size: 0.9rem;
  }
  
  .hot-label {
    font-size: 0.7rem;
  }
  
  .city-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 0.375rem;
  }
  
  .city-tag {
    padding: 0.375rem 0.25rem;
    font-size: 0.7rem;
  }
  
  .weather-footer {
    padding-top: 0.75rem;
  }
  
  .update-time {
    font-size: 0.65rem;
  }
  
  .refresh-btn {
    width: 26px;
    height: 26px;
    font-size: 0.85rem;
  }
}
</style>
