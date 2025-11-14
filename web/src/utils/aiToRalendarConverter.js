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
 * 验证日期格式 (YYYY-MM-DD)
 * @param {string} date - 日期字符串
 * @returns {boolean} - 是否有效
 */
function isValidDate(date) {
  if (!date || typeof date !== 'string') return false
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!dateRegex.test(date)) return false
  
  const dateObj = new Date(date + 'T00:00:00')
  return !isNaN(dateObj.getTime()) && dateObj.toISOString().startsWith(date)
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
  
  // 创建 UTC 时间（减去8小时偏移，因为我们要表示的是 UTC+8 时区的时间）
  // 例如：2025-11-15 09:00 UTC+8 = 2025-11-15 01:00 UTC
  const utcDate = new Date(Date.UTC(year, month - 1, day, hours - 8, mins, 0, 0))
  
  // 验证日期对象是否有效
  if (isNaN(utcDate.getTime())) {
    throw new Error(`无效的日期时间: ${date} ${normalizedTime}`)
  }
  
  // 格式化为 ISO 8601 字符串 (格式: YYYY-MM-DDTHH:MM:SSZ)
  const isoString = utcDate.toISOString()
  
  // 替换 UTC 时区标识符 Z 为 +08:00（表示 UTC+8）
  const isoStringWithOffset = isoString.replace('Z', '+08:00')
  
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
export function convertAITripToEvents(aiPlan, tripTitle = '', startDate = null) {
  if (!aiPlan || !aiPlan.days_detail || !Array.isArray(aiPlan.days_detail)) {
    throw new Error('AI 行程数据格式不正确')
  }
  
  const events = []
  let usedStartDate = null
  const warnings = []
  
  // 如果没有提供开始日期，尝试从第一天获取或使用今天
  if (!startDate && aiPlan.days_detail.length > 0) {
    const firstDay = aiPlan.days_detail[0]
    if (firstDay.date && isValidDate(firstDay.date.split('T')[0])) {
      startDate = firstDay.date.split('T')[0]
    } else {
      // 使用今天作为默认开始日期
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      startDate = `${year}-${month}-${day}`
      warnings.push('未提供开始日期，使用今天作为默认开始日期')
    }
  } else if (!startDate) {
    // 如果完全没有日期信息，使用今天
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    startDate = `${year}-${month}-${day}`
    warnings.push('未提供开始日期，使用今天作为默认开始日期')
  }
  
  usedStartDate = startDate
  
  // 遍历每一天的行程
  aiPlan.days_detail.forEach((day, dayIndex) => {
    let dayDate = null
    
    // 计算日期
    if (usedStartDate) {
      // 如果提供了开始日期，从开始日期计算
      try {
        // 验证开始日期格式
        if (!isValidDate(usedStartDate)) {
          warnings.push(`开始日期格式无效: ${usedStartDate}，跳过第 ${dayIndex + 1} 天`)
          console.warn(`开始日期格式无效: ${usedStartDate}，跳过第 ${dayIndex + 1} 天`)
          return
        }
        
        // 解析开始日期
        const [year, month, dayNum] = usedStartDate.split('-').map(Number)
        const start = new Date(year, month - 1, dayNum)
        
        if (isNaN(start.getTime())) {
          warnings.push(`开始日期无效: ${usedStartDate}，跳过第 ${dayIndex + 1} 天`)
          console.warn(`开始日期无效: ${usedStartDate}，跳过第 ${dayIndex + 1} 天`)
          return
        }
        
        // 计算当前天的日期
        const current = new Date(start)
        current.setDate(start.getDate() + dayIndex)
        
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
    } else if (day.date) {
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
          
          // 解析开始时间
          const startDateObj = new Date(startTime)
          if (isNaN(startDateObj.getTime())) {
            throw new Error(`无效的开始时间: ${startTime}`)
          }
          
          // 计算结束时间（毫秒）
          const endDateObj = new Date(startDateObj.getTime() + duration * 60 * 60 * 1000)
          
          if (isNaN(endDateObj.getTime())) {
            throw new Error(`无效的结束时间（开始时间: ${startTime}, 持续时间: ${duration}小时）`)
          }
          
          // 转换为 ISO 8601 格式（UTC+8）
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
          
          // 构建地点信息（优先使用详细地址，其次使用地点名称）
          let location = activity.location || '未指定地点'
          if (activity.address) {
            // 如果地址存在，组合地点名称和地址
            location = `${location}（${activity.address}）`
          }
          
          // 构建事件对象
          const event = {
            title: eventTitle,
            description: description.trim(),
            start_time: startTime,
            end_time: endTime,
            location: location, // 完整地点信息（名称+地址）
            location_name: activity.location || '未指定地点', // 地点名称
            location_address: activity.address || null, // 详细地址
            location_type: activity.location_type || null, // 地点类型
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
          warnings.push(`转换活动失败 (Day ${dayIndex + 1}, Activity ${activityIndex + 1}): ${error.message}`)
          console.error(`转换活动失败 (Day ${dayIndex + 1}, Activity ${activityIndex + 1}):`, error, activity)
          // 继续处理下一个活动，不中断整个转换过程
        }
      })
  })
  
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

