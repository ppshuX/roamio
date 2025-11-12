<template>
  <div class="weather-widget">
    <!-- 加载中 -->
    <div v-if="loading" class="weather-btn">
      <i class="bi bi-hourglass-split"></i>
      <span class="weather-text">加载中...</span>
    </div>
    
    <!-- 加载失败 -->
    <div v-else-if="error" class="weather-btn" @click="fetchWeather" title="点击重试">
      <i class="bi bi-exclamation-circle"></i>
      <span class="weather-text">天气</span>
    </div>
    
    <!-- 天气信息 -->
    <div v-else class="dropdown">
      <a
        href="#"
        class="weather-btn dropdown-toggle"
        id="dropdownWeather"
        data-bs-toggle="dropdown"
        aria-expanded="false"
        @click.prevent
      >
        <i :class="getWeatherIcon(weather.weather)"></i>
        <span class="weather-text">{{ weather.temperature }}°</span>
        <span class="weather-city d-none d-md-inline">{{ weather.city }}</span>
      </a>
      
      <!-- 详细天气信息下拉菜单 -->
      <div class="dropdown-menu dropdown-menu-end weather-dropdown" aria-labelledby="dropdownWeather">
        <div class="weather-detail">
          <div class="weather-header">
            <i :class="getWeatherIcon(weather.weather)" class="weather-icon-large"></i>
            <div>
              <h6 class="mb-0">{{ weather.city }}</h6>
              <small class="text-muted">{{ weather.weather }}</small>
            </div>
          </div>
          
          <div class="weather-stats">
            <div class="stat-item">
              <i class="bi bi-thermometer-half"></i>
              <div>
                <small class="text-muted">温度</small>
                <div>{{ weather.temperature }}°C</div>
              </div>
            </div>
            <div class="stat-item">
              <i class="bi bi-wind"></i>
              <div>
                <small class="text-muted">风力</small>
                <div>{{ weather.windPower }}级</div>
              </div>
            </div>
            <div class="stat-item">
              <i class="bi bi-droplet"></i>
              <div>
                <small class="text-muted">湿度</small>
                <div>{{ weather.humidity }}%</div>
              </div>
            </div>
          </div>
          
          <div class="weather-footer">
            <small class="text-muted">
              <i class="bi bi-clock"></i>
              {{ weather.reportTime }}
            </small>
            <button @click="fetchWeather" class="btn btn-sm btn-link">
              <i class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
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
        
        // 2. 如果没有缓存，调用后端IP定位接口获取城市
        if (!city) {
          const locationRes = await fetch('/api/location/')
          const locationData = await locationRes.json()
          
          if (locationData.success) {
            city = locationData.data.city
            // 缓存位置信息（24小时）
            localStorage.setItem('weatherCity', city)
            localStorage.setItem('weatherCacheTime', Date.now().toString())
          } else {
            // 定位失败，使用默认城市
            city = '北京'
          }
        }
        
        // 3. 调用后端天气接口获取天气信息
        const weatherRes = await fetch(`/api/weather/?location=${encodeURIComponent(city)}`)
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
    
    onMounted(() => {
      // 检查缓存是否过期
      if (isCacheExpired()) {
        localStorage.removeItem('weatherCity')
        localStorage.removeItem('weatherAdcode')
        localStorage.removeItem('weatherCacheTime')
      }
      fetchWeather()
    })
    
    return {
      loading,
      error,
      weather,
      getWeatherIcon,
      fetchWeather
    }
  }
}
</script>

<style scoped>
.weather-widget {
  margin-right: 1rem;
}

.weather-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  padding: 0.5rem 1rem;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  white-space: nowrap;
}

.weather-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
  color: white;
}

.weather-btn i {
  font-size: 1.2rem;
}

.weather-text {
  font-weight: 500;
  font-size: 1rem;
}

.weather-city {
  opacity: 0.9;
  margin-left: 0.25rem;
}

/* 下拉菜单样式 */
.weather-dropdown {
  min-width: 280px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: none;
  margin-top: 0.5rem;
  padding: 0;
}

.weather-detail {
  padding: 1.25rem;
}

.weather-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.weather-icon-large {
  font-size: 3rem;
  color: #667eea;
}

.weather-header h6 {
  font-weight: 600;
  color: #333;
}

.weather-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-item i {
  font-size: 1.5rem;
  color: #667eea;
  width: 24px;
  text-align: center;
}

.stat-item small {
  display: block;
  font-size: 0.75rem;
}

.stat-item > div > div {
  font-weight: 600;
  color: #333;
}

.weather-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.weather-footer small {
  font-size: 0.75rem;
}

.weather-footer .btn-link {
  color: #667eea;
  text-decoration: none;
  padding: 0.25rem 0.5rem;
}

.weather-footer .btn-link:hover {
  color: #764ba2;
}

/* 移动端优化 */
@media (max-width: 991px) {
  .weather-widget {
    margin-right: 0.5rem;
  }
  
  .weather-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .weather-btn i {
    font-size: 1rem;
  }
  
  .weather-text {
    font-size: 0.9rem;
  }
  
  .weather-dropdown {
    min-width: 260px;
    max-width: calc(100vw - 30px);
  }
}
</style>

