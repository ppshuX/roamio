/**
 * 本地事项存储工具类
 * 
 * 用于管理存储在 localStorage 中的旅行事项
 * 支持游客在未登录状态下创建和管理事项
 * 
 * 数据结构：
 * {
 *   id: 'local_1699999999999',  // 本地 ID（时间戳）
 *   tripId: 123,                 // 关联的旅行 ID
 *   title: '参观故宫',           // 事项标题
 *   description: '上午9点到达',  // 事项描述
 *   eventTime: '2025-12-01T09:00:00',  // 事件时间
 *   location: {                  // 地点信息
 *     name: '故宫博物院',
 *     address: '北京市东城区景山前街4号',
 *     lat: 39.916527,
 *     lng: 116.397026
 *   },
 *   reminder: {                  // 提醒信息
 *     enabled: false,
 *     time: null,
 *     method: 'email'
 *   },
 *   createdAt: '2025-11-08T10:00:00',  // 创建时间
 *   source: 'local'              // 来源标记
 * }
 */

export class LocalEventStorage {
  // localStorage 键名
  static KEY = 'roamio_local_events'
  
  /**
   * 获取所有本地事项
   * @returns {Array} 事项数组
   */
  static getAll() {
    try {
      const stored = localStorage.getItem(this.KEY)
      return stored ? JSON.parse(stored) : []
    } catch (error) {
      console.error('读取本地事项失败:', error)
      return []
    }
  }
  
  /**
   * 获取指定旅行的事项
   * @param {Number} tripId - 旅行 ID
   * @returns {Array} 事项数组
   */
  static getByTripId(tripId) {
    const allEvents = this.getAll()
    return allEvents.filter(event => event.tripId === tripId)
  }
  
  /**
   * 添加事项
   * @param {Object} event - 事项数据
   * @returns {Object} 添加后的事项（包含生成的 ID）
   */
  static add(event) {
    try {
      const events = this.getAll()
      
      // 生成唯一 ID
      const newEvent = {
        ...event,
        id: `local_${Date.now()}`,
        createdAt: new Date().toISOString(),
        source: 'local'
      }
      
      events.push(newEvent)
      localStorage.setItem(this.KEY, JSON.stringify(events))
      
      return newEvent
    } catch (error) {
      console.error('添加本地事项失败:', error)
      throw error
    }
  }
  
  /**
   * 更新事项
   * @param {String} eventId - 事项 ID
   * @param {Object} updates - 要更新的字段
   * @returns {Object|null} 更新后的事项，如果未找到则返回 null
   */
  static update(eventId, updates) {
    try {
      const events = this.getAll()
      const index = events.findIndex(e => e.id === eventId)
      
      if (index === -1) {
        console.warn(`未找到 ID 为 ${eventId} 的事项`)
        return null
      }
      
      // 更新事项
      events[index] = {
        ...events[index],
        ...updates,
        updatedAt: new Date().toISOString()
      }
      
      localStorage.setItem(this.KEY, JSON.stringify(events))
      
      return events[index]
    } catch (error) {
      console.error('更新本地事项失败:', error)
      throw error
    }
  }
  
  /**
   * 删除事项
   * @param {String} eventId - 事项 ID
   * @returns {Boolean} 是否删除成功
   */
  static delete(eventId) {
    try {
      const events = this.getAll()
      const filtered = events.filter(e => e.id !== eventId)
      
      if (filtered.length === events.length) {
        console.warn(`未找到 ID 为 ${eventId} 的事项`)
        return false
      }
      
      localStorage.setItem(this.KEY, JSON.stringify(filtered))
      return true
    } catch (error) {
      console.error('删除本地事项失败:', error)
      throw error
    }
  }
  
  /**
   * 批量删除事项（用于转移到云端后清理）
   * @param {Array<String>} eventIds - 事项 ID 数组
   * @returns {Number} 删除的数量
   */
  static deleteByIds(eventIds) {
    try {
      const events = this.getAll()
      const filtered = events.filter(e => !eventIds.includes(e.id))
      const deletedCount = events.length - filtered.length
      
      localStorage.setItem(this.KEY, JSON.stringify(filtered))
      
      return deletedCount
    } catch (error) {
      console.error('批量删除本地事项失败:', error)
      throw error
    }
  }
  
  /**
   * 清空所有本地事项
   * @returns {Boolean} 是否清空成功
   */
  static clear() {
    try {
      localStorage.removeItem(this.KEY)
      return true
    } catch (error) {
      console.error('清空本地事项失败:', error)
      throw error
    }
  }
  
  /**
   * 获取存储大小（KB）
   * @returns {String} 存储大小，格式化为字符串
   */
  static getStorageSize() {
    try {
      const stored = localStorage.getItem(this.KEY) || ''
      const sizeInBytes = new Blob([stored]).size
      const sizeInKB = (sizeInBytes / 1024).toFixed(2)
      return `${sizeInKB} KB`
    } catch (error) {
      console.error('获取存储大小失败:', error)
      return '0 KB'
    }
  }
  
  /**
   * 获取事项数量统计
   * @returns {Object} 统计信息
   */
  static getStats() {
    try {
      const events = this.getAll()
      
      // 按旅行分组统计
      const byTrip = events.reduce((acc, event) => {
        acc[event.tripId] = (acc[event.tripId] || 0) + 1
        return acc
      }, {})
      
      return {
        total: events.length,
        byTrip,
        storageSize: this.getStorageSize()
      }
    } catch (error) {
      console.error('获取统计信息失败:', error)
      return {
        total: 0,
        byTrip: {},
        storageSize: '0 KB'
      }
    }
  }
  
  /**
   * 检查存储是否可用
   * @returns {Boolean} 是否可用
   */
  static isAvailable() {
    try {
      const testKey = '__roamio_test__'
      localStorage.setItem(testKey, 'test')
      localStorage.removeItem(testKey)
      return true
    } catch (error) {
      console.error('localStorage 不可用:', error)
      return false
    }
  }
  
  /**
   * 导出所有本地事项（用于备份）
   * @returns {String} JSON 字符串
   */
  static export() {
    try {
      const events = this.getAll()
      return JSON.stringify(events, null, 2)
    } catch (error) {
      console.error('导出本地事项失败:', error)
      throw error
    }
  }
  
  /**
   * 导入本地事项（用于恢复）
   * @param {String} jsonString - JSON 字符串
   * @returns {Number} 导入的数量
   */
  static import(jsonString) {
    try {
      const events = JSON.parse(jsonString)
      
      if (!Array.isArray(events)) {
        throw new Error('导入数据格式错误：必须是数组')
      }
      
      // 合并现有事项（避免重复）
      const existingEvents = this.getAll()
      const existingIds = new Set(existingEvents.map(e => e.id))
      
      const newEvents = events.filter(e => !existingIds.has(e.id))
      const merged = [...existingEvents, ...newEvents]
      
      localStorage.setItem(this.KEY, JSON.stringify(merged))
      
      return newEvents.length
    } catch (error) {
      console.error('导入本地事项失败:', error)
      throw error
    }
  }
}

// 默认导出
export default LocalEventStorage


