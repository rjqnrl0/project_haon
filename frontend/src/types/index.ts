export interface User {
  id: string
  email: string
  faceRegistered: boolean
}

export type AuthStatus = 'UNAUTHENTICATED' | 'AUTHENTICATED_NO_FACE' | 'FULLY_AUTHENTICATED'

export type ClothingCategory = 'top' | 'bottom' | 'dress' | 'outer' | 'accessory'

export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface ApiError {
  detail: string
  code: string
}

export interface DutyFreeProduct {
  id: string
  brand: string
  name: string
  category: ClothingCategory
  price: number
  discountPrice: number
  imageUrl: string
  description: string
}

export interface Attraction {
  name: string
  nameKo: string
  description: string
  imageKeyword: string
}

export interface DutyFreeCodiResult {
  recommended_items: DutyFreeProduct[]
  codi_advice: string
  weather_info: {
    avg_temp: number
    condition: string
  }
}

export interface FittingWithBackgroundResult {
  task_id: string
  result_url: string
  status: string
}
