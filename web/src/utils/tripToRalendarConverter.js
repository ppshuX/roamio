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
        let location = null

        // 模式1: 匹配 "13:00-15:00 地点名称" 或 "13:00 - 地点名称" 格式
        // 先移除时间范围，然后提取后面的内容
        const timeRangePattern = /\d{1,2}:\d{2}\s*[-~至]\s*\d{1,2}:\d{2}/
        const singleTimePattern = /^\d{1,2}:\d{2}\s*[-~]\s*/

        if (timeRangePattern.test(line)) {
            // 移除时间范围（如 "13:00-15:00"）
            let cleanedLine = line.replace(timeRangePattern, '').trim()
            // 移除可能的箭头和分隔符
            cleanedLine = cleanedLine.replace(/^[→\s-~]+/, '').trim()

            if (cleanedLine) {
                // 提取第一个有意义的部分（通常是地点名称）
                const match = cleanedLine.match(/^([^→，,：:：\n]+?)(?:[→，,：:：]|$)/)
                if (match) {
                    location = match[1].trim()
                }
            }
        } else if (singleTimePattern.test(line)) {
            // 匹配 "13:00 - 地点名称" 格式
            const match = line.match(singleTimePattern)
            if (match) {
                let afterTime = line.substring(match[0].length).trim()
                afterTime = afterTime.replace(/^[→\s-~]+/, '').trim()
                if (afterTime) {
                    const locationMatch = afterTime.match(/^([^→，,：:：\n]+?)(?:[→，,：:：]|$)/)
                    if (locationMatch) {
                        location = locationMatch[1].trim()
                    }
                }
            }
        } else {
            // 模式2: 匹配 "地点名称: 描述" 或 "地点名称：描述" 格式
            const colonMatch = line.match(/^([^：:：\n\d]+?)[：:：]/)
            if (colonMatch) {
                location = colonMatch[1].trim()
            } else {
                // 模式3: 纯文本，提取第一个有意义的部分
                const textMatch = line.match(/^([^→，,：:：\n\d]+?)(?:[→，,：:：\s]|$)/)
                if (textMatch) {
                    location = textMatch[1].trim()
                }
            }
        }

        // 验证地点名称是否有效
        if (location &&
            location.length > 1 &&
            location.length < 50 &&
            !/^\d+$/.test(location) && // 不是纯数字（如 "13"）
            !/^\d{1,2}:\d{2}$/.test(location) && // 不是时间格式（如 "13:00"）
            !/^[-~→]+$/.test(location) && // 不是纯符号
            !/^[→\s-~]+$/.test(location)) { // 不是纯空白和符号

            // 移除可能的前导符号和空白
            location = location.replace(/^[-~→\s]+/, '').replace(/[-~→\s]+$/, '').trim()

            if (location && location.length > 1) {
                return {
                    location: location,
                    description: content.replace(line, '').trim() || content
                }
            }
        }
    }

    // 如果没有找到，使用第一行作为地点（移除时间部分）
    if (lines.length > 0) {
        let firstLine = lines[0].trim()

        // 移除时间部分（如 "13:00-15:00" 或 "13:00 -"）
        firstLine = firstLine.replace(/\d{1,2}:\d{2}\s*[-~至]\s*\d{1,2}:\d{2}/g, '')
        firstLine = firstLine.replace(/\d{1,2}:\d{2}\s*[-~]\s*/g, '')
        firstLine = firstLine.replace(/^[-~→\s]+/, '').trim()

        // 如果第一行还有内容，且不是纯数字
        if (firstLine &&
            firstLine.length > 1 &&
            !/^\d+$/.test(firstLine) &&
            !/^\d{1,2}:\d{2}$/.test(firstLine)) {

            // 提取第一个有意义的部分（可能是地点）
            const parts = firstLine.split(/[：:：→，,]/)
            const location = parts[0].trim()

            if (location && location.length > 1) {
                return {
                    location: location,
                    description: lines.slice(1).join('\n') || (parts.slice(1).join(' ') || firstLine)
                }
            }
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

        // 构建事件对象（确保字段符合 Ralendar API 要求）
        const event = {
            title: eventTitle.trim(), // 必填：标题
            description: (description || day.content || day.highlight || '').trim(), // 可选：描述
            start_time: formatISOWithOffset(startTimeUTC), // 必填：开始时间（ISO 8601 with timezone）
            end_time: formatISOWithOffset(endTimeUTC), // 可选：结束时间（ISO 8601 with timezone）
            reminder_minutes: 30, // 可选：提醒时间（分钟）
            email_reminder: true // 可选：邮件提醒
        }

        // 地点处理：如果有有效地点，添加 location 字段
        // 注意：Ralendar API 只需要 location 字段，不需要 location_name、location_address 等
        if (location && location !== '未指定地点' && location.trim() !== '') {
            event.location = location.trim()
        }

        // 如果有坐标，添加坐标信息（Ralendar API 支持）
        // 注意：坐标信息可能不在原始数据中，这里暂时不添加
        // 如果需要，可以从其他地方获取坐标信息

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

