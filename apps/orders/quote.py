from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import Users, Orders,Quote, OrderType
from schemas.serviceProvider.serviceProviderSchema import ServiceProviderOut
from schemas.order.orderSchema import OrderIn, OrderOut,QuoteIn,QuoteUpdate,QuoteOut
from schemas.user.usersSchema import UserOut
from apps.serviceProvider.serviceProviderOauth import get_current_user
from config.database import get_db
from sqlalchemy.orm import Session 
from sqlalchemy import and_
from typing import List
from apps.users.auth import get_current_user as current_login_user





router= APIRouter(
    tags=["Quotes"]
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
    new_quote = Quote(quote_id=custom_id, status="Pending", service_provider_id=current_user.service_provider_id, client_id = check_order.client_id, **quote.dict())
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote




"""
To get all quote made
"""
@router.get("/quotes",response_model=List[QuoteOut])
async def get_all_quote(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    quotes = db.query(Quote).order_by(Quote.created_at).all()
    return quotes




"""
To get all quote made by current user (user)
"""
@router.get("/current_user_quotes",response_model=List[QuoteOut])
async def get_all_quote_by_current_id(db:Session=Depends(get_db),current_user: UserOut = Depends(current_login_user)):
    quotes = db.query(Quote).filter(and_(Quote.client_id == current_user.user_id, Quote.status == "Pending")).all()
    return quotes


"""
To get quote made by ID 
"""
@router.get("/quote/{quote_id}", response_model=QuoteOut)
async def get_a_quote_by_id(quote_id:str,db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    quote = db.query(Quote).filter(Quote.quote_id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No quote with: {quote_id} found")
    return quote


"""
To make update to a quote

"""
@router.put('/quote/{quote_id}',response_model=QuoteOut)
async def update_quote(
    quote_id: str,
    quote_update: QuoteUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    existing_quote = db.query(Quote).filter(Quote.quote_id == quote_id).first()

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



"""
To Assigned an order with a quote from a signed in user (user)
"""


@router.post('/accept_quote/{quote_id}', response_model=OrderOut)
async def accept_quote_by_current_user(quote_id: str, db: Session = Depends(get_db), current_user: UserOut = Depends(current_login_user)):
    quote = db.query(Quote).filter(Quote.quote_id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No quote with ID: {quote_id} found")
    order = db.query(Orders).filter(Orders.order_id == quote.order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with ID: {quote.order_id} found")
    if order.order_type != OrderType.quote:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only quote orders can have quotes")
    if quote.client_id != current_user.user_id :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You cannot accept this quote")
    order.is_assigned = True
    order.assigned_to = quote.service_provider_id
    quote.is_accepted = True
    quote.status ="Accepted"
    order.status ="Pending"
    order.budget = quote.quote_amount
    order.quote_id = quote_id
    db.commit()
    db.refresh(order)
    return order




"""
To accept an order with budget by service provider
"""


@router.post('/accept_budget/{order_id}', response_model=OrderOut)
async def accept_budget_as_service_provider(order_id: str, db: Session = Depends(get_db), current_user: ServiceProviderOut = Depends(get_current_user)):
    order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with ID: {order_id} found")
    if order.status ==  "Pending" or order.status =="Completed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="This order has already been completed/Assigned.")
    order.status ="Accepted"
    order.bidding_budget= current_user.service_provider_id
    db.commit()
    db.refresh(order)
    return order





"""
To Assigned an order with a budget from a signed in user (user)
"""


@router.post('/pend_budget/{order_id}', response_model=OrderOut)
async def accept_budget_by_current_user(order_id: str, db: Session = Depends(get_db), current_user: UserOut = Depends(current_login_user)):
    order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with ID: {order_id} found")
    if order.status != "Accepted":
        raise HTTPException(status_code=400, detail="The Order has no bidding budget/ has been assigned")
    order.is_assigned = True
    order.assigned_to = order.bidding_budget
    order.status ="Pending"
    db.commit()
    db.refresh(order)
    return order