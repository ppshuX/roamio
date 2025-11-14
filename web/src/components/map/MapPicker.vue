<template>
  <div v-if="show" class="map-picker-overlay" @click.self="$emit('close')">
    <div class="map-picker-container">
      <!-- 头部 -->
      <div class="map-header">
        <h6>选择地点</h6>
        <div class="map-type-selector">
          <button 
            :class="['map-type-btn', { active: mapType === 'baidu' }]"
            @click="switchMapType('baidu')"
          >
            百度地图
          </button>
          <button 
            :class="['map-type-btn', { active: mapType === 'amap' }]"
            @click="switchMapType('amap')"
          >
            高德地图
          </button>
        </div>
        <button @click="$emit('close')" class="btn-close">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
          </svg>
        </button>
      </div>
      
      <!-- 搜索框 -->
      <div class="map-search">
        <input 
          v-model="searchKeyword" 
          type="text" 
          class="form-control" 
          placeholder="搜索地点..."
          @input="handleSearch"
        >
      </div>
      
      <!-- 地图容器 -->
      <div ref="mapContainer" class="map-container"></div>
      
      <!-- 已选位置信息 -->
      <div v-if="selectedLocation" class="location-info">
        <div class="location-name">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/>
          </svg>
          {{ selectedLocation.name }}
        </div>
        <div class="location-coords text-muted small">
          坐标: {{ selectedLocation.lat.toFixed(6) }}, {{ selectedLocation.lng.toFixed(6) }}
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="map-footer">
        <button class="btn btn-secondary" @click="$emit('close')">取消</button>
        <button class="btn btn-primary" @click="handleConfirm" :disabled="!selectedLocation">
          确定
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick, defineComponent } from 'vue'

export default defineComponent({
  name: 'MapPicker',
  
  props: {
    show: {
      type: Boolean,
      default: false
    },
    defaultLocation: {
      type: String,
      default: ''
    }
  },
  
  emits: ['close', 'select'],
  
  setup(props, { emit }) {
    const mapContainer = ref(null)
    const searchKeyword = ref('')
    const selectedLocation = ref(null)
    const mapType = ref(localStorage.getItem('preferredMapType') || 'baidu') // 记住用户偏好
    let map = null
    let marker = null
    let searchTimer = null
    
    // 切换地图类型
    const switchMapType = (type) => {
      mapType.value = type
      localStorage.setItem('preferredMapType', type)
      selectedLocation.value = null
      // 销毁旧地图
      if (map) {
        if (mapType.value === 'baidu' && map.destroy) {
          map.destroy()
        } else if (mapType.value === 'amap' && map.destroy) {
          map.destroy()
        }
        map = null
        marker = null
      }
      // 重新初始化
      nextTick(() => {
        initMap()
      })
    }
    
    // 初始化地图
    const initMap = () => {
      if (!mapContainer.value) return
      
      if (mapType.value === 'baidu') {
        initBaiduMap()
      } else {
        initAmapMap()
      }
    }
    
    // 初始化百度地图
    const initBaiduMap = () => {
      if (!window.BMap) {
        console.error('❌ 百度地图 API 未加载，请检查：1) API Key 是否正确 2) Referer 白名单是否配置')
        return
      }
      
      console.log('✅ 百度地图 API 已加载，开始初始化...')
      
      // 创建地图实例
      map = new window.BMap.Map(mapContainer.value)
      
      // 设置中心点（默认北京）
      const point = new window.BMap.Point(116.404, 39.915)
      map.centerAndZoom(point, 12)
      
      // 启用滚轮缩放
      map.enableScrollWheelZoom(true)
      
      // 添加控件
      map.addControl(new window.BMap.NavigationControl())
      map.addControl(new window.BMap.ScaleControl())
      
      // 点击地图选择位置
      map.addEventListener('click', (e) => {
        const point = e.point
        setMarkerBaidu(point)
        getLocationNameBaidu(point)
      })
    }
    
    // 初始化高德地图
    const initAmapMap = () => {
      if (!window.AMap) return
      
      // 创建地图实例
      map = new window.AMap.Map(mapContainer.value, {
        zoom: 12,
        center: [116.404, 39.915], // 默认北京
        viewMode: '2D'
      })
      
      // 点击地图选择位置
      map.on('click', (e) => {
        const lnglat = e.lnglat
        setMarkerAmap(lnglat)
        getLocationNameAmap(lnglat)
      })
    }
    
    // 百度地图：设置标记
    const setMarkerBaidu = (point) => {
      // 移除旧标记
      if (marker) {
        map.removeOverlay(marker)
      }
      
      // 添加新标记
      marker = new window.BMap.Marker(point)
      map.addOverlay(marker)
      
      // 动画效果
      marker.setAnimation(window.BMAP_ANIMATION_BOUNCE)
      setTimeout(() => {
        marker.setAnimation(null)
      }, 1000)
    }
    
    // 高德地图：设置标记
    const setMarkerAmap = (lnglat) => {
      // 移除旧标记
      if (marker) {
        map.remove(marker)
      }
      
      // 添加新标记
      marker = new window.AMap.Marker({
        position: lnglat,
        animation: 'AMAP_ANIMATION_DROP'
      })
      map.add(marker)
    }
    
    // 百度地图：获取地点名称（反向地理编码）
    let geocodeTimer = null
    const getLocationNameBaidu = (point) => {
      if (geocodeTimer) {
        clearTimeout(geocodeTimer)
      }
      
      geocodeTimer = setTimeout(() => {
        const gc = new window.BMap.Geocoder()
        gc.getLocation(point, (result) => {
          if (result) {
            selectedLocation.value = {
              name: result.address,
              lat: point.lat,
              lng: point.lng
            }
          }
        })
      }, 500)
    }
    
    // 高德地图：获取地点名称（反向地理编码）
    const getLocationNameAmap = (lnglat) => {
      if (geocodeTimer) {
        clearTimeout(geocodeTimer)
      }
      
      geocodeTimer = setTimeout(() => {
        window.AMap.plugin('AMap.Geocoder', () => {
          const geocoder = new window.AMap.Geocoder()
          geocoder.getAddress(lnglat, (status, result) => {
            if (status === 'complete' && result.info === 'OK') {
              selectedLocation.value = {
                name: result.regeocode.formattedAddress,
                lat: lnglat.lat,
                lng: lnglat.lng
              }
            } else {
              console.error('高德地图地理编码失败:', status, result)
            }
          })
        })
      }, 500)
    }
    
    // 搜索地点
    const handleSearch = () => {
      if (searchTimer) {
        clearTimeout(searchTimer)
      }
      
      searchTimer = setTimeout(() => {
        if (!searchKeyword.value || !map) return
        
        if (mapType.value === 'baidu') {
          handleSearchBaidu()
        } else {
          handleSearchAmap()
        }
      }, 300) // 防抖 300ms
    }
    
    // 百度地图搜索
    const handleSearchBaidu = () => {
      const localSearch = new window.BMap.LocalSearch(map, {
        onSearchComplete: (results) => {
          if (results && results.getCurrentNumPois() > 0) {
            const poi = results.getPoi(0)
            const point = poi.point
            
            map.centerAndZoom(point, 15)
            setMarkerBaidu(point)
            
            selectedLocation.value = {
              name: poi.title,
              lat: point.lat,
              lng: point.lng
            }
          }
        }
      })
      localSearch.search(searchKeyword.value)
    }
    
    // 高德地图搜索
    const handleSearchAmap = () => {
      window.AMap.plugin('AMap.PlaceSearch', () => {
        const placeSearch = new window.AMap.PlaceSearch({
          map: map
        })
        
        placeSearch.search(searchKeyword.value, (status, result) => {
          if (status === 'complete' && result.poiList.pois.length > 0) {
            const poi = result.poiList.pois[0]
            const lnglat = poi.location
            
            map.setZoomAndCenter(15, lnglat)
            setMarkerAmap(lnglat)
            
            selectedLocation.value = {
              name: poi.name,
              lat: lnglat.lat,
              lng: lnglat.lng
            }
          }
        })
      })
    }
    
    // 确认选择
    const handleConfirm = () => {
      if (selectedLocation.value) {
        emit('select', selectedLocation.value)
        emit('close')
      }
    }
    
    // 等待百度地图 API 加载
    const waitForBaiduMap = () => {
      return new Promise((resolve) => {
        if (window.BMap) {
          resolve()
          return
        }
        
        // 最多等待 5 秒
        let attempts = 0
        const maxAttempts = 50
        const checkInterval = setInterval(() => {
          attempts++
          if (window.BMap) {
            clearInterval(checkInterval)
            resolve()
          } else if (attempts >= maxAttempts) {
            clearInterval(checkInterval)
            console.error('⚠️ 百度地图 API 加载超时')
            resolve()
          }
        }, 100)
      })
    }
    
    // 监听显示状态
    watch(() => props.show, async (newVal) => {
      if (newVal) {
        await nextTick()
        
        // 如果是百度地图，等待 API 加载
        if (mapType.value === 'baidu') {
          await waitForBaiduMap()
        }
        
        initMap()
        
        // 如果有默认地点，搜索它
        if (props.defaultLocation) {
          searchKeyword.value = props.defaultLocation
          handleSearch()
        }
      }
    })
    
    return {
      mapContainer,
      searchKeyword,
      selectedLocation,
      mapType,
      switchMapType,
      handleSearch,
      handleConfirm
    }
  }
})
</script>

<style scoped>
.map-picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.map-picker-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.map-header h6 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

/* 地图类型选择器 */
.map-type-selector {
  display: flex;
  gap: 8px;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px;
  border-radius: 8px;
}

.map-type-btn {
  padding: 6px 16px;
  border: none;
  background: transparent;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.map-type-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.map-type-btn.active {
  background: white;
  color: #667eea;
  font-weight: 600;
}

.btn-close {
  background: white;
  border: none;
  color: #667eea;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-close:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.map-search {
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.map-search .form-control {
  border-radius: 8px;
}

.map-container {
  flex: 1;
  min-height: 400px;
  background: #f5f5f5;
}

.location-info {
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.location-name {
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.location-name svg {
  color: #667eea;
}

.map-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
}

.map-footer .btn {
  border-radius: 8px;
  padding: 8px 24px;
  font-weight: 500;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .map-picker-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .map-header {
    border-radius: 0;
  }
  
  .map-container {
    min-height: 300px;
  }
}
</style>

