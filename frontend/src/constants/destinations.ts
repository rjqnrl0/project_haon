export interface Destination {
  id: string
  nameKo: string
  nameEn: string
  country: string
  emoji: string
  imageUrl: string
}

export const DESTINATIONS: Destination[] = [
  {
    id: 'tokyo',
    nameKo: '도쿄',
    nameEn: 'Tokyo',
    country: 'JP',
    emoji: '🗼',
    imageUrl: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop',
  },
  {
    id: 'bangkok',
    nameKo: '방콕',
    nameEn: 'Bangkok',
    country: 'TH',
    emoji: '🛕',
    imageUrl: 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=400&h=300&fit=crop',
  },
  {
    id: 'paris',
    nameKo: '파리',
    nameEn: 'Paris',
    country: 'FR',
    emoji: '🇫🇷',
    imageUrl: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400&h=300&fit=crop',
  },
  {
    id: 'london',
    nameKo: '런던',
    nameEn: 'London',
    country: 'GB',
    emoji: '🎡',
    imageUrl: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400&h=300&fit=crop',
  },
  {
    id: 'new york',
    nameKo: '뉴욕',
    nameEn: 'New York',
    country: 'US',
    emoji: '🗽',
    imageUrl: 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=400&h=300&fit=crop',
  },
  {
    id: 'bali',
    nameKo: '발리',
    nameEn: 'Bali',
    country: 'ID',
    emoji: '🏝️',
    imageUrl: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=400&h=300&fit=crop',
  },
]
