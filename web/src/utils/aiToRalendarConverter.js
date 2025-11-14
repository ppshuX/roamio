/**
 * AI 行程转 Ralendar 事件转换工具
 * 
 * 将 AI 生成的旅行计划数据转换为 Ralendar 日历事件格式
 */

import { geocode } from './mapService'

/**
 * 解析持续时间字符串（如 "2小时"、"3.5小时"、"120分钟"）
 * @param {string} duration - 持续时间字符串
 * @returns {number} - 小时数（浮点数）
 */
function parseDuration(duration) {
  if (!duration) return 2 // 默认 2 小时
  
  // 匹配 "X小时" 或 "X.5小时"
  const hourMatch = duration.match(/(\d+\.?\d*)\s*小时/)
  if (hourMatch) {
    return parseFloat(hourMatch[1])
  }
  
  // 匹配 "X分钟"
  const minuteMatch = duration.match(/(\d+)\s*分钟/)
  if (minuteMatch) {
    return parseFloat(minuteMatch[1]) / 60
  }
  
  // 默认返回 2 小时
  return 2
}

/**
 * 验证日期格式 (YYYY-MM-DD)
 * @param {string} date - 日期字符串
 * @returns {boolean} - 是否有效
 */
function isValidDate(date) {
  if (!date || typeof date !== 'string') return false
  
  // 排除占位符
  if (date === 'YYYY-MM-DD') return false
  
  // 验证格式：YYYY-MM-DD
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!dateRegex.test(date)) return false
  
  // 解析日期
  const [year, month, day] = date.split('-').map(Number)
  
  // 验证范围
  if (year < 1900 || year > 2100) return false
  if (month < 1 || month > 12) return false
  if (day < 1 || day > 31) return false
  
  // 创建日期对象验证（使用本地时区）
  const dateObj = new Date(year, month - 1, day)
  
  // 验证日期对象是否有效
  if (isNaN(dateObj.getTime())) return false
  
  // 验证日期是否正确（防止无效日期如 2月30日）
  if (dateObj.getFullYear() !== year || 
      dateObj.getMonth() !== month - 1 || 
      dateObj.getDate() !== day) {
    return false
  }
  
  return true
}

/**
 * 将日期和时间组合为 ISO 8601 格式
 * @param {string} date - 日期字符串 (YYYY-MM-DD)
 * @param {string} time - 时间字符串 (HH:MM)
 * @returns {string} - ISO 8601 格式的时间字符串
 */
function combineDateTime(date, time) {
  if (!date || !time) {
    throw new Error('日期和时间不能为空')
  }
  
  // 验证日期格式
  if (!isValidDate(date)) {
    throw new Error(`无效的日期格式: ${date}，期望格式: YYYY-MM-DD`)
  }
  
  // 确保时间格式正确 (HH:MM)
  let normalizedTime = time
  const timeMatch = time.match(/(\d{1,2}):(\d{2})/)
  if (!timeMatch) {
    // 如果没有匹配到时间，使用默认时间 09:00
    normalizedTime = '09:00'
  } else {
    // 确保两位数格式并验证范围
    const hours = parseInt(timeMatch[1], 10)
    const minutes = parseInt(timeMatch[2], 10)
    
    if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
      throw new Error(`无效的时间值: ${time}，小时应在 0-23，分钟应在 0-59`)
    }
    
    normalizedTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
  }
  
  // 解析日期和时间
  const [year, month, day] = date.split('-').map(Number)
  const [hours, mins] = normalizedTime.split(':').map(Number)
  
  // 验证日期范围
  if (month < 1 || month > 12 || day < 1 || day > 31) {
    throw new Error(`无效的日期: ${date}`)
  }
  
  // 直接使用 UTC+8 时间，不需要转换
  // Ralendar API 期望的是 UTC+8 时区的时间字符串
  // 格式：YYYY-MM-DDTHH:MM:SS+08:00
  
  // 验证日期对象
  const dateObj = new Date(year, month - 1, day, hours, mins, 0, 0)
  if (isNaN(dateObj.getTime())) {
    throw new Error(`无效的日期时间: ${date} ${normalizedTime}`)
  }
  
  // 直接格式化为 UTC+8 格式的 ISO 字符串
  const yearStr = String(year).padStart(4, '0')
  const monthStr = String(month).padStart(2, '0')
  const dayStr = String(day).padStart(2, '0')
  const hoursStr = String(hours).padStart(2, '0')
  const minsStr = String(mins).padStart(2, '0')
  
  const isoStringWithOffset = `${yearStr}-${monthStr}-${dayStr}T${hoursStr}:${minsStr}:00+08:00`
  
  // 再次验证生成的字符串可以被正确解析
  const testDate = new Date(isoStringWithOffset)
  if (isNaN(testDate.getTime())) {
    throw new Error(`生成的日期时间无效: ${isoStringWithOffset}`)
  }
  
  return isoStringWithOffset
}

/**
 * 将 AI 生成的行程转换为 Ralendar 事件数组
 * 
 * @param {Object} aiPlan - AI 生成的行程数据
 * @param {string} tripTitle - 旅行标题
 * @param {string} startDate - 开始日期 (YYYY-MM-DD)，可选
 * @returns {Array} Ralendar 事件数组
 */
export async function convertAITripToEvents(aiPlan, tripTitle = '', startDate = null) {
  if (!aiPlan || !aiPlan.days_detail || !Array.isArray(aiPlan.days_detail)) {
    throw new Error('AI 行程数据格式不正确')
  }
  
  const events = []
  let usedStartDate = null
  const warnings = []
  
  // 检查并处理开始日期
  let finalStartDate = null
  
  // 1. 检查传入的 startDate（如果提供）
  if (startDate && isValidDate(startDate)) {
    finalStartDate = startDate
  }
  
  // 2. 如果没有有效日期，尝试从第一天的日期获取
  if (!finalStartDate && aiPlan.days_detail && aiPlan.days_detail.length > 0) {
    const firstDay = aiPlan.days_detail[0]
    if (firstDay.date) {
      // 处理各种日期格式
      let dateStr = firstDay.date
      
      // 如果是 ISO 格式，提取日期部分
      if (dateStr.includes('T')) {
        dateStr = dateStr.split('T')[0]
      }
      
      // 如果是占位符，跳过
      if (dateStr !== 'YYYY-MM-DD' && isValidDate(dateStr)) {
        finalStartDate = dateStr
      }
    }
  }
  
  // 3. 如果仍然没有有效日期，使用今天作为默认值
  if (!finalStartDate) {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    finalStartDate = `${year}-${month}-${day}`
    
    // 验证生成的日期（应该总是有效的）
    if (!isValidDate(finalStartDate)) {
      throw new Error('无法生成有效的默认日期')
    }
    
    warnings.push(`未提供有效开始日期，使用今天（${finalStartDate}）作为默认开始日期`)
    console.info(`未提供有效开始日期，使用今天（${finalStartDate}）作为默认开始日期`)
  }
  
  // 最终验证（应该总是通过）
  if (!isValidDate(finalStartDate)) {
    throw new Error(`开始日期无效: ${finalStartDate}`)
  }
  
  usedStartDate = finalStartDate
  
  // 遍历每一天的行程
  for (let dayIndex = 0; dayIndex < aiPlan.days_detail.length; dayIndex++) {
    const day = aiPlan.days_detail[dayIndex]
    let dayDate = null
    
    // 计算日期（usedStartDate 应该已经在前面验证过，所以这里直接使用）
    try {
      // 解析开始日期
      const [year, month, dayNum] = usedStartDate.split('-').map(Number)
      const start = new Date(year, month - 1, dayNum)
      
      // 验证日期对象（双重检查）
      if (isNaN(start.getTime()) || 
          start.getFullYear() !== year || 
          start.getMonth() !== month - 1 || 
          start.getDate() !== dayNum) {
        warnings.push(`开始日期解析失败: ${usedStartDate}，跳过第 ${dayIndex + 1} 天`)
        console.warn(`开始日期解析失败: ${usedStartDate}，跳过第 ${dayIndex + 1} 天`)
        return
      }
      
      // 计算当前天的日期
      const current = new Date(start)
      current.setDate(start.getDate() + dayIndex)
      
      // 验证计算后的日期
      if (isNaN(current.getTime())) {
        warnings.push(`计算日期失败 (Day ${dayIndex + 1})，跳过`)
        console.warn(`计算日期失败 (Day ${dayIndex + 1})，跳过`)
        return
      }
      
      // 格式化为 YYYY-MM-DD
      const yearStr = current.getFullYear()
      const monthStr = String(current.getMonth() + 1).padStart(2, '0')
      const dayStr = String(current.getDate()).padStart(2, '0')
      dayDate = `${yearStr}-${monthStr}-${dayStr}`
      
    } catch (error) {
      warnings.push(`计算日期失败 (Day ${dayIndex + 1}): ${error.message}`)
      console.error(`计算日期失败 (Day ${dayIndex + 1}):`, error)
      return
    }
    
    // 如果仍然没有日期，尝试使用 day.date（备用方案）
    if (!dayDate && day.date) {
      // 使用 day.date，但需要验证格式
      const dateStr = day.date
      
      // 如果是完整的时间戳，提取日期部分
      if (dateStr.includes('T')) {
        dayDate = dateStr.split('T')[0]
      } else {
        dayDate = dateStr
      }
      
      // 验证日期格式
      if (!isValidDate(dayDate)) {
        warnings.push(`第 ${dayIndex + 1} 天日期格式无效: ${day.date}，跳过`)
        console.warn(`第 ${dayIndex + 1} 天日期格式无效: ${day.date}，跳过`)
        return
      }
    }
    
    if (!dayDate) {
      // 如果仍然没有日期，使用开始日期加天数
      if (usedStartDate && isValidDate(usedStartDate)) {
        try {
          const [year, month, dayNum] = usedStartDate.split('-').map(Number)
          const start = new Date(year, month - 1, dayNum)
          const current = new Date(start)
          current.setDate(start.getDate() + dayIndex)
          const yearStr = current.getFullYear()
          const monthStr = String(current.getMonth() + 1).padStart(2, '0')
          const dayStr = String(current.getDate()).padStart(2, '0')
          dayDate = `${yearStr}-${monthStr}-${dayStr}`
        } catch (error) {
          warnings.push(`第 ${dayIndex + 1} 天无法计算日期，跳过`)
          console.warn(`第 ${dayIndex + 1} 天无法计算日期，跳过`)
          return
        }
      } else {
        warnings.push(`第 ${dayIndex + 1} 天缺少日期且无法计算，跳过`)
        console.warn(`第 ${dayIndex + 1} 天缺少日期且无法计算，跳过`)
        return
      }
    }
    
    const dayTitle = day.title || `Day ${day.day_number || dayIndex + 1}`
    
    // 检查是否有活动
    if (!day.activities || !Array.isArray(day.activities) || day.activities.length === 0) {
      warnings.push(`第 ${dayIndex + 1} 天没有活动，跳过`)
      console.warn(`第 ${dayIndex + 1} 天没有活动，跳过`)
      return
    }
    
    // 遍历当天的活动
    for (let activityIndex = 0; activityIndex < day.activities.length; activityIndex++) {
      const activity = day.activities[activityIndex]
        try {
          // 构建事件标题: {trip_title} - {day_title}: {location}
          let eventTitle = `${tripTitle || aiPlan.trip_title || '旅行'}`.trim()
          if (dayTitle) {
            eventTitle += ` - ${dayTitle}`
          }
          if (activity.location) {
            eventTitle += `: ${activity.location}`
          }
          
          // 限制标题长度（50 字符）
          if (eventTitle.length > 50) {
            eventTitle = eventTitle.substring(0, 47) + '...'
          }
          
          // 获取开始时间
          const activityTime = activity.time || '09:00' // 默认 09:00
          const startTime = combineDateTime(dayDate, activityTime)
          
          // 计算结束时间
          const duration = parseDuration(activity.duration || '2小时')
          
          // 解析开始时间（UTC+8 格式）
          const startDateObj = new Date(startTime)
          if (isNaN(startDateObj.getTime())) {
            throw new Error(`无效的开始时间: ${startTime}`)
          }
          
          // 计算结束时间：直接在 UTC+8 时区计算
          // 从 startTime 字符串中提取日期和时间
          const startMatch = startTime.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):\d{2}\+08:00$/)
          if (!startMatch) {
            throw new Error(`开始时间格式错误: ${startTime}`)
          }
          
          const [, startYear, startMonth, startDay, startHour, startMin] = startMatch.map(Number)
          
          // 计算结束时间（小时和分钟）
          let endHour = startHour + Math.floor(duration)
          let endMin = startMin + Math.round((duration % 1) * 60)
          
          // 处理分钟进位
          if (endMin >= 60) {
            endHour += Math.floor(endMin / 60)
            endMin = endMin % 60
          }
          
          // 处理小时进位（跨天）
          let endYear = startYear
          let endMonth = startMonth
          let endDay = startDay
          
          if (endHour >= 24) {
            endDay += Math.floor(endHour / 24)
            endHour = endHour % 24
            
            // 处理跨月（简化处理，假设每月最多31天）
            const daysInMonth = new Date(startYear, startMonth, 0).getDate()
            if (endDay > daysInMonth) {
              endMonth += 1
              endDay = endDay - daysInMonth
              if (endMonth > 12) {
                endYear += 1
                endMonth = 1
              }
            }
          }
          
          // 格式化为 UTC+8 格式
          const endTime = `${String(endYear).padStart(4, '0')}-${String(endMonth).padStart(2, '0')}-${String(endDay).padStart(2, '0')}T${String(endHour).padStart(2, '0')}:${String(endMin).padStart(2, '0')}:00+08:00`
          
          // 构建事件描述
          let description = ''
          if (activity.description) {
            description = activity.description
          }
          if (activity.tips) {
            description += (description ? '\n\n' : '') + `💡 提示: ${activity.tips}`
          }
          if (activity.estimated_cost) {
            description += (description ? '\n\n' : '') + `💰 预估费用: ¥${activity.estimated_cost}`
          }
          if (!description) {
            description = '来自 Roamio AI 生成的行程'
          } else {
            description += '\n\n(来自 Roamio AI 生成的行程)'
          }
          
          // 提取地理坐标
          let latitude = null
          let longitude = null
          
          if (activity.coordinates) {
            latitude = activity.coordinates.lat || activity.coordinates.latitude
            longitude = activity.coordinates.lng || activity.coordinates.longitude
          }
          
          // 🌟 如果没有坐标但有地点，尝试自动获取坐标
          if (!latitude && !longitude && activity.location) {
            try {
              // 构建地址字符串（优先使用详细地址）
              const addressToGeocode = activity.address || activity.location
              
              // 调用地理编码 API（使用高德地图）
              const geoResult = await geocode(addressToGeocode)
              
              if (geoResult && geoResult.lat && geoResult.lng) {
                latitude = geoResult.lat
                longitude = geoResult.lng
                console.info(`✅ 自动获取坐标: ${activity.location} -> (${latitude}, ${longitude})`)
              }
            } catch (error) {
              // 地理编码失败，不影响事件创建，只记录日志
              console.warn(`⚠️ 无法获取坐标: ${activity.location}，错误: ${error.message}`)
            }
          }
          
          // 构建地点信息（优先使用详细地址，其次使用地点名称）
          let location = activity.location || '未指定地点'
          if (activity.address) {
            // 如果地址存在，组合地点名称和地址
            location = `${location}（${activity.address}）`
          }
          
          // 构建事件对象（确保字段符合 Ralendar API 要求）
          const event = {
            title: eventTitle.trim(), // 必填：标题
            description: description.trim(), // 可选：描述
            start_time: startTime, // 必填：开始时间（ISO 8601 with timezone）
            end_time: endTime, // 可选：结束时间（ISO 8601 with timezone）
            reminder_minutes: 30, // 可选：提醒时间（分钟）
            email_reminder: true // 可选：邮件提醒
          }
          
          // 地点处理：如果有有效地点，添加 location 字段
          // 注意：Ralendar API 只需要 location 字段，不需要 location_name、location_address 等
          if (location && location !== '未指定地点' && location.trim() !== '') {
            event.location = location.trim()
          }
          
          // 如果有坐标，添加坐标信息（Ralendar API 支持）
          if (latitude != null && longitude != null) {
            event.latitude = parseFloat(latitude)
            event.longitude = parseFloat(longitude)
          }
          
          events.push(event)
          
        } catch (error) {
          warnings.push(`转换活动失败 (Day ${dayIndex + 1}, Activity ${activityIndex + 1}): ${error.message}`)
          console.error(`转换活动失败 (Day ${dayIndex + 1}, Activity ${activityIndex + 1}):`, error, activity)
          // 继续处理下一个活动，不中断整个转换过程
        }
      }
  }
  
  // 如果有警告，记录到控制台
  if (warnings.length > 0) {
    console.warn('转换过程中的警告:', warnings)
  }
  
  // 如果没有生成任何事件，抛出详细错误
  if (events.length === 0) {
    const errorMsg = warnings.length > 0 
      ? `无法生成任何事件。警告：${warnings.join('; ')}`
      : '无法生成任何事件，请检查行程数据格式'
    throw new Error(errorMsg)
  }
  
  return events
}

/**
 * 验证事件数据格式
 * @param {Object} event - 事件对象
 * @returns {boolean} - 是否有效
 */
export function validateEvent(event) {
  const requiredFields = ['title', 'start_time', 'end_time', 'location']
  
  for (const field of requiredFields) {
    if (!event[field]) {
      console.error(`事件缺少必需字段: ${field}`, event)
      return false
    }
  }
  
  // 验证时间格式
  try {
    new Date(event.start_time)
    new Date(event.end_time)
  } catch (error) {
    console.error('事件时间格式错误:', error, event)
    return false
  }
  
  return true
}

/**
 * 验证事件数组
 * @param {Array} events - 事件数组
 * @returns {{valid: Array, invalid: Array}} - 有效和无效的事件数组
 */
export function validateEvents(events) {
  const valid = []
  const invalid = []
  
  events.forEach((event, index) => {
    if (validateEvent(event)) {
      valid.push(event)
    } else {
      invalid.push({ index, event, reason: '数据格式不正确' })
    }
  })
  
  return { valid, invalid }
}

