import request from './request'

/**
 * 通过后端定位接口获取当前城市
 * @returns {Promise<Object>} 定位结果
 */
export const getLocationByIP = () => {
  return request.get('/location/')
}

/**
 * 获取指定城市天气
 * @param {string} city - 城市名称
 * @returns {Promise<Object>} 天气结果
 */
export const getWeatherByCity = (city) => {
  return request.get('/weather/', {
    params: { location: city }
  })
}
