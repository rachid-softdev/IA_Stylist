from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


# ─── User ─────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    email: str
    plan: str
    credits: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(BaseModel):
    id: str
    user_id: str
    photos: Optional[list[dict]] = None
    metadata: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfilePhotoSchema(BaseModel):
    url: str
    r2_key: str
    order: int


class ProfileMetadataSchema(BaseModel):
    morphologie: Optional[str] = None
    teint: Optional[str] = None
    style: Optional[str] = None
    detected_at: Optional[str] = None


# ─── Generation ───────────────────────────────────────────

class GenerateTryOnRequest(BaseModel):
    garment_id: Optional[str] = None
    garment_image: Optional[str] = None
    category: str = Field(..., pattern="^(top|bottom|dress|outerwear|shoes|accessories)$")
    model_photo_id: Optional[str] = None
    seed: Optional[int] = None
    num_inference_steps: int = Field(default=30, ge=20, le=50)


class GenerateVideoRequest(BaseModel):
    job_id: str
    video_type: str = Field(..., pattern="^(runway_walk|mirror_selfie|360_rotation|transition)$")


class GenerateLookbookRequest(BaseModel):
    garment_ids: list[str]
    style: str = Field(default="studio", pattern="^(studio|outdoor|lifestyle|luxe)$")
    model_type: Optional[str] = None
    background: Optional[str] = None


class JobResponse(BaseModel):
    id: str
    user_id: str
    brand_id: Optional[str] = None
    job_type: str
    status: str
    garment_id: Optional[str] = None
    input_params: Optional[dict] = None
    result_url: Optional[str] = None
    result_metadata: Optional[dict] = None
    credits_used: int
    error_message: Optional[str] = None
    ai_provider: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class JobCreateResponse(BaseModel):
    job_id: str
    status: str = "queued"


# ─── Credits ──────────────────────────────────────────────

class CreditBalanceResponse(BaseModel):
    balance: int
    plan: str


class CreditTransactionResponse(BaseModel):
    id: str
    user_id: str
    brand_id: Optional[str] = None
    amount: int
    type: str
    job_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Brand ────────────────────────────────────────────────

class BrandResponse(BaseModel):
    id: str
    name: str
    plan: str
    credits: int
    shopify_url: Optional[str] = None
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BrandCreateRequest(BaseModel):
    name: str
    shopify_url: Optional[str] = None


class BrandMemberResponse(BaseModel):
    brand_id: str
    user_id: str
    role: str

    model_config = {"from_attributes": True}


class BrandMemberCreateRequest(BaseModel):
    email: EmailStr
    role: str = Field(default="member", pattern="^(admin|member)$")


class ApiKeyResponse(BaseModel):
    id: str
    prefix: str
    last_four: str
    created_at: datetime


class ApiKeyCreateResponse(BaseModel):
    api_key: str
    id: str


# ─── Garments ─────────────────────────────────────────────

class GarmentResponse(BaseModel):
    id: str
    brand_id: str
    sku: str
    name: str
    category: str
    image_url: str
    metadata: Optional[dict] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GarmentCreateRequest(BaseModel):
    sku: str
    name: str
    category: str = Field(..., pattern="^(top|bottom|dress|outerwear|shoes|accessories)$")
    image_url: str
    metadata: Optional[dict] = None


class GarmentUpdateRequest(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[dict] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|validating)$")


# ─── Collections ─────────────────────────────────────────

class CollectionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    is_public: bool
    share_token: Optional[str] = None
    created_at: datetime
    items_count: Optional[int] = None

    model_config = {"from_attributes": True}


class CollectionCreateRequest(BaseModel):
    name: str
    is_public: bool = False


class CollectionUpdateRequest(BaseModel):
    name: Optional[str] = None
    is_public: Optional[bool] = None


# ─── Upload ───────────────────────────────────────────────

class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str = Field(..., pattern="^(image/jpeg|image/png|image/webp)$")
    folder: str = Field(..., pattern="^(uploads/raw|uploads/garments|avatars)$")
    size: Optional[int] = Field(default=None, ge=1, le=10 * 1024 * 1024, description="File size in bytes (max 10MB)")


class PresignedUrlResponse(BaseModel):
    upload_url: str
    r2_key: str
    public_url: str


class UploadConfirmRequest(BaseModel):
    r2_key: str
    size: int


# ─── Analytics ────────────────────────────────────────────

class AnalyticsOverviewResponse(BaseModel):
    total_tryons: int
    tryons_delta: float
    conversion_rate: float
    conversion_delta: float
    returns_saved: int
    returns_delta: float
    cost_savings: float
    savings_delta: float
    is_estimate: bool = True


class TimelineDataPoint(BaseModel):
    date: str
    count: int


class TopSkuItem(BaseModel):
    sku: str
    name: str
    tryons: int


# ─── Stylist ──────────────────────────────────────────────

class StylistRecommendation(BaseModel):
    garment_id: str
    fit_advice: str
    style_advice: str
    color_advice: str
    fit_score: int = Field(ge=1, le=10)


class StylistOutfit(BaseModel):
    items: list[dict]
    description: str
    occasion: str


class StylistFeedbackRequest(BaseModel):
    job_id: str
    helpful: bool


# ─── Common ───────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    cursor: Optional[str] = None


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None
