export type ProductStatus = 'publicado' | 'pendente' | 'rejeitado' | 'monitorando'

export interface Product {
  id: string
  title: string
  image: string
  price: number
  oldPrice: number
  discount: number
  score: number
  store: string
  officialStore: boolean
  freeShipping: boolean
  niche: string
  status: ProductStatus
  foundAt: string
  affiliateLink: string
}

export interface Niche {
  id: string
  name: string
  keywords: string[]
  active: boolean
  minScore: number
  productsFound: number
}

export interface PricePoint {
  date: string
  price: number
}

export interface ActivityItem {
  id: string
  type: 'publicado' | 'encontrado' | 'aprovado' | 'rejeitado' | 'queda'
  message: string
  time: string
}

export const products: Product[] = [
  {
    id: 'MLB-4821093',
    title: 'Fone de Ouvido Bluetooth JBL Tune 520BT Sem Fio',
    image: '/images/products/fone-bluetooth.png',
    price: 189.9,
    oldPrice: 349.9,
    discount: 46,
    score: 92,
    store: 'JBL Loja Oficial',
    officialStore: true,
    freeShipping: true,
    niche: 'Áudio',
    status: 'pendente',
    foundAt: 'há 12 min',
    affiliateLink: 'https://mercadolivre.com/sec/1abc23',
  },
  {
    id: 'MLB-3390218',
    title: 'Smartwatch Amazfit Bip 5 Tela 1.91" GPS',
    image: '/images/products/smartwatch.png',
    price: 279.0,
    oldPrice: 449.0,
    discount: 38,
    score: 87,
    store: 'Amazfit Oficial',
    officialStore: true,
    freeShipping: true,
    niche: 'Wearables',
    status: 'pendente',
    foundAt: 'há 25 min',
    affiliateLink: 'https://mercadolivre.com/sec/2def45',
  },
  {
    id: 'MLB-2874530',
    title: 'Fritadeira Air Fryer Mondial 4L Family AFN-40',
    image: '/images/products/airfryer.png',
    price: 299.9,
    oldPrice: 499.9,
    discount: 40,
    score: 85,
    store: 'Mondial Eletros',
    officialStore: true,
    freeShipping: true,
    niche: 'Casa & Cozinha',
    status: 'pendente',
    foundAt: 'há 41 min',
    affiliateLink: 'https://mercadolivre.com/sec/3ghi67',
  },
  {
    id: 'MLB-5102947',
    title: 'Notebook Lenovo IdeaPad 1 Ryzen 5 8GB 512GB SSD',
    image: '/images/products/notebook.png',
    price: 2199.0,
    oldPrice: 3099.0,
    discount: 29,
    score: 78,
    store: 'Lenovo Store',
    officialStore: true,
    freeShipping: true,
    niche: 'Informática',
    status: 'publicado',
    foundAt: 'há 2 h',
    affiliateLink: 'https://mercadolivre.com/sec/4jkl89',
  },
  {
    id: 'MLB-1938475',
    title: 'Tênis Olympikus Corre 4 Masculino Corrida',
    image: '/images/products/tenis.png',
    price: 249.9,
    oldPrice: 399.9,
    discount: 37,
    score: 81,
    store: 'Olympikus Oficial',
    officialStore: true,
    freeShipping: true,
    niche: 'Esportes',
    status: 'publicado',
    foundAt: 'há 3 h',
    affiliateLink: 'https://mercadolivre.com/sec/5mno12',
  },
  {
    id: 'MLB-6203184',
    title: 'Cafeteira Espresso Três Corações Mimo Preta',
    image: '/images/products/cafeteira.png',
    price: 359.0,
    oldPrice: 529.0,
    discount: 32,
    score: 74,
    store: 'TudoDeCafé',
    officialStore: false,
    freeShipping: true,
    niche: 'Casa & Cozinha',
    status: 'publicado',
    foundAt: 'há 5 h',
    affiliateLink: 'https://mercadolivre.com/sec/6pqr34',
  },
  {
    id: 'MLB-7381920',
    title: 'Smart TV Samsung 50" Crystal UHD 4K CU7700',
    image: '/images/products/smart-tv.png',
    price: 2099.0,
    oldPrice: 2899.0,
    discount: 28,
    score: 76,
    store: 'Samsung Oficial',
    officialStore: true,
    freeShipping: true,
    niche: 'TV & Vídeo',
    status: 'monitorando',
    foundAt: 'há 8 h',
    affiliateLink: 'https://mercadolivre.com/sec/7stu56',
  },
  {
    id: 'MLB-8471029',
    title: 'Aspirador Robô Wap Robot W90 com Mapeamento',
    image: '/images/products/aspirador-robo.png',
    price: 599.9,
    oldPrice: 999.9,
    discount: 40,
    score: 83,
    store: 'Wap Loja Oficial',
    officialStore: true,
    freeShipping: false,
    niche: 'Casa & Cozinha',
    status: 'monitorando',
    foundAt: 'há 10 h',
    affiliateLink: 'https://mercadolivre.com/sec/8vwx78',
  },
]

export const niches: Niche[] = [
  {
    id: 'n1',
    name: 'Casa & Cozinha',
    keywords: ['air fryer', 'cafeteira', 'aspirador robô', 'panela elétrica'],
    active: true,
    minScore: 70,
    productsFound: 148,
  },
  {
    id: 'n2',
    name: 'Informática',
    keywords: ['notebook', 'ssd', 'monitor', 'teclado mecânico'],
    active: true,
    minScore: 75,
    productsFound: 96,
  },
  {
    id: 'n3',
    name: 'Áudio',
    keywords: ['fone bluetooth', 'caixa de som', 'soundbar'],
    active: true,
    minScore: 72,
    productsFound: 87,
  },
  {
    id: 'n4',
    name: 'Wearables',
    keywords: ['smartwatch', 'pulseira inteligente'],
    active: true,
    minScore: 70,
    productsFound: 54,
  },
  {
    id: 'n5',
    name: 'Esportes',
    keywords: ['tênis corrida', 'whey protein', 'bicicleta'],
    active: false,
    minScore: 68,
    productsFound: 41,
  },
  {
    id: 'n6',
    name: 'TV & Vídeo',
    keywords: ['smart tv', 'projetor', 'chromecast'],
    active: true,
    minScore: 74,
    productsFound: 38,
  },
]

export const priceHistory: Record<string, PricePoint[]> = {
  'MLB-4821093': [
    { date: '01/07', price: 349.9 },
    { date: '03/07', price: 329.9 },
    { date: '05/07', price: 319.9 },
    { date: '07/07', price: 299.9 },
    { date: '09/07', price: 259.9 },
    { date: '11/07', price: 219.9 },
    { date: '12/07', price: 189.9 },
  ],
}

export const publishedPerDay = [
  { date: '06/07', publicadas: 14, encontradas: 52 },
  { date: '07/07', publicadas: 18, encontradas: 61 },
  { date: '08/07', publicadas: 11, encontradas: 44 },
  { date: '09/07', publicadas: 22, encontradas: 73 },
  { date: '10/07', publicadas: 19, encontradas: 66 },
  { date: '11/07', publicadas: 25, encontradas: 81 },
  { date: '12/07', publicadas: 16, encontradas: 58 },
]

export const activity: ActivityItem[] = [
  {
    id: 'a1',
    type: 'encontrado',
    message: 'Nova oferta encontrada: Fone JBL Tune 520BT (score 92)',
    time: 'há 12 min',
  },
  {
    id: 'a2',
    type: 'publicado',
    message: 'Notebook Lenovo IdeaPad 1 publicado no canal @ofertasbr',
    time: 'há 2 h',
  },
  {
    id: 'a3',
    type: 'queda',
    message: 'Queda de preço: Smart TV Samsung 50" caiu 8% em 24h',
    time: 'há 4 h',
  },
  {
    id: 'a4',
    type: 'aprovado',
    message: 'Tênis Olympikus Corre 4 aprovado manualmente',
    time: 'há 3 h',
  },
  {
    id: 'a5',
    type: 'publicado',
    message: 'Cafeteira Três Corações Mimo publicada no canal @ofertasbr',
    time: 'há 5 h',
  },
  {
    id: 'a6',
    type: 'rejeitado',
    message: 'Carregador turbo genérico rejeitado (score 41)',
    time: 'há 6 h',
  },
]

export const stats = {
  ofertasHoje: 58,
  ofertasHojeDelta: '+12%',
  publicadasHoje: 16,
  publicadasHojeDelta: '+6%',
  scoreMedio: 79,
  scoreMedioDelta: '+3 pts',
  cliquesAfiliado: 1243,
  cliquesAfiliadoDelta: '+18%',
}

export function formatBRL(value: number) {
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  })
}
