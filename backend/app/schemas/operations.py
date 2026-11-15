from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class SaleItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0, max_digits=16, decimal_places=4, allow_inf_nan=False)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2, allow_inf_nan=False)


class SaleCreate(BaseModel):
    client_event_id: UUID
    location_id: UUID
    items: list[SaleItemCreate] = Field(min_length=1, max_length=100)

    @model_validator(mode='after')
    def no_duplicate_products(self):
        ids = [item.product_id for item in self.items]
        if len(set(ids)) != len(ids):
            raise ValueError('Combine each product into one sale line')
        return self
