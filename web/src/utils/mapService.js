/**
 * 地图服务工具
 * 使用高德地图 API 进行地理编码
 */

// 高德地图 Web 服务 API Key（需要在高德开放平台申请）
// 获取地址：https://lbs.amap.com/
const AMAP_KEY = process.env.VUE_APP_AMAP_KEY || 'b08eafe129adb474e9cda93cb5da2ec7' // 默认使用示例 Key

/**
 * 地理编码：将地址转换为经纬度
 * @param {string} address - 地址字符串
 * @param {string} city - 城市名称（可选，提高精确度）
 * @returns {Promise<{lng: number, lat: number, formattedAddress: string}>}
 */
export async function geocode(address, city = '') {
  if (!address || !address.trim()) {
    throw new Error('地址不能为空')
  }

  try {
    // 使用高德地图 Web 服务 API 进行地理编码
    const url = 'https://restapi.amap.com/v3/geocode/geo'
    const params = new URLSearchParams({
      key: AMAP_KEY,
      address: address.trim(),
      city: city || ''
    })

    const response = await fetch(`${url}?${params}`)
    const data = await response.json()

    if (data.status !== '1') {
      throw new Error(data.info || '地理编码失败')
    }

    if (!data.geocodes || data.geocodes.length === 0) {
      throw new Error('未找到该地址的位置信息，请输入更详细的地址')
    }

    // 获取第一个结果
    const result = data.geocodes[0]
    const [lng, lat] = result.location.split(',').map(Number)

    return {
      lng,
      lat,
      formattedAddress: result.formatted_address,
      province: result.province,
      city: result.city,
      district: result.district,
      adcode: result.adcode
    }
  } catch (error) {
    console.error('地理编码失败:', error)
    throw error
  }
}

/**
 * 逆地理编码：将经纬度转换为地址
 * @param {number} lng - 经度
 * @param {number} lat - 纬度
 * @returns {Promise<{address: string, province: string, city: string, district: string}>}
 */
export async function reverseGeocode(lng, lat) {
  if (!lng || !lat) {
    throw new Error('经纬度不能为空')
  }

  try {
    const url = 'https://restapi.amap.com/v3/geocode/regeo'
    const params = new URLSearchParams({
      key: AMAP_KEY,
      location: `${lng},${lat}`
    })

    const response = await fetch(`${url}?${params}`)
    const data = await response.json()

    if (data.status !== '1') {
      throw new Error(data.info || '逆地理编码失败')
    }

    const regeocode = data.regeocode
    return {
      address: regeocode.formatted_address,
      province: regeocode.addressComponent.province,
      city: regeocode.addressComponent.city,
      district: regeocode.addressComponent.district
    }
  } catch (error) {
    console.error('逆地理编码失败:', error)
    throw error
  }
}

/**
 * 搜索地点（POI 搜索）
 * @param {string} keyword - 搜索关键词
 * @param {string} city - 城市名称（可选）
 * @returns {Promise<Array>}
 */
export async function searchPlace(keyword, city = '') {
  if (!keyword || !keyword.trim()) {
    throw new Error('搜索关键词不能为空')
  }

  try {
    const url = 'https://restapi.amap.com/v3/place/text'
    const params = new URLSearchParams({
      key: AMAP_KEY,
      keywords: keyword.trim(),
      city: city || '',
      offset: 10,
      page: 1,
      extensions: 'all'
    })

    const response = await fetch(`${url}?${params}`)
    const data = await response.json()

    if (data.status !== '1') {
      throw new Error(data.info || '搜索失败')
    }

    return data.pois.map(poi => {
      const [lng, lat] = poi.location.split(',').map(Number)
      return {
        name: poi.name,
        address: poi.address,
        lng,
        lat,
        type: poi.type,
        typecode: poi.typecode
      }
    })
  } catch (error) {
    console.error('地点搜索失败:', error)
    throw error
  }
}

