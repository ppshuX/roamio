<template>
  <div v-if="show" class="map-picker-overlay" @click.self="$emit('close')">
    <div class="map-picker-container">
      <div class="map-header">
        <h6>地点操作</h6>
        <button @click="$emit('close')" class="btn-close" aria-label="关闭">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z" />
          </svg>
        </button>
      </div>

      <div class="map-body">
        <div class="map-unavailable">
          <div class="map-unavailable-icon">
            <i class="bi bi-map"></i>
          </div>
          <h6>地图预览功能暂未开放</h6>
          <p>可先复制地点名称，或跳转到地图应用查看位置与路线。</p>
        </div>

        <label class="form-label" for="locationKeyword">地点名称</label>
        <input
          id="locationKeyword"
          v-model.trim="locationKeyword"
          type="text"
          class="form-control"
          placeholder="输入地点、地址或景点名称"
          @keyup.enter="handleConfirm"
        >

        <div class="map-actions">
          <button class="btn btn-outline-secondary" type="button" :disabled="!locationKeyword" @click="copyLocation">
            <i class="bi bi-clipboard"></i>
            复制地点
          </button>
          <a
            class="btn btn-outline-primary"
            :class="{ disabled: !locationKeyword }"
            :href="baiduMapUrl"
            target="_blank"
            rel="noopener noreferrer"
            @click.prevent="openIfReady(baiduMapUrl)"
          >
            <i class="bi bi-box-arrow-up-right"></i>
            打开百度地图
          </a>
          <a
            class="btn btn-outline-primary"
            :class="{ disabled: !locationKeyword }"
            :href="amapUrl"
            target="_blank"
            rel="noopener noreferrer"
            @click.prevent="openIfReady(amapUrl)"
          >
            <i class="bi bi-box-arrow-up-right"></i>
            打开高德地图
          </a>
        </div>

        <div v-if="copyMessage" class="copy-message">{{ copyMessage }}</div>
      </div>

      <div class="map-footer">
        <button class="btn btn-secondary" @click="$emit('close')">取消</button>
        <button class="btn btn-primary" @click="handleConfirm" :disabled="!locationKeyword">
          使用此地点
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, defineComponent, ref, watch } from 'vue'

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
    const locationKeyword = ref('')
    const copyMessage = ref('')

    const encodedLocation = computed(() => encodeURIComponent(locationKeyword.value || ''))
    const baiduMapUrl = computed(() => `https://map.baidu.com/search/${encodedLocation.value}`)
    const amapUrl = computed(() => `https://www.amap.com/search?query=${encodedLocation.value}`)

    const copyLocation = async () => {
      if (!locationKeyword.value) return

      try {
        await navigator.clipboard.writeText(locationKeyword.value)
        copyMessage.value = '已复制地点名称'
      } catch (error) {
        copyMessage.value = '复制失败，请手动复制'
      }

      window.setTimeout(() => {
        copyMessage.value = ''
      }, 2000)
    }

    const openIfReady = (url) => {
      if (!locationKeyword.value) return
      window.open(url, '_blank', 'noopener,noreferrer')
    }

    const handleConfirm = () => {
      if (!locationKeyword.value) return

      emit('select', {
        name: locationKeyword.value,
        lat: null,
        lng: null
      })
      emit('close')
    }

    watch(() => props.show, (newVal) => {
      if (newVal) {
        locationKeyword.value = props.defaultLocation || ''
        copyMessage.value = ''
      }
    })

    return {
      locationKeyword,
      copyMessage,
      baiduMapUrl,
      amapUrl,
      copyLocation,
      openIfReady,
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
  background: #fff;
  border-radius: 8px;
  width: 100%;
  max-width: 560px;
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
  background: var(--roamio-primary);
  color: #fff;
  border-radius: 8px 8px 0 0;
}

.map-header h6 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.btn-close {
  background: #fff;
  border: none;
  color: var(--roamio-primary);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.map-body {
  padding: 20px;
}

.map-unavailable {
  border: 1px dashed #c8d1dc;
  border-radius: 8px;
  background: #f8fafc;
  padding: 20px;
  text-align: center;
  margin-bottom: 18px;
}

.map-unavailable-icon {
  color: var(--roamio-primary);
  font-size: 32px;
  line-height: 1;
  margin-bottom: 8px;
}

.map-unavailable h6 {
  margin: 0 0 6px;
  font-weight: 700;
  color: #2c3e50;
}

.map-unavailable p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.map-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.map-actions .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  white-space: nowrap;
}

.map-actions .disabled {
  pointer-events: none;
  opacity: 0.65;
}

.copy-message {
  margin-top: 12px;
  color: #198754;
  font-size: 14px;
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

@media (max-width: 768px) {
  .map-picker-container {
    max-width: 100%;
  }

  .map-actions {
    grid-template-columns: 1fr;
  }
}
</style>
