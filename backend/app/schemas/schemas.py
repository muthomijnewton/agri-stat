from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

# ============== User Schemas ==============
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============== Login Schemas ==============
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_admin: bool
    message: str = "Login successful"

# ============== Product Schemas ==============
class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[Decimal] = None
    unit: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[Decimal] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============== Transaction Schemas ==============
class TransactionBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    transaction_date: date
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    user_id: Optional[int] = None

class TransactionUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    transaction_date: Optional[date] = None
    notes: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    product: Optional[ProductResponse] = None
    
    class Config:
        from_attributes = True

# ============== Forecast Schemas ==============
class ForecastBase(BaseModel):
    product_id: int
    forecast_date: date
    predicted_demand: int
    confidence_lower: Optional[Decimal] = None
    confidence_upper: Optional[Decimal] = None
    model_type: Optional[str] = None
    accuracy_score: Optional[Decimal] = None

class ForecastCreate(ForecastBase):
    pass

class ForecastUpdate(BaseModel):
    predicted_demand: Optional[int] = None
    confidence_lower: Optional[Decimal] = None
    confidence_upper: Optional[Decimal] = None
    accuracy_score: Optional[Decimal] = None

class ForecastResponse(ForecastBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    product: Optional[ProductResponse] = None
    
    class Config:
        from_attributes = True

# ============== Inventory Recommendation Schemas ==============
class InventoryRecommendationBase(BaseModel):
    product_id: int
    recommended_quantity: int
    current_quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    recommendation_date: date
    reason: Optional[str] = None

class InventoryRecommendationCreate(InventoryRecommendationBase):
    pass

class InventoryRecommendationUpdate(BaseModel):
    recommended_quantity: Optional[int] = None
    current_quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    reason: Optional[str] = None
    status: Optional[str] = None

class InventoryRecommendationResponse(InventoryRecommendationBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    product: Optional[ProductResponse] = None
    
    class Config:
        from_attributes = True

# ============== Bulk Response Schemas ==============
class TransactionWithForecast(BaseModel):
    transaction: TransactionResponse
    forecast: Optional[ForecastResponse] = None
    recommendation: Optional[InventoryRecommendationResponse] = None
