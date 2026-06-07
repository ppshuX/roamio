export async function geocode(address) {
  if (!address || address.trim() === '') {
    throw new Error('Address is required')
  }

  throw new Error('Map geocoding is temporarily unavailable')
}
