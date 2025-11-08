# 🗺️ Roamio v2.0 技术实施方案

> **版本**: v2.0.0  
> **日期**: 2025-11-08  
> **状态**: 规划中 🚧

---

## 📋 目录

- [1. 项目概述](#1-项目概述)
- [2. 架构设计](#2-架构设计)
- [3. 数据模型设计](#3-数据模型设计)
- [4. 技术实施路线](#4-技术实施路线)
- [5. 关键技术点](#5-关键技术点)
- [6. 风险评估](#6-风险评估)
- [7. 实施时间表](#7-实施时间表)

---

## 1. 项目概述

### 1.1 核心目标

**将 Roamio 从"旅行展示平台"升级为"智能旅行助手"**

- ✅ 用户可在旅行详情中创建待办事件
- ✅ 支持地点选择、时间设定、提醒功能
- ✅ 与 Ralendar 深度融合，实现日历同步
- ✅ 支持本地事项（游客）与云端事项（登录用户）

### 1.2 技术亮点

| 特性 | 说明 |
|------|------|
| **微服务架构** | Roamio + Ralendar 独立部署，API 互通 |
| **双轨制设计** | 本地事项（localStorage）+ 云端事项（数据库） |
| **渐进式增强** | 游客可用基础功能，登录后解锁全部能力 |
| **地图集成** | 百度地图 SDK，支持选点、导航 |
| **统一账号** | QQ 登录 UnionID 或内部 UID 绑定 |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                            │
├─────────────────────────────────────────────────────────────┤
│  Roamio 前端 (Vue 3)                                         │
│  ├── 旅行详情页                                              │
│  ├── 添加事件表单 (EventForm.vue)                           │
│  ├── 本地事项栏 (LocalEvents.vue)                           │
│  ├── 云端事项栏 (CloudEvents.vue)                           │
│  └── 地图选点组件 (BaiduMapPicker.vue)                      │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Roamio API    │ │ Ralendar API│ │  百度地图   │
│  (Django)      │ │ (Django)    │ │  API        │
├────────────────┤ ├─────────────┤ ├─────────────┤
│ • Trip CRUD    │ │ • Event CRUD│ │ • 地点搜索  │
│ • Event CRUD   │ │ • Reminder  │ │ • 坐标转换  │
│ • User Auth    │ │ • Calendar  │ │ • 路径规划  │
└────────────────┘ └─────────────┘ └─────────────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  PostgreSQL     │
        │  (共享数据库)    │
        ├─────────────────┤
        │ • auth_user     │
        │ • trips_trip    │
        │ • trips_event   │
        │ • ralendar_event│
        └─────────────────┘
```

### 2.2 数据流设计

#### **场景 1: 游客创建本地事项**

```
用户（未登录）
    ↓
填写事件表单（标题、时间、地点）
    ↓
点击"保存到本地"
    ↓
localStorage.setItem('roamio_local_events', JSON.stringify(events))
    ↓
显示在"本地事项栏"
```

#### **场景 2: 登录用户创建云端事项**

```
用户（已登录）
    ↓
填写事件表单 + 设置提醒
    ↓
POST /api/v1/trips/{trip_id}/events/
    ↓
Roamio 后端保存到 trips_event 表
    ↓
如果设置了提醒：
    POST /ralendar/api/v1/events/  (跨项目调用)
    ↓
Ralendar 保存到 ralendar_event 表，设置提醒任务
    ↓
显示在"云端事项栏"
```

#### **场景 3: 本地事项转移到云端**

```
用户点击"拉到云端"
    ↓
检查登录状态
    ↓
POST /api/v1/trips/{trip_id}/events/
    body: { ...localEvent, source: 'local_migration' }
    ↓
保存成功后：
    - 从 localStorage 删除
    - 添加到云端事项栏
    - 可选：同步到 Ralendar
```

---

## 3. 数据模型设计

### 3.1 Roamio Event 模型

```python
# trips/models/event.py

from django.db import models
from django.contrib.auth.models import User
from .trip import Trip

class TripEvent(models.Model):
    """旅行事件模型"""
    
    # 基础字段
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='events')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_events')
    title = models.CharField(max_length=200, verbose_name='事件标题')
    description = models.TextField(blank=True, verbose_name='事件描述')
    
    # 时间字段
    event_time = models.DateTimeField(null=True, blank=True, verbose_name='事件时间')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 地点字段
    location_name = models.CharField(max_length=200, blank=True, verbose_name='地点名称')
    location_address = models.CharField(max_length=500, blank=True, verbose_name='详细地址')
    location_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='纬度')
    location_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='经度')
    
    # 提醒字段
    reminder_enabled = models.BooleanField(default=False, verbose_name='启用提醒')
    reminder_time = models.DateTimeField(null=True, blank=True, verbose_name='提醒时间')
    reminder_method = models.CharField(
        max_length=20, 
        choices=[('email', '邮件'), ('system', '系统通知')],
        default='email',
        verbose_name='提醒方式'
    )
    
    # 来源标记（用于生态融合）
    source_app = models.CharField(
        max_length=50, 
        default='roamio',
        verbose_name='来源应用'
    )
    source_id = models.CharField(max_length=100, blank=True, verbose_name='来源ID')
    
    # Ralendar 同步
    synced_to_ralendar = models.BooleanField(default=False, verbose_name='已同步到Ralendar')
    ralendar_event_id = models.IntegerField(null=True, blank=True, verbose_name='Ralendar事件ID')
    
    # 状态
    is_completed = models.BooleanField(default=False, verbose_name='已完成')
    is_deleted = models.BooleanField(default=False, verbose_name='已删除')
    
    class Meta:
        db_table = 'trips_event'
        ordering = ['-created_at']
        verbose_name = '旅行事件'
        verbose_name_plural = '旅行事件'
        indexes = [
            models.Index(fields=['trip', 'user']),
            models.Index(fields=['event_time']),
            models.Index(fields=['ralendar_event_id']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.trip.title}"
```

### 3.2 Ralendar Event 模型（需要新增字段）

```python
# ralendar/models/event.py

class Event(models.Model):
    """日历事件模型"""
    
    # ... 原有字段 ...
    
    # 新增：来源标记
    source_app = models.CharField(
        max_length=50, 
        default='ralendar',
        choices=[
            ('ralendar', 'Ralendar'),
            ('roamio', 'Roamio'),
            ('rote', 'Rote'),
        ],
        verbose_name='来源应用'
    )
    source_id = models.CharField(max_length=100, blank=True, verbose_name='来源ID')
    
    # 新增：关联旅行（如果来自 Roamio）
    roamio_trip_id = models.IntegerField(null=True, blank=True, verbose_name='关联旅行ID')
```

### 3.3 本地事项数据结构（localStorage）

```javascript
// 存储在 localStorage 中的数据结构
const localEvents = [
  {
    id: 'local_1699999999999', // 本地 ID（时间戳）
    tripId: 123,
    title: '参观故宫',
    description: '上午9点到达',
    eventTime: '2025-12-01T09:00:00',
    location: {
      name: '故宫博物院',
      address: '北京市东城区景山前街4号',
      lat: 39.916527,
      lng: 116.397026
    },
    reminder: {
      enabled: false,
      time: null,
      method: 'email'
    },
    createdAt: '2025-11-08T10:00:00',
    source: 'local'
  }
]
```

---

## 4. 技术实施路线

### 阶段 1: 基础架构（1-2 周）

#### 1.1 数据库迁移

```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate
```

#### 1.2 API 端点设计

```python
# trips/api/viewsets/event_viewset.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class TripEventViewSet(viewsets.ModelViewSet):
    """旅行事件 API"""
    
    serializer_class = TripEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        trip_id = self.kwargs.get('trip_pk')
        return TripEvent.objects.filter(
            trip_id=trip_id,
            is_deleted=False
        )
    
    def perform_create(self, serializer):
        trip_id = self.kwargs.get('trip_pk')
        event = serializer.save(
            user=self.request.user,
            trip_id=trip_id
        )
        
        # 如果启用提醒，同步到 Ralendar
        if event.reminder_enabled and event.synced_to_ralendar:
            self._sync_to_ralendar(event)
    
    def _sync_to_ralendar(self, event):
        """同步事件到 Ralendar"""
        # TODO: 实现跨项目 API 调用
        pass
    
    @action(detail=True, methods=['post'])
    def sync_to_ralendar(self, request, trip_pk=None, pk=None):
        """手动同步到 Ralendar"""
        event = self.get_object()
        # TODO: 实现同步逻辑
        return Response({'status': 'synced'})
    
    @action(detail=False, methods=['post'])
    def batch_create_from_local(self, request, trip_pk=None):
        """批量导入本地事项"""
        local_events = request.data.get('events', [])
        created_events = []
        
        for event_data in local_events:
            serializer = self.get_serializer(data=event_data)
            if serializer.is_valid():
                event = serializer.save(
                    user=request.user,
                    trip_id=trip_pk,
                    source_app='roamio',
                    source_id=event_data.get('id', '')
                )
                created_events.append(event)
        
        return Response({
            'count': len(created_events),
            'events': TripEventSerializer(created_events, many=True).data
        })
```

#### 1.3 URL 配置

```python
# trips/urls/api_urls.py

from rest_framework_nested import routers
from trips.api.viewsets.event_viewset import TripEventViewSet

router = routers.DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')

trips_router = routers.NestedDefaultRouter(router, r'trips', lookup='trip')
trips_router.register(r'events', TripEventViewSet, basename='trip-events')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(trips_router.urls)),
]
```

---

### 阶段 2: 前端组件开发（2-3 周）

#### 2.1 添加事件表单组件

```vue
<!-- web/src/components/events/EventForm.vue -->

<template>
  <div class="event-form">
    <h5>{{ isEdit ? '编辑事件' : '添加事件' }}</h5>
    
    <!-- 标题（必填） -->
    <div class="mb-3">
      <label class="form-label">事件标题 *</label>
      <input 
        v-model="form.title" 
        type="text" 
        class="form-control"
        placeholder="例如：参观故宫"
        required
      />
    </div>
    
    <!-- 描述（选填） -->
    <div class="mb-3">
      <label class="form-label">事件描述</label>
      <textarea 
        v-model="form.description" 
        class="form-control"
        rows="3"
        placeholder="添加更多细节..."
      ></textarea>
    </div>
    
    <!-- 时间选择（选填） -->
    <div class="mb-3">
      <label class="form-label">事件时间</label>
      <input 
        v-model="form.eventTime" 
        type="datetime-local" 
        class="form-control"
      />
    </div>
    
    <!-- 地点选择（选填） -->
    <div class="mb-3">
      <label class="form-label">地点</label>
      <div class="input-group">
        <input 
          v-model="form.location.name" 
          type="text" 
          class="form-control"
          placeholder="点击地图选择或直接输入"
          readonly
        />
        <button 
          class="btn btn-outline-secondary" 
          type="button"
          @click="showMapPicker = true"
        >
          <i class="bi bi-geo-alt"></i> 选择
        </button>
      </div>
    </div>
    
    <!-- 提醒设置（选填，需登录） -->
    <div v-if="isLoggedIn" class="mb-3">
      <div class="form-check form-switch">
        <input 
          v-model="form.reminder.enabled" 
          class="form-check-input" 
          type="checkbox"
          id="reminderSwitch"
        />
        <label class="form-check-label" for="reminderSwitch">
          启用提醒
        </label>
      </div>
      
      <div v-if="form.reminder.enabled" class="mt-2">
        <label class="form-label">提醒时间</label>
        <input 
          v-model="form.reminder.time" 
          type="datetime-local" 
          class="form-control"
        />
        
        <label class="form-label mt-2">提醒方式</label>
        <select v-model="form.reminder.method" class="form-select">
          <option value="email">邮件提醒</option>
          <option value="system">系统通知</option>
        </select>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="d-flex gap-2">
      <button 
        v-if="!isLoggedIn" 
        @click="saveToLocal" 
        class="btn btn-primary"
        :disabled="!form.title"
      >
        <i class="bi bi-save"></i> 保存到本地
      </button>
      
      <button 
        v-if="isLoggedIn" 
        @click="saveToCloud" 
        class="btn btn-success"
        :disabled="!form.title"
      >
        <i class="bi bi-cloud-upload"></i> 保存到云端
      </button>
      
      <button 
        @click="$emit('cancel')" 
        class="btn btn-secondary"
      >
        取消
      </button>
    </div>
    
    <!-- 地图选点弹窗 -->
    <BaiduMapPicker 
      v-if="showMapPicker"
      :show="showMapPicker"
      @select="handleLocationSelect"
      @close="showMapPicker = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import BaiduMapPicker from './BaiduMapPicker.vue'

const props = defineProps({
  tripId: {
    type: Number,
    required: true
  },
  event: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'cancel'])

const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)
const isEdit = computed(() => !!props.event)

const showMapPicker = ref(false)

const form = ref({
  title: props.event?.title || '',
  description: props.event?.description || '',
  eventTime: props.event?.eventTime || '',
  location: {
    name: props.event?.location?.name || '',
    address: props.event?.location?.address || '',
    lat: props.event?.location?.lat || null,
    lng: props.event?.location?.lng || null
  },
  reminder: {
    enabled: props.event?.reminder?.enabled || false,
    time: props.event?.reminder?.time || '',
    method: props.event?.reminder?.method || 'email'
  }
})

const handleLocationSelect = (location) => {
  form.value.location = location
  showMapPicker.value = false
}

const saveToLocal = () => {
  const localEvent = {
    id: `local_${Date.now()}`,
    tripId: props.tripId,
    ...form.value,
    createdAt: new Date().toISOString(),
    source: 'local'
  }
  
  // 保存到 localStorage
  const existingEvents = JSON.parse(localStorage.getItem('roamio_local_events') || '[]')
  existingEvents.push(localEvent)
  localStorage.setItem('roamio_local_events', JSON.stringify(existingEvents))
  
  emit('save', localEvent)
}

const saveToCloud = async () => {
  // TODO: 调用 API
  emit('save', form.value)
}
</script>
```

#### 2.2 百度地图选点组件

```vue
<!-- web/src/components/events/BaiduMapPicker.vue -->

<template>
  <div v-if="show" class="map-picker-modal">
    <div class="modal-backdrop" @click="$emit('close')"></div>
    <div class="modal-content">
      <div class="modal-header">
        <h5>选择地点</h5>
        <button @click="$emit('close')" class="btn-close"></button>
      </div>
      
      <div class="modal-body">
        <!-- 搜索框 -->
        <div class="search-box mb-3">
          <input 
            v-model="searchKeyword"
            type="text"
            class="form-control"
            placeholder="搜索地点..."
            @keyup.enter="searchLocation"
          />
          <button @click="searchLocation" class="btn btn-primary">
            <i class="bi bi-search"></i>
          </button>
        </div>
        
        <!-- 地图容器 -->
        <div id="baidu-map" style="height: 400px;"></div>
        
        <!-- 选中的地点信息 -->
        <div v-if="selectedLocation" class="selected-location mt-3">
          <h6>{{ selectedLocation.name }}</h6>
          <p class="text-muted">{{ selectedLocation.address }}</p>
          <small>经纬度: {{ selectedLocation.lat }}, {{ selectedLocation.lng }}</small>
        </div>
      </div>
      
      <div class="modal-footer">
        <button 
          @click="confirmSelection" 
          class="btn btn-success"
          :disabled="!selectedLocation"
        >
          确认选择
        </button>
        <button @click="$emit('close')" class="btn btn-secondary">
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  initialLocation: Object
})

const emit = defineEmits(['select', 'close'])

const searchKeyword = ref('')
const selectedLocation = ref(null)
let map = null
let marker = null

onMounted(() => {
  if (props.show) {
    initMap()
  }
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    setTimeout(initMap, 100) // 等待 DOM 渲染
  }
})

const initMap = () => {
  // 初始化百度地图
  const BMap = window.BMap
  map = new BMap.Map('baidu-map')
  
  // 设置初始中心点（默认北京天安门）
  const point = new BMap.Point(116.404, 39.915)
  map.centerAndZoom(point, 15)
  map.enableScrollWheelZoom(true)
  
  // 添加点击事件
  map.addEventListener('click', (e) => {
    const pt = e.point
    getLocationInfo(pt.lng, pt.lat)
  })
  
  // 如果有初始位置，显示标记
  if (props.initialLocation) {
    const { lat, lng } = props.initialLocation
    const initPoint = new BMap.Point(lng, lat)
    map.centerAndZoom(initPoint, 15)
    addMarker(initPoint)
  }
}

const addMarker = (point) => {
  if (marker) {
    map.removeOverlay(marker)
  }
  
  const BMap = window.BMap
  marker = new BMap.Marker(point)
  map.addOverlay(marker)
  map.panTo(point)
}

const getLocationInfo = (lng, lat) => {
  const BMap = window.BMap
  const point = new BMap.Point(lng, lat)
  const geocoder = new BMap.Geocoder()
  
  geocoder.getLocation(point, (result) => {
    if (result) {
      selectedLocation.value = {
        name: result.addressComponents.street || result.business || '未知地点',
        address: result.address,
        lat: lat,
        lng: lng
      }
      addMarker(point)
    }
  })
}

const searchLocation = () => {
  if (!searchKeyword.value) return
  
  const BMap = window.BMap
  const localSearch = new BMap.LocalSearch(map, {
    onSearchComplete: (results) => {
      if (localSearch.getStatus() === 0) {
        const poi = results.getPoi(0)
        const point = poi.point
        getLocationInfo(point.lng, point.lat)
      }
    }
  })
  
  localSearch.search(searchKeyword.value)
}

const confirmSelection = () => {
  if (selectedLocation.value) {
    emit('select', selectedLocation.value)
  }
}
</script>

<style scoped>
.map-picker-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: auto;
  z-index: 1051;
}

.search-box {
  display: flex;
  gap: 8px;
}

.selected-location {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}
</style>
```

#### 2.3 双轨制事项栏组件

```vue
<!-- web/src/components/events/EventsSidebar.vue -->

<template>
  <div class="events-sidebar">
    <div class="sidebar-header">
      <h5>事项管理</h5>
      <button @click="showEventForm = true" class="btn btn-sm btn-primary">
        <i class="bi bi-plus-lg"></i> 添加事项
      </button>
    </div>
    
    <div class="sidebar-body">
      <!-- 本地事项栏 -->
      <div class="events-section">
        <div class="section-header">
          <h6>
            <i class="bi bi-laptop"></i> 本地事项
            <span class="badge bg-secondary">{{ localEvents.length }}</span>
          </h6>
        </div>
        
        <div class="events-list">
          <EventItem 
            v-for="event in localEvents"
            :key="event.id"
            :event="event"
            :is-local="true"
            @edit="handleEdit"
            @delete="handleDelete"
            @move-to-cloud="handleMoveToCloud"
          />
          
          <div v-if="localEvents.length === 0" class="empty-state">
            <p class="text-muted">暂无本地事项</p>
          </div>
        </div>
      </div>
      
      <!-- 云端事项栏 -->
      <div v-if="isLoggedIn" class="events-section">
        <div class="section-header">
          <h6>
            <i class="bi bi-cloud"></i> 云端事项
            <span class="badge bg-primary">{{ cloudEvents.length }}</span>
          </h6>
        </div>
        
        <div class="events-list">
          <EventItem 
            v-for="event in cloudEvents"
            :key="event.id"
            :event="event"
            :is-local="false"
            @edit="handleEdit"
            @delete="handleDelete"
            @move-to-local="handleMoveToLocal"
          />
          
          <div v-if="cloudEvents.length === 0" class="empty-state">
            <p class="text-muted">暂无云端事项</p>
          </div>
        </div>
      </div>
      
      <!-- 未登录提示 -->
      <div v-else class="login-prompt">
        <p class="text-muted">登录后可使用云端事项</p>
        <button @click="goToLogin" class="btn btn-sm btn-outline-primary">
          立即登录
        </button>
      </div>
    </div>
    
    <!-- 添加事件表单 -->
    <EventForm 
      v-if="showEventForm"
      :trip-id="tripId"
      :event="editingEvent"
      @save="handleSave"
      @cancel="showEventForm = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import EventForm from './EventForm.vue'
import EventItem from './EventItem.vue'

const props = defineProps({
  tripId: {
    type: Number,
    required: true
  }
})

const userStore = useUserStore()
const router = useRouter()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const showEventForm = ref(false)
const editingEvent = ref(null)
const localEvents = ref([])
const cloudEvents = ref([])

onMounted(() => {
  loadLocalEvents()
  if (isLoggedIn.value) {
    loadCloudEvents()
  }
})

const loadLocalEvents = () => {
  const stored = localStorage.getItem('roamio_local_events')
  if (stored) {
    const allEvents = JSON.parse(stored)
    localEvents.value = allEvents.filter(e => e.tripId === props.tripId)
  }
}

const loadCloudEvents = async () => {
  // TODO: 调用 API 加载云端事项
}

const handleSave = (event) => {
  showEventForm.value = false
  editingEvent.value = null
  
  // 刷新列表
  loadLocalEvents()
  if (isLoggedIn.value) {
    loadCloudEvents()
  }
}

const handleEdit = (event) => {
  editingEvent.value = event
  showEventForm.value = true
}

const handleDelete = (event) => {
  if (confirm('确定要删除这个事项吗？')) {
    if (event.source === 'local') {
      // 从 localStorage 删除
      const stored = JSON.parse(localStorage.getItem('roamio_local_events') || '[]')
      const filtered = stored.filter(e => e.id !== event.id)
      localStorage.setItem('roamio_local_events', JSON.stringify(filtered))
      loadLocalEvents()
    } else {
      // TODO: 调用 API 删除云端事项
    }
  }
}

const handleMoveToCloud = async (event) => {
  if (!isLoggedIn.value) {
    alert('请先登录')
    return
  }
  
  // TODO: 调用 API 将本地事项转移到云端
  // 成功后从 localStorage 删除
}

const handleMoveToLocal = (event) => {
  // TODO: 将云端事项复制到本地
}

const goToLogin = () => {
  router.push('/auth/login')
}
</script>

<style scoped>
.events-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.sidebar-header {
  padding: 16px;
  background: white;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.events-section {
  margin-bottom: 24px;
}

.section-header {
  margin-bottom: 12px;
}

.section-header h6 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 24px;
}

.login-prompt {
  text-align: center;
  padding: 24px;
  background: white;
  border-radius: 8px;
}
</style>
```

---

### 阶段 3: 百度地图集成（1 周）

#### 3.1 申请百度地图 AK

1. 访问 [百度地图开放平台](https://lbsyun.baidu.com/)
2. 注册开发者账号
3. 创建应用，获取 AK（Access Key）
4. 设置域名白名单（如 `roamio.com`, `localhost:8080`）

#### 3.2 引入百度地图 SDK

```html
<!-- web/public/index.html -->

<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <!-- ... -->
  
  <!-- 百度地图 API -->
  <script 
    type="text/javascript" 
    src="https://api.map.baidu.com/api?v=3.0&ak=YOUR_BAIDU_MAP_AK"
  ></script>
</head>
<body>
  <!-- ... -->
</body>
</html>
```

#### 3.3 配置环境变量

```javascript
// web/.env.local

VUE_APP_BAIDU_MAP_AK=你的百度地图AK
```

---

### 阶段 4: Roamio ↔ Ralendar 数据同步（2 周）

#### 4.1 统一账号体系

**方案选择：内部 UID 绑定**（推荐）

```python
# trips/models/user_profile.py

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 统一 UID（生态系统内部唯一标识）
    ecosystem_uid = models.CharField(max_length=100, unique=True, verbose_name='生态UID')
    
    # QQ 登录信息
    qq_openid = models.CharField(max_length=100, blank=True, unique=True)
    qq_unionid = models.CharField(max_length=100, blank=True)
    
    # ... 其他字段 ...
```

**登录时绑定逻辑**：

```python
# trips/views/auth/qq_login.py

def qq_login_callback(request):
    # 获取 QQ openid
    openid = get_qq_openid(request)
    
    # 查找或创建用户
    try:
        profile = UserProfile.objects.get(qq_openid=openid)
        user = profile.user
    except UserProfile.DoesNotExist:
        # 创建新用户
        user = User.objects.create(username=f'qq_{openid[:8]}')
        profile = UserProfile.objects.create(
            user=user,
            qq_openid=openid,
            ecosystem_uid=f'roamio_{user.id}_{int(time.time())}'  # 生成唯一 UID
        )
    
    # 生成 JWT Token
    token = generate_jwt_token(user)
    
    return JsonResponse({
        'token': token,
        'ecosystem_uid': profile.ecosystem_uid,
        'user': UserSerializer(user).data
    })
```

#### 4.2 跨项目 API 调用

```python
# trips/utils/ralendar_sync.py

import requests
from django.conf import settings

class RalendarSyncService:
    """Ralendar 同步服务"""
    
    def __init__(self):
        self.base_url = settings.RALENDAR_API_URL  # 'https://ralendar.com/api/v1'
        self.api_key = settings.RALENDAR_API_KEY
    
    def create_event(self, trip_event):
        """在 Ralendar 中创建事件"""
        url = f'{self.base_url}/events/'
        
        data = {
            'title': trip_event.title,
            'description': trip_event.description,
            'start_time': trip_event.event_time.isoformat() if trip_event.event_time else None,
            'location': {
                'name': trip_event.location_name,
                'address': trip_event.location_address,
                'lat': float(trip_event.location_lat) if trip_event.location_lat else None,
                'lng': float(trip_event.location_lng) if trip_event.location_lng else None,
            },
            'reminder_enabled': trip_event.reminder_enabled,
            'reminder_time': trip_event.reminder_time.isoformat() if trip_event.reminder_time else None,
            'reminder_method': trip_event.reminder_method,
            'source_app': 'roamio',
            'source_id': str(trip_event.id),
            'roamio_trip_id': trip_event.trip_id,
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # 更新 Roamio 事件的同步状态
            trip_event.synced_to_ralendar = True
            trip_event.ralendar_event_id = result.get('id')
            trip_event.save()
            
            return result
        except requests.exceptions.RequestException as e:
            print(f'同步到 Ralendar 失败: {e}')
            return None
    
    def update_event(self, trip_event):
        """更新 Ralendar 中的事件"""
        if not trip_event.ralendar_event_id:
            return None
        
        url = f'{self.base_url}/events/{trip_event.ralendar_event_id}/'
        # TODO: 实现更新逻辑
    
    def delete_event(self, trip_event):
        """删除 Ralendar 中的事件"""
        if not trip_event.ralendar_event_id:
            return None
        
        url = f'{self.base_url}/events/{trip_event.ralendar_event_id}/'
        # TODO: 实现删除逻辑
```

#### 4.3 配置 Ralendar API

```python
# roamio/settings.py

# Ralendar 集成配置
RALENDAR_API_URL = os.getenv('RALENDAR_API_URL', 'http://localhost:8001/api/v1')
RALENDAR_API_KEY = os.getenv('RALENDAR_API_KEY', 'your-api-key')
```

---

## 5. 关键技术点

### 5.1 百度地图 API 配额

| 服务 | 免费配额 | 说明 |
|------|---------|------|
| 地图展示 | 50,000次/天 | 足够初期使用 |
| 地点搜索 | 10,000次/天 | 足够初期使用 |
| 路径规划 | 1,000次/天 | 需要控制使用频率 |
| 地理编码 | 10,000次/天 | 坐标 ↔ 地址转换 |

**优化建议**：
- ✅ 缓存常用地点信息
- ✅ 限制用户搜索频率
- ✅ 使用防抖（debounce）减少请求

### 5.2 本地存储策略

```javascript
// web/src/utils/localEventStorage.js

export class LocalEventStorage {
  static KEY = 'roamio_local_events'
  
  // 获取所有本地事项
  static getAll() {
    const stored = localStorage.getItem(this.KEY)
    return stored ? JSON.parse(stored) : []
  }
  
  // 获取指定旅行的事项
  static getByTripId(tripId) {
    return this.getAll().filter(e => e.tripId === tripId)
  }
  
  // 添加事项
  static add(event) {
    const events = this.getAll()
    events.push({
      ...event,
      id: `local_${Date.now()}`,
      createdAt: new Date().toISOString(),
      source: 'local'
    })
    localStorage.setItem(this.KEY, JSON.stringify(events))
  }
  
  // 更新事项
  static update(eventId, updates) {
    const events = this.getAll()
    const index = events.findIndex(e => e.id === eventId)
    if (index !== -1) {
      events[index] = { ...events[index], ...updates }
      localStorage.setItem(this.KEY, JSON.stringify(events))
    }
  }
  
  // 删除事项
  static delete(eventId) {
    const events = this.getAll().filter(e => e.id !== eventId)
    localStorage.setItem(this.KEY, JSON.stringify(events))
  }
  
  // 批量转移到云端后清理
  static deleteByIds(eventIds) {
    const events = this.getAll().filter(e => !eventIds.includes(e.id))
    localStorage.setItem(this.KEY, JSON.stringify(events))
  }
  
  // 获取存储大小（KB）
  static getStorageSize() {
    const stored = localStorage.getItem(this.KEY) || ''
    return (new Blob([stored]).size / 1024).toFixed(2)
  }
}
```

### 5.3 JWT Token 共享

**关键点**：Roamio 和 Ralendar 必须使用相同的 `SECRET_KEY`

```python
# roamio/settings.py 和 ralendar/settings.py

# 统一的密钥（生产环境从环境变量读取）
SECRET_KEY = os.getenv('ECOSYSTEM_SECRET_KEY', 'roamio-ecosystem-unified-2025')

# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'SIGNING_KEY': SECRET_KEY,  # 使用统一密钥
    'ALGORITHM': 'HS256',
}
```

**这样生成的 Token 可以在两个项目间互通！**

---

## 6. 风险评估

### 6.1 技术风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| 百度地图 API 配额不足 | 中 | 低 | 实现缓存、限流；准备备用方案（高德地图） |
| 跨项目 API 调用失败 | 高 | 中 | 实现重试机制、降级方案（仅保存本地） |
| localStorage 容量限制 | 低 | 低 | 限制本地事项数量（最多50条），提示用户转移到云端 |
| Ralendar 未完成开发 | 高 | 中 | 先实现 Roamio 端功能，预留接口，后续对接 |

### 6.2 用户体验风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 本地事项丢失（清除浏览器数据） | 中 | 明确提示用户，引导转移到云端 |
| 地图加载慢 | 低 | 添加加载动画，支持直接输入地址 |
| 提醒不及时 | 中 | 使用可靠的邮件服务（腾讯云 SES） |

---

## 7. 实施时间表

### 第 1-2 周：基础架构

- [x] 设计数据模型
- [ ] 创建数据库迁移
- [ ] 实现基础 API（CRUD）
- [ ] 编写 API 文档

### 第 3-4 周：前端组件

- [ ] 开发事件表单组件
- [ ] 实现本地存储逻辑
- [ ] 开发双轨制界面
- [ ] 集成到旅行详情页

### 第 5 周：地图集成

- [ ] 申请百度地图 AK
- [ ] 开发地图选点组件
- [ ] 实现导航跳转
- [ ] 测试地图功能

### 第 6-7 周：生态融合

- [ ] 统一账号体系
- [ ] 实现跨项目 API 调用
- [ ] 开发同步服务
- [ ] 实现提醒功能

### 第 8 周：测试与优化

- [ ] 功能测试
- [ ] 性能优化
- [ ] 用户体验优化
- [ ] 文档完善

---

## 8. 后续迭代方向

### v2.1: 协同功能

- [ ] 邀请好友加入旅行计划
- [ ] 共享事项编辑
- [ ] 实时协同更新

### v2.2: 智能推荐

- [ ] 根据旅行目的地推荐景点
- [ ] 智能生成行程安排
- [ ] 天气提醒

### v2.3: 社交功能

- [ ] 旅行合集订阅
- [ ] 事项模板分享
- [ ] 旅行社区

---

## 📚 参考资料

- [百度地图开放平台文档](https://lbsyun.baidu.com/index.php?title=jspopularGL)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue 3 组合式 API](https://cn.vuejs.org/guide/introduction.html)
- [JWT 认证](https://jwt.io/)

---

**文档版本**: v1.0  
**最后更新**: 2025-11-08  
**维护者**: Roamio 开发团队

