/**
 * AI 行程转 Ralendar 事件转换工具
 * 
 * 将 AI 生成的旅行计划数据转换为 Ralendar 日历事件格式
 */

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
 * 将日期和时间组合为 ISO 8601 格式
 * @param {string} date - 日期字符串 (YYYY-MM-DD)
 * @param {string} time - 时间字符串 (HH:MM)
 * @returns {string} - ISO 8601 格式的时间字符串
 */
function combineDateTime(date, time) {
  if (!date || !time) {
    throw new Error('日期和时间不能为空')
  }
  
  // 确保时间格式正确 (HH:MM)
  const timeMatch = time.match(/(\d{1,2}):(\d{2})/)
  if (!timeMatch) {
    // 如果没有匹配到时间，使用默认时间 09:00
    time = '09:00'
  } else {
    // 确保两位数格式
    const hours = timeMatch[1].padStart(2, '0')
    const minutes = timeMatch[2].padStart(2, '0')
    time = `${hours}:${minutes}`
  }
  
  // 组合日期和时间，使用中国时区 (UTC+8)
  // 格式: YYYY-MM-DDTHH:MM:00+08:00
  const isoString = `${date}T${time}:00+08:00`
  
  return isoString
}

/**
 * 将 AI 生成的行程转换为 Ralendar 事件数组
 * 
 * @param {Object} aiPlan - AI 生成的行程数据
 * @param {string} tripTitle - 旅行标题
 * @param {string} startDate - 开始日期 (YYYY-MM-DD)，可选
 * @returns {Array} Ralendar 事件数组
 */
export function convertAITripToEvents(aiPlan, tripTitle = '', startDate = null) {
  if (!aiPlan || !aiPlan.days_detail || !Array.isArray(aiPlan.days_detail)) {
    throw new Error('AI 行程数据格式不正确')
  }
  
  const events = []
  
  // 遍历每一天的行程
  aiPlan.days_detail.forEach((day, dayIndex) => {
    const dayDate = startDate 
      ? (() => {
          // 如果提供了开始日期，从开始日期计算
          const start = new Date(startDate)
          const current = new Date(start)
          current.setDate(start.getDate() + dayIndex)
          return current.toISOString().split('T')[0]
        })()
      : (day.date || null)
    
    if (!dayDate) {
      console.warn(`第 ${dayIndex + 1} 天缺少日期，跳过`)
      return
    }
    
    const dayTitle = day.title || `Day ${day.day_number || dayIndex + 1}`
    
    // 遍历当天的活动
    if (day.activities && Array.isArray(day.activities)) {
      day.activities.forEach((activity, activityIndex) => {
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
          const startDateObj = new Date(startTime)
          const endDateObj = new Date(startDateObj.getTime() + duration * 60 * 60 * 1000)
          const endTime = endDateObj.toISOString().replace('Z', '+08:00')
          
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
          
          // 构建事件对象
          const event = {
            title: eventTitle,
            description: description.trim(),
            start_time: startTime,
            end_time: endTime,
            location: activity.location || '未指定地点',
            reminder_minutes: 30, // 固定提前 30 分钟提醒
            email_reminder: true // 启用邮件提醒
          }
          
          // 如果有坐标，添加坐标信息
          if (latitude && longitude) {
            event.latitude = parseFloat(latitude)
            event.longitude = parseFloat(longitude)
          }
          
          events.push(event)
          
        } catch (error) {
          console.error(`转换活动失败 (Day ${dayIndex + 1}, Activity ${activityIndex + 1}):`, error)
          // 继续处理下一个活动，不中断整个转换过程
        }
      })
    }
    
    // 如果没有活动但有日期，创建一个默认事件（可选）
    // 这里先不创建，只处理有活动的行程
  })
  
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

