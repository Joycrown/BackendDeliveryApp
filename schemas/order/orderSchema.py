from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from schemas.user.usersSchema import UserOut
from schemas.serviceProvider.serviceProviderSchema import ServiceProviderOut




class OrderIn(BaseModel):
    order_title: str
    brand: str
    model:str
    equipment_Category: str
    equipment_type: str
    dimension_height: Optional[str]
    dimension_length: Optional[str]
    dimension_width: Optional[str]
    dimension_weight: Optional[str]
    trailer_preference: bool
    on_trailer: bool
    no_of_pieces: int
    collection_area: str
    collection_location: str
    loading_assistance: bool
    date_of_collection: str
    delivery_area: str
    delivery_location: str
    off_loading_assistance: bool
    date_of_delivery: str
    is_budget: bool
    budget: Optional[str]


class OrderOut(BaseModel):
    order_id: str
    order_title: str
    brand: str
    model:str
    equipment_Category: str
    equipment_type: str
    dimension_height: str
    dimension_length: str
    dimension_width: str
    dimension_weight: str
    trailer_preference: bool
    on_trailer: bool
    collection_area: str
    collection_location: str
    no_of_pieces: int
    bidding_budget: str
    loading_assistance: bool
    date_of_collection: str
    delivery_area: str
    delivery_location: str
    off_loading_assistance: bool
    date_of_delivery: str
    is_assigned: bool
    is_completed: bool
    assigned_to: Optional[str]
    client_id: str
    is_budget: bool
    order_type: str
    is_completed: bool
    quote_id: str
    payment_intent_id:str
    budget: str
    status: str
    client: UserOut
    quote_id: Optional[str]
    # rejectedServiceProvider: List[str] = []
    carrier: Optional[ServiceProviderOut]
    created_at: datetime

    class Config:
        from_attributes = True


class QuoteOut(BaseModel):
    quote_id : str
    service_provider: Optional[ServiceProviderOut]
    order_id: str
    client_id: str
    order : Optional[OrderOut]
    quote_amount : str
    is_accepted: bool
    created_at: datetime

class BudgetOut(BaseModel):
    budget_id : str
    service_provider: Optional[ServiceProviderOut]
    order_id: str
    client: Optional[UserOut]
    order : Optional[OrderOut]
    amount : str
    status: str
    created_at: datetime




class QuoteIn(BaseModel):
    order_id: str
    quote_amount: str


class QuoteUpdate(BaseModel):
     quote_amount: float