// web/src/utils/mapService.js

/**
 * 高德地图 Web 服务 API Key
 * 注意：这是服务器端或前端直接调用的 Web 服务 API Key，与 JS API Key 不同
 * 实际使用时应该从环境变量或配置中获取
 */
const AMAP_WEB_SERVICE_KEY = '53b6a185427e97b53e16c8786a272f62' // 使用你的高德 Web 服务 API Key

/**
 * 使用高德地图 Web 服务 API 进行地理编码（地址转坐标）
 * @param {string} address - 要进行地理编码的地址
 * @returns {Promise<Object>} - 包含 lat, lng, formattedAddress 的 Promise
 */
export async function geocode(address) {
  if (!address || address.trim() === '') {
    throw new Error('地址不能为空')
  }

  if (!AMAP_WEB_SERVICE_KEY || AMAP_WEB_SERVICE_KEY === 'YOUR_AMAP_WEB_SERVICE_KEY') {
    console.warn('⚠️ 高德地图 Web 服务 API Key 未配置，地理编码功能将无法使用。')
    throw new Error('高德地图 Web 服务 API Key 未配置')
  }

  const url = `https://restapi.amap.com/v3/geocode/geo?key=${AMAP_WEB_SERVICE_KEY}&address=${encodeURIComponent(address)}`

  try {
    const response = await fetch(url)
    const data = await response.json()

    if (data.status === '1' && data.infocode === '10000' && data.geocodes && data.geocodes.length > 0) {
      const geocode = data.geocodes[0]
      const [lng, lat] = geocode.location.split(',')
      return {
        lat: parseFloat(lat),
        lng: parseFloat(lng),
        formattedAddress: geocode.formatted_address || address,
      }
    } else {
      const errorMsg = data.info || '未知错误'
      throw new Error(`高德地理编码失败: ${errorMsg}`)
    }
  } catch (error) {
    console.error('地理编码请求失败:', error)
    throw new Error(`地理编码请求失败: ${error.message}`)
  }
}
