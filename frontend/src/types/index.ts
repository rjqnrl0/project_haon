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
