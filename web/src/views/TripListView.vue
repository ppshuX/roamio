<template>
  <div class="trip-list-container">
    <!-- 导航栏 -->
    <NavBar />
    
    <!-- 主标题 -->
    <div class="main-header">
      <h1 class="title">旅行树</h1>
    </div>
    
    <!-- 欢迎语 -->
    <div class="welcome">
      欢迎来到旅行计划与交流平台！<br>
      发现精彩行程，记录美好旅途，和朋友一起分享旅行故事。
    </div>
    
    <!-- Loading状态 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
    
    <!-- 藤蔓式布局 -->
    <div v-else class="vine-container">
      <!-- 中间的藤蔓线 -->
      <div class="vine-line"></div>
      
      <!-- 原始果实：前5个（厦门、三岔湖、曲靖、昆明、长沙） -->
      <div
        v-for="(trip, index) in originalTrips"
        :key="trip.slug"
        :class="['fruit', `fruit-${index + 1}`]"
        @click="goToDetail(trip.slug)"
      >
        <span class="icon">{{ getIcon(index) }}</span>
        <div class="info">
          <div class="trip-title">{{ trip.name }}</div>
          <div class="desc">{{ trip.description }}</div>
          <div class="stats">
            <span class="stat-item">👁️ {{ trip.stats.views }}</span>
            <span class="stat-item">❤️ {{ trip.stats.likes }}</span>
            <span class="stat-item">💬 {{ trip.stats.comments_count }}</span>
          </div>
        </div>
      </div>
      
      <!-- 新增的果实：时间较晚的放在最下面，按左右交错 -->
      <div
        v-for="(trip, index) in newTrips"
        :key="trip.slug"
        :class="['fruit', `fruit-${5 + index + 1}`]"
        @click="goToDetail(trip.slug)"
      >
        <span class="icon">{{ getIcon(index + 5) }}</span>
        <div class="info">
          <div class="trip-title">{{ trip.name }}</div>
          <div class="desc">{{ trip.description }}</div>
          <div class="stats">
            <span class="stat-item">👁️ {{ trip.stats.views }}</span>
            <span class="stat-item">❤️ {{ trip.stats.likes }}</span>
            <span class="stat-item">💬 {{ trip.stats.comments_count }}</span>
          </div>
        </div>
      </div>
      
      <!-- 敬请期待（作为最后一个果实，与newTrips一起循环） -->
      <div class="fruit fruit-coming-soon" style="pointer-events: none;" :class="`fruit-${trips.length + 1}`">
        <span class="icon">⏳</span>
        <div class="info">
          <div class="trip-title">敬请期待</div>
          <div class="desc">更多精彩行程即将上线，欢迎持续关注！</div>
          <div class="date">Coming soon...</div>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <div class="footer">
      &copy; 2025 旅行计划平台 | 旅行社区<br>
      技术支持：Vue 3 + Django REST Framework
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getTripList, getTripStats, getTripPlanStats } from '@/api/trip'
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'TripListView',
  
  components: {
    NavBar
  },
  
  setup() {
    const router = useRouter()
    const trips = ref([])
    const loading = ref(true)
    let statsTimer = null
    
    const fetchTrips = async () => {
      loading.value = true
      try {
        const data = await getTripList()
        trips.value = data.results || data || []
      } catch (error) {
        console.error('获取旅行大厅失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const goToDetail = (slug) => {
      router.push(`/trip/${slug}/`)
    }
    
    // 根据索引返回不同的图标
    const getIcon = (index) => {
      const icons = ['🏖️', '🌊', '🏙️', '🌄', '🌇']
      return icons[index] || '🗺️'
    }
    
    // 将trips分成原始（前5个）和新数据
    const originalTrips = computed(() => trips.value.slice(0, 5))
    const newTrips = computed(() => trips.value.slice(5))
    
    const refreshStats = async () => {
      if (!trips.value?.length) return
      try {
        const updated = await Promise.all(
          trips.value.map(async (t) => {
            try {
              // 优先新接口（tp: 前缀），失败再回退旧接口，确保与详情页一致
              let stat
              try {
                stat = await getTripPlanStats(t.slug)
              } catch (e1) {
                stat = await getTripStats(t.slug)
              }
              return { ...t, stats: { ...t.stats, ...stat } }
            } catch (e) {
              return t
            }
          })
        )
        trips.value = updated
      } catch (e) {
        // ignore
      }
    }

    onMounted(() => {
      fetchTrips().then(() => {
        // 首次加载后刷新一次统计并开启轮询（云端接口）
        refreshStats()
        statsTimer = setInterval(refreshStats, 15000)
      })
    })

    onBeforeUnmount(() => {
      if (statsTimer) clearInterval(statsTimer)
    })
    
    return {
      trips,
      originalTrips,
      newTrips,
      loading,
      goToDetail,
      getIcon
    }
  }
}
</script>

<style scoped>
.trip-list-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0e7ff 0%, #f0f4f8 100%);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  padding-bottom: 40px;
}

/* 主标题 */
.main-header {
  text-align: center;
  margin-top: 36px;
  margin-bottom: 10px;
}

.main-header .title {
  font-size: 2.1rem;
  color: #2366b4;
  font-weight: bold;
  letter-spacing: 2px;
  margin: 0;
}

/* 欢迎语 */
.welcome {
  text-align: center;
  color: #234;
  font-size: 1.08rem;
  margin-bottom: 40px;
  line-height: 1.6;
}

/* 藤蔓容器 */
.vine-container {
  position: relative;
  width: 100%;
  max-width: 520px;
  margin: 0 auto 40px auto;
  min-height: 1400px;
  padding-bottom: 150px;
}

/* 中间的藤蔓线 */
.vine-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 6px;
  background: linear-gradient(to bottom, #7ec850 0%, #2366b4 100%);
  border-radius: 3px;
  z-index: 0;
  transform: translateX(-50%);
}

/* 旅行卡片（果实） */
.fruit {
  position: absolute;
  left: 50%;
  width: 320px;
  max-width: 95vw;
  background: #fff;
  border-radius: 50px;
  box-shadow: 0 4px 24px rgba(35, 102, 180, 0.10);
  padding: 1.7rem 1.5rem 1.5rem 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 1.3rem;
  transition: all 0.18s ease;
  cursor: pointer;
  z-index: 1;
}

.fruit:hover {
  box-shadow: 0 12px 36px rgba(35, 102, 180, 0.22);
  transform: scale(1.08) translateY(-6px);
  background: linear-gradient(90deg, #f0f8ff 0%, #e0e7ff 100%);
}

.fruit .icon {
  font-size: 2.5rem;
  flex-shrink: 0;
  transition: transform 0.18s;
}

.fruit:hover .icon {
  transform: rotate(10deg);
}

.fruit .info {
  flex: 1;
  min-width: 0;
}

.fruit .trip-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  transition: color 0.18s;
}

.fruit:hover .trip-title {
  color: #2366b4;
}

.fruit .desc {
  font-size: 0.95rem;
  color: #666;
  line-height: 1.5;
  margin-bottom: 0.7rem;
  transition: color 0.18s;
  /* 超长简介显示省略号 */
  display: -webkit-box;
  -webkit-line-clamp: 3; /* 最多显示三行 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fruit:hover .desc {
  color: #2c3e50;
}

.fruit .stats {
  display: flex;
  gap: 0.8rem;
  font-size: 0.9rem;
}

.fruit .stat-item {
  color: #888;
  transition: color 0.18s;
}

.fruit:hover .stat-item {
  color: #2366b4;
}

.fruit .date {
  font-size: 0.9rem;
  color: #aaa;
  margin-top: 0.5rem;
  display: block;
}

/* 电脑端：左右交错布局 - 间隔减小 */
.fruit-1 {
  top: 30px;
  transform: translate(-120%, 0);
}

.fruit-2 {
  top: 160px;
  transform: translate(20%, 0);
}

.fruit-3 {
  top: 290px;
  transform: translate(-120%, 0);
}

.fruit-4 {
  top: 420px;
  transform: translate(20%, 0);
}

.fruit-5 {
  top: 550px;
  transform: translate(-120%, 0);
}

.fruit-6 {
  top: 680px;
  transform: translate(20%, 0);
}

.fruit-7 {
  top: 810px;
  transform: translate(-120%, 0);
}

.fruit-8 {
  top: 940px;
  transform: translate(20%, 0);
}

.fruit-9 {
  top: 1070px;
  transform: translate(-120%, 0);
}

.fruit-10 {
  top: 1200px;
  transform: translate(20%, 0);
}

/* 敬请期待位置动态调整 */
.fruit-coming-soon {
  background: #f8f8ff;
  opacity: 0.7;
}

/* Hover时的位置调整 */
.fruit-1:hover,
.fruit-3:hover,
.fruit-5:hover,
.fruit-7:hover,
.fruit-9:hover {
  transform: translate(-120%, -6px) scale(1.08);
}

.fruit-2:hover,
.fruit-4:hover,
.fruit-6:hover,
.fruit-8:hover,
.fruit-10:hover {
  transform: translate(20%, -6px) scale(1.08);
}

/* 页脚 */
.footer {
  text-align: center;
  color: #aaa;
  font-size: 0.98rem;
  margin-top: 60px;
  padding-bottom: 18px;
  line-height: 1.8;
}

/* 响应式设计 - 移动端 */
@media (max-width: 600px) {
  .main-header .title {
    font-size: 1.5rem;
  }

  .welcome {
    font-size: 1rem;
    padding: 0 20px;
  }

  .vine-container {
    min-height: 1000px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 32px;
    box-shadow: 0 4px 24px rgba(35, 102, 180, 0.08);
    padding: 20px 10px;
  }

  .fruit {
    left: 50%;
    width: calc(100% - 20px);
    max-width: calc(100% - 20px);
    padding: 1.4rem 1.2rem;
    margin-bottom: 10px;
    transition: all 0.25s ease;
  }

  /* 移动端：上下堆叠 */
  .fruit {
    position: relative !important;
    left: 50% !important;
    margin-bottom: 20px !important;
  }
  
  .fruit-1,
  .fruit-2,
  .fruit-3,
  .fruit-4,
  .fruit-5,
  .fruit-6,
  .fruit-7,
  .fruit-8,
  .fruit-9,
  .fruit-10,
  .fruit-coming-soon {
    top: auto !important;
    transform: translate(-50%, 0) !important;
    margin-bottom: 25px !important;
  }
  
  .fruit-coming-soon {
    margin-top: 10px !important;
  }

  .fruit:hover {
    transform: translate(-50%, -8px) scale(1.03) !important;
    box-shadow: 0 6px 30px rgba(35, 102, 180, 0.18) !important;
    background: linear-gradient(90deg, #f8fbff 0%, #f0f4ff 100%) !important;
  }

  .fruit .icon {
    font-size: 2rem;
    transition: transform 0.25s ease;
  }
  
  .fruit:hover .icon {
    transform: scale(1.1) rotate(5deg);
  }

  .fruit .trip-title {
    font-size: 1.05rem;
    transition: color 0.25s ease;
  }
  
  .fruit:hover .trip-title {
    color: #2366b4;
  }

  .fruit .desc {
    font-size: 0.9rem;
    transition: color 0.25s ease;
    /* 移动端可再压缩为两行 */
    -webkit-line-clamp: 2;
  }
  
  .fruit:hover .desc {
    color: #2c3e50;
  }

  .footer {
    font-size: 0.85rem;
    margin-top: 30px;
  }
}
</style>

