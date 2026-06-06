import { geocodeAddress } from '@/api/weather'

export async function geocode(address) {
  if (!address || address.trim() === '') {
    throw new Error('Address is required')
  }

  const result = await geocodeAddress(address)

  if (!result?.success || !result?.data) {
    throw new Error(result?.message || 'Geocode failed')
  }

  return {
    lat: result.data.lat,
    lng: result.data.lng,
    formattedAddress: result.data.formattedAddress || address,
  }
}
