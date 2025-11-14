/**
 * 将已保存的行程数据转换为 Ralendar 事件格式
 * 用于从编辑页面或详情页面同步到 Ralendar
 */

// 使用原生 Date 和简单的日期处理，避免依赖 moment-timezone
// import moment from 'moment-timezone'

/**
 * 解析时间字符串（支持多种格式）
 * @param {string} timeStr - 时间字符串，如 "09:00", "09:00-12:00", "上午9点" 等
 * @returns {Object} { start: "HH:MM", end: "HH:MM" } 或 null
 */
function parseTimeRange(timeStr) {
    if (!timeStr || typeof timeStr !== 'string') {
        return { start: '09:00', end: '11:00' } // 默认时间
    }

    // 格式1: "09:00-12:00" 或 "09:00 - 12:00"
    const rangeMatch = timeStr.match(/(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})/)
    if (rangeMatch) {
        const startHour = String(parseInt(rangeMatch[1], 10)).padStart(2, '0')
        const startMin = rangeMatch[2]
        const endHour = String(parseInt(rangeMatch[3], 10)).padStart(2, '0')
        const endMin = rangeMatch[4]
        return {
            start: `${startHour}:${startMin}`,
            end: `${endHour}:${endMin}`
        }
    }

    // 格式2: "09:00" 单个时间
    const singleMatch = timeStr.match(/(\d{1,2}):(\d{2})/)
    if (singleMatch) {
        const hour = String(parseInt(singleMatch[1], 10)).padStart(2, '0')
        const min = singleMatch[2]
        const startTime = `${hour}:${min}`
        // 默认持续2小时
        const endHour = (parseInt(hour, 10) + 2) % 24
        const endTime = `${String(endHour).padStart(2, '0')}:${min}`
        return { start: startTime, end: endTime }
    }

    // 默认时间
    return { start: '09:00', end: '11:00' }
}

/**
 * 从行程内容中提取地点信息
 * @param {string} content - 行程内容文本
 * @returns {Object} { location: string, description: string }
 */
function extractLocationFromContent(content) {
    if (!content) {
        return { location: '未指定地点', description: '' }
    }

    // 尝试提取地点（通常在时间后面，如 "09:00 - 故宫博物院"）
    const lines = content.split('\n').filter(line => line.trim())

    // 查找包含地点的行
    for (const line of lines) {
        // 匹配格式: "时间 - 地点" 或 "地点: 描述"
        const locationMatch = line.match(/(?:^|\d{1,2}:\d{2}\s*[-~]\s*)([^：:：\n]+?)(?:[：:：]|$)/)
        if (locationMatch) {
            const location = locationMatch[1].trim()
            if (location && location.length > 1 && location.length < 50) {
                return {
                    location: location,
                    description: content.replace(line, '').trim() || content
                }
            }
        }
    }

    // 如果没有找到，使用第一行作为地点
    if (lines.length > 0) {
        const firstLine = lines[0].trim()
        // 移除时间部分
        const location = firstLine.replace(/\d{1,2}:\d{2}\s*[-~]\s*/, '').trim()
        return {
            location: location || '未指定地点',
            description: lines.slice(1).join('\n') || firstLine
        }
    }

    return { location: '未指定地点', description: content }
}

/**
 * 将行程数据转换为 Ralendar 事件数组
 * @param {Object} tripData - 行程数据
 * @returns {Array} Ralendar 事件数组
 */
export function convertTripToRalendarEvents(tripData) {
    if (!tripData || !tripData.overview || !tripData.overview.itinerary) {
        throw new Error('行程数据格式不正确：缺少 itinerary 数据')
    }

    const events = []
    const itinerary = tripData.overview.itinerary

    if (!Array.isArray(itinerary) || itinerary.length === 0) {
        throw new Error('行程数据为空：itinerary 数组为空')
    }

    // 获取开始日期
    let startDate = null
    if (tripData.start_date) {
        // 处理各种日期格式
        let dateStr = tripData.start_date
        if (dateStr.includes('T')) {
            dateStr = dateStr.split('T')[0]
        }
        startDate = new Date(dateStr + 'T00:00:00+08:00')
    } else {
        // 如果没有开始日期，使用今天
        startDate = new Date()
        startDate.setHours(0, 0, 0, 0)
    }

    if (isNaN(startDate.getTime())) {
        throw new Error('开始日期无效，请先设置行程的开始日期')
    }

    const tripTitle = tripData.title || tripData.name || '旅行'

    // 遍历每一天的行程
    itinerary.forEach((day, dayIndex) => {
        if (!day || !day.day) {
            return // 跳过无效的天数
        }

        // 计算当前天的日期
        const currentDate = new Date(startDate)
        currentDate.setDate(startDate.getDate() + dayIndex)
        const year = currentDate.getFullYear()
        const month = currentDate.getMonth()
        const dayNum = currentDate.getDate()

        // 解析时间范围
        const timeRange = parseTimeRange(day.time)

        // 提取地点和描述
        const { location, description } = extractLocationFromContent(day.content || day.highlight || '')

        // 构建开始和结束时间（UTC+8）
        const [startHour, startMin] = timeRange.start.split(':').map(Number)
        const [endHour, endMin] = timeRange.end.split(':').map(Number)

        // 创建 UTC+8 时间的 Date 对象（使用 UTC 方法并减去8小时偏移）
        // 例如：2025-11-15 09:00 UTC+8 = 2025-11-15 01:00 UTC
        const startTimeUTC = new Date(Date.UTC(year, month, dayNum, startHour - 8, startMin, 0, 0))
        const endTimeUTC = new Date(Date.UTC(year, month, dayNum, endHour - 8, endMin, 0, 0))

        if (isNaN(startTimeUTC.getTime()) || isNaN(endTimeUTC.getTime())) {
            console.warn(`第 ${dayIndex + 1} 天时间无效，跳过`)
            return
        }

        // 构建事件标题
        let eventTitle = tripTitle
        const dayTitle = day.day.replace(/^第\d+天[：:：]?\s*/, '').trim()
        if (dayTitle) {
            eventTitle += ` - ${dayTitle}`
        }
        if (location && location !== '未指定地点') {
            eventTitle += `: ${location}`
        }

        // 限制标题长度
        if (eventTitle.length > 50) {
            eventTitle = eventTitle.substring(0, 47) + '...'
        }

        // 格式化时间为 ISO 8601 格式（UTC+8）
        // 将 UTC 时间转换为 UTC+8 格式的 ISO 字符串
        const formatISOWithOffset = (utcDate) => {
            const iso = utcDate.toISOString()
            // 将 UTC 时间标识符 Z 替换为 +08:00（表示 UTC+8）
            return iso.replace('Z', '+08:00')
        }

        // 构建事件对象
        const event = {
            title: eventTitle,
            description: description || day.content || day.highlight || '',
            start_time: formatISOWithOffset(startTimeUTC),
            end_time: formatISOWithOffset(endTimeUTC),
            location: location || '未指定地点',
            location_name: location || '未指定地点',
            location_address: null, // 已保存的行程可能没有详细地址
            location_type: null, // 已保存的行程可能没有地点类型
            reminder_minutes: 30, // 默认提前30分钟提醒
            email_reminder: true
        }

        events.push(event)
    })

    if (events.length === 0) {
        throw new Error('无法从行程数据中提取任何事件，请检查行程内容')
    }

    return events
}

/**
 * 验证事件数据
 * @param {Array} events - 事件数组
 * @returns {Object} { valid: Array, invalid: Array }
 */
export function validateTripEvents(events) {
    const valid = []
    const invalid = []

    events.forEach((event, index) => {
        const startTime = new Date(event.start_time)
        const endTime = new Date(event.end_time)

        const isValid = event.title &&
            event.start_time &&
            !isNaN(startTime.getTime()) &&
            event.end_time &&
            !isNaN(endTime.getTime()) &&
            endTime >= startTime &&
            event.location

        if (isValid) {
            valid.push(event)
        } else {
            invalid.push({ index, event, reason: '缺少必填字段或时间无效' })
        }
    })

    return { valid, invalid }
}

