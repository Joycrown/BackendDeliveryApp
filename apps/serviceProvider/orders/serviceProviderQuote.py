from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import Orders,Quote, OrderType
from schemas.serviceProvider.serviceProviderSchema import ServiceProviderOut
from schemas.order.orderSchema import QuoteIn,QuoteUpdate,QuoteOut
from config.database import get_db
from sqlalchemy.orm import Session 
from sqlalchemy import and_
from apps.users.auth import get_current_user 





router= APIRouter(
    tags=["Service Providers Quotes"]
)

def generate_custom_id(prefix: str, n_digits: int) -> str:
    """Generate a custom ID with a given prefix and a certain number of random digits"""
    random_digits = ''.join([str(random.randint(0,9)) for i in range(n_digits)])
    return f"{prefix}{random_digits}"


"""
Create/make a quote
"""
@router.post('/quote', status_code=status.HTTP_201_CREATED, response_model=QuoteOut)
async def create_quote(quote: QuoteIn, db: Session = Depends(get_db),current_user: ServiceProviderOut = Depends(get_current_user)):
    custom_id = generate_custom_id("QU", 5)
    check_order = db.query(Orders).filter(Orders.order_id == quote.order_id).first()
    if not check_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")
    if check_order.order_type != OrderType.quote:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only quote orders can have quotes")
    quote_check = db.query(Quote).filter((Quote.order_id == quote.order_id) & (Quote.service_provider_id == current_user.service_provider_id)).first()
    if quote_check:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="You have already submitted a quote to this order.")
    new_quote = Quote(quote_id=custom_id, status="Pending", service_provider_id=current_user.service_provider_id, client_id = check_order.client_id, **quote.dict())
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote







"""
To make update to a quote
"""
@router.put('/quote/{quote_id}',response_model=QuoteOut)
async def update_quote(
    quote_id: str,
    quote_update: QuoteUpdate,
    db: Session = Depends(get_db),
    current_user: ServiceProviderOut = Depends(get_current_user)
):
    existing_quote = db.query(Quote).filter(and_(Quote.quote_id == quote_id, Quote.service_provider_id == current_user.service_provider_id)).first()

    if not existing_quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quote with id {quote_id} not found")

    # Update user details
    for field, value in quote_update.dict().items():
        setattr(existing_quote, field, value)

    db.commit()
    db.refresh(existing_quote)

    return existing_quote




"""
To delete a quote
"""

@router.delete("/quote/{quote_id}")
async def delete_a_quote(quote_id: str, db: Session = Depends(get_db), current_user: ServiceProviderOut = Depends(get_current_user)):
    # Check if the order exists
    quote = db.query(Quote).filter(Quote.quote_id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No quote with ID: {quote_id} found")

    # Check if the current user is the owner of the order (optional)
    if quote.service_provider_id != current_user.service_provider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this order")

    # Delete the order from the database
    db.delete(quote)
    db.commit()

    return {"message": f"Order with ID: {quote_id} deleted successfully"}









