export { DUTY_FREE_PRODUCTS } from './dutyfree'

export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

export const CLOTHING_CATEGORIES = [
  { value: 'top', label: '상의' },
  { value: 'bottom', label: '하의' },
  { value: 'dress', label: '원피스' },
  { value: 'outer', label: '아우터' },
  { value: 'accessory', label: '액세서리' },
] as const

export const POPULAR_CITIES = [
  { nameKo: '서울', nameEn: 'Seoul', country: 'KR' },
  { nameKo: '부산', nameEn: 'Busan', country: 'KR' },
  { nameKo: '제주', nameEn: 'Jeju', country: 'KR' },
  { nameKo: '도쿄', nameEn: 'Tokyo', country: 'JP' },
  { nameKo: '오사카', nameEn: 'Osaka', country: 'JP' },
  { nameKo: '방콕', nameEn: 'Bangkok', country: 'TH' },
  { nameKo: '싱가포르', nameEn: 'Singapore', country: 'SG' },
  { nameKo: '파리', nameEn: 'Paris', country: 'FR' },
  { nameKo: '런던', nameEn: 'London', country: 'GB' },
  { nameKo: '뉴욕', nameEn: 'New York', country: 'US' },
  { nameKo: '하와이', nameEn: 'Honolulu', country: 'US' },
  { nameKo: '발리', nameEn: 'Bali', country: 'ID' },
  { nameKo: '다낭', nameEn: 'Da Nang', country: 'VN' },
  { nameKo: '강릉', nameEn: 'Gangneung', country: 'KR' },
  { nameKo: '경주', nameEn: 'Gyeongju', country: 'KR' },
  { nameKo: '전주', nameEn: 'Jeonju', country: 'KR' },
  { nameKo: '여수', nameEn: 'Yeosu', country: 'KR' },
] as const
