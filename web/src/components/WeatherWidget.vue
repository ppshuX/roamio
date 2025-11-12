<template>
  <div class="dropdown">
    <a
      href="#"
      class="nav-link dropdown-toggle"
      id="dropdownWeather"
      data-bs-toggle="dropdown"
      aria-expanded="false"
      @click.prevent
    >
      <i class="bi bi-cloud-sun me-1"></i>
      查看天气
    </a>
      
    <!-- 详细天气信息下拉菜单 -->
    <ul class="dropdown-menu dropdown-menu-end weather-dropdown" aria-labelledby="dropdownWeather">
      <li>
        <!-- 加载中状态 -->
        <div v-if="loading" class="weather-detail text-center">
          <i class="bi bi-hourglass-split" style="font-size: 2rem; color: #667eea;"></i>
          <p class="mt-2 mb-0 text-muted">加载中...</p>
        </div>
        
        <!-- 加载失败状态 -->
        <div v-else-if="error" class="weather-detail text-center">
          <i class="bi bi-exclamation-circle" style="font-size: 2rem; color: #dc3545;"></i>
          <p class="mt-2 mb-2 text-muted">加载失败</p>
          <button @click="fetchWeather" class="btn btn-sm btn-primary">
            <i class="bi bi-arrow-clockwise me-1"></i>重试
          </button>
        </div>
        
        <!-- 天气信息 -->
        <div v-else class="weather-detail">
          <!-- 顶部：城市和天气状况 -->
          <div class="weather-header">
            <div class="weather-main">
              <i :class="getWeatherIcon(weather.weather)" class="weather-icon-large"></i>
              <div class="weather-temp">
                <span class="temp-number">{{ weather.temperature }}</span>
                <span class="temp-unit">°C</span>
              </div>
            </div>
            <div class="weather-info">
              <h6 class="city-name">{{ weather.city }}</h6>
              <p class="weather-desc">{{ weather.weather }}</p>
            </div>
          </div>
          
          <!-- 详细数据卡片 -->
          <div class="weather-stats">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="bi bi-wind"></i>
              </div>
              <div class="stat-content">
                <div class="stat-label">风力</div>
                <div class="stat-value">{{ weather.windDirection }} {{ weather.windPower }}级</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="bi bi-droplet-fill"></i>
              </div>
              <div class="stat-content">
                <div class="stat-label">湿度</div>
                <div class="stat-value">{{ weather.humidity }}%</div>
              </div>
            </div>
          </div>
          
          <!-- 切换城市 -->
          <div class="city-selector">
            <div class="selector-header">
              <div class="selector-label">
                <i class="bi bi-geo-alt-fill me-1"></i>切换城市
              </div>
              <transition name="fade">
                <small v-if="savedNotice" class="saved-notice">
                  <i class="bi bi-check-circle-fill me-1"></i>已设为默认
                </small>
              </transition>
            </div>
            
            <!-- 自定义输入 -->
            <div class="custom-input">
              <input 
                v-model="customCity"
                type="text" 
                class="city-input" 
                placeholder="输入城市名称..."
                @keyup.enter="changeCity(customCity)"
              />
              <button 
                @click="changeCity(customCity)" 
                class="search-btn"
                :disabled="!customCity.trim()"
              >
                <i class="bi bi-search"></i>
              </button>
            </div>
            
            <!-- 热门城市 -->
            <div class="city-list">
              <button 
                v-for="city in hotCities" 
                :key="city"
                :class="['city-btn', { active: weather.city === city }]"
                @click="changeCity(city)"
              >
                {{ city }}
              </button>
            </div>
          </div>
          
          <!-- 底部：更新时间和刷新按钮 -->
          <div class="weather-footer">
            <small class="update-time">
              <i class="bi bi-clock me-1"></i>{{ weather.reportTime }}
            </small>
            <button @click="fetchWeather" class="refresh-btn" title="刷新天气">
              <i class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'WeatherWidget',
  
  setup() {
    const loading = ref(true)
    const error = ref(false)
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
    
    // 获取天气数据（调用后端API）
    const fetchWeather = async () => {
      loading.value = true
      error.value = false
      
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
            const locationRes = await fetch('/api/v1/location/')
            const locationData = await locationRes.json()
            
            if (locationData.success && locationData.data && locationData.data.city) {
              city = String(locationData.data.city).trim()
              if (city) {
                // 缓存位置信息（24小时）
                localStorage.setItem('weatherCity', city)
                localStorage.setItem('weatherCacheTime', Date.now().toString())
              }
            }
          } catch (err) {
            console.warn('IP定位失败:', err)
          }
        }
        
        // 3. 最后的保底：如果还是没有有效城市，使用默认值
        if (!city) {
          city = '北京'
          localStorage.setItem('weatherCity', city)
          localStorage.setItem('weatherCacheTime', Date.now().toString())
        }
        
        // 4. 调用后端天气接口获取天气信息
        const weatherRes = await fetch(`/api/v1/weather/?location=${encodeURIComponent(city)}`)
        const weatherData = await weatherRes.json()
        
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
        console.error('获取天气失败:', err)
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
      
      fetchWeather()
    })
    
    return {
      loading,
      error,
      weather,
      hotCities,
      customCity,
      savedNotice,
      getWeatherIcon,
      fetchWeather,
      changeCity
    }
  }
}
</script>

<style scoped>
/* 下拉菜单样式 */
.weather-dropdown {
  min-width: 320px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
  border: none;
}

.weather-dropdown > li {
  list-style: none;
  padding: 0;
}

/* 天气详情容器 */
.weather-detail {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* 顶部区域 */
.weather-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.weather-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.weather-icon-large {
  font-size: 4rem;
  color: rgba(255, 255, 255, 0.95);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

.weather-temp {
  display: flex;
  align-items: flex-start;
  gap: 0.25rem;
}

.temp-number {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.temp-unit {
  font-size: 1.5rem;
  font-weight: 400;
  margin-top: 0.5rem;
  opacity: 0.9;
}

.weather-info {
  text-align: left;
}

.city-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: white;
}

.weather-desc {
  font-size: 0.95rem;
  margin: 0;
  opacity: 0.9;
}

/* 详细数据卡片 */
.weather-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.stat-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  font-size: 1.25rem;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  opacity: 0.85;
  margin-bottom: 0.125rem;
}

.stat-value {
  font-size: 0.95rem;
  font-weight: 600;
}

/* 底部区域 */
.weather-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.update-time {
  font-size: 0.75rem;
  opacity: 0.8;
  display: flex;
  align-items: center;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
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
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(180deg);
}

/* 城市选择器 */
.city-selector {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.selector-label {
  font-size: 0.85rem;
  opacity: 0.9;
  display: flex;
  align-items: center;
}

.saved-notice {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.95);
  background: rgba(76, 175, 80, 0.3);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 自定义城市输入 */
.custom-input {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.city-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 0.5rem 1rem;
  color: white;
  font-size: 0.85rem;
  outline: none;
  transition: all 0.3s ease;
}

.city-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.city-input:focus {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
}

.search-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.search-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.search-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.city-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.city-btn {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.city-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.city-btn.active {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
}
</style>


