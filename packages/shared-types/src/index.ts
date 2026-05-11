// ─── User & Auth ──────────────────────────────────────────

export type PlanTier = 'free' | 'pro' | 'creator' | 'starter' | 'growth' | 'enterprise'

export interface User {
  id: string
  email: string
  plan: PlanTier
  credits: number
  created_at: string
  updated_at: string
}

export interface UserProfile {
  id: string
  user_id: string
  photos: ProfilePhoto[]
  metadata: ProfileMetadata | null
  created_at: string
}

export interface ProfilePhoto {
  url: string
  r2_key: string
  order: number
}

export interface ProfileMetadata {
  morphologie?: string
  teint?: string
  style?: string
  detected_at?: string
}

// ─── Brand ────────────────────────────────────────────────

export interface Brand {
  id: string
  name: string
  plan: PlanTier
  credits: number
  shopify_url?: string | null
  tenant_id: string
  created_at: string
}

export interface BrandMember {
  brand_id: string
  user_id: string
  role: 'admin' | 'member'
  user?: User
}

// ─── Garments ─────────────────────────────────────────────

export type GarmentCategory = 'top' | 'bottom' | 'dress' | 'outerwear' | 'shoes' | 'accessories'

export type GarmentStatus = 'active' | 'inactive' | 'validating'

export interface Garment {
  id: string
  brand_id: string
  sku: string
  name: string
  category: GarmentCategory
  image_url: string
  metadata: GarmentMetadata
  status: GarmentStatus
  created_at: string
}

export interface GarmentMetadata {
  colors?: string[]
  sizes?: string[]
  fit?: string
  material?: string
  season?: string
  price?: number
}

// ─── Generation Jobs ──────────────────────────────────────

export type JobType = 'image' | 'video' | 'lookbook'

export type JobStatus = 'queued' | 'processing' | 'done' | 'error' | 'cancelled'

export type VideoType = 'runway_walk' | 'mirror_selfie' | '360_rotation' | 'transition'

export interface GenerationJob {
  id: string
  user_id: string
  brand_id?: string | null
  job_type: JobType
  status: JobStatus
  garment_id?: string | null
  input_params: GenerationParams
  result_url?: string | null
  result_metadata?: Record<string, unknown> | null
  credits_used: number
  error_message?: string | null
  ai_provider?: string | null
  duration_ms?: number | null
  created_at: string
  completed_at?: string | null
  garment?: Garment | null
}

export interface GenerationParams {
  model_photo?: string
  garment_image?: string
  category?: GarmentCategory
  num_inference_steps?: number
  seed?: number
  video_type?: VideoType
  style?: string
  background?: string
  model_type?: string
  num_variations?: number
}

// ─── Credits ──────────────────────────────────────────────

export type CreditTransactionType = 'generation' | 'purchase' | 'refund' | 'bonus'

export interface CreditTransaction {
  id: string
  user_id: string
  brand_id?: string | null
  amount: number
  type: CreditTransactionType
  job_id?: string | null
  description?: string | null
  created_at: string
}

// ─── Collections ──────────────────────────────────────────

export interface Collection {
  id: string
  user_id: string
  name: string
  is_public: boolean
  share_token?: string | null
  created_at: string
  items_count?: number
}

export interface CollectionItem {
  collection_id: string
  job_id: string
  added_at: string
  job?: GenerationJob
}

// ─── API Types ────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T
  meta: {
    request_id: string
    timestamp: string
    page?: number
    page_size?: number
    total?: number
    next_cursor?: string | null
  }
  error: null
}

export interface ApiError {
  data: null
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

// ─── Plan Definitions ─────────────────────────────────────

export interface PlanDefinition {
  tier: PlanTier
  name: string
  price: number
  currency: string
  interval: 'month' | 'year'
  credits_per_month: number
  features: string[]
  limits: PlanLimits
}

export interface PlanLimits {
  max_generations_per_hour: number
  max_storage_days: number
  video_enabled: boolean
  max_skus?: number
  watermark: boolean
  export_formats: string[]
}
