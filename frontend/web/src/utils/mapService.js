export async function geocode(address) {
  if (!address || address.trim() === '') {
    throw new Error('Address is required')
  }

  return {
    success: false,
    code: 'MAP_DISABLED',
    message: 'Map geocoding is temporarily unavailable'
  }
}
