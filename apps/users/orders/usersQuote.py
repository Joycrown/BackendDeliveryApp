from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import Users, Orders,Quote, OrderType, Budget
from schemas.serviceProvider.serviceProviderSchema import ServiceProviderOut
from schemas.order.orderSchema import OrderIn, OrderOut,QuoteIn,QuoteUpdate,QuoteOut, BudgetOut
from schemas.user.usersSchema import UserOut
# from apps.serviceProvider.serviceProviderOauth import get_current_user
from config.database import get_db
from sqlalchemy.orm import Session 
from sqlalchemy import and_
from typing import List, Union
from apps.users.auth import get_current_user 





router= APIRouter(
    tags=["Users Quotes"]
)


def generate_custom_id(prefix: str, n_digits: int) -> str:
  """Generate a custom ID with a given prefix and a certain number of random digits"""
  random_digits = ''.join([str(random.randint(0,9)) for i in range(n_digits)])
  return f"{prefix}{random_digits}"


"""
To get all quote made
"""
@router.get("/quotes",response_model=List[QuoteOut])
async def get_all_quote(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
  quotes = db.query(Quote).order_by(Quote.created_at).all()
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
To Assigned an order with a quote from a signed in user (user)
"""


@router.post('/accept_quote/{quote_id}', response_model=OrderOut)
async def accept_quote_by_current_user(quote_id: str, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
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
To get all quote made by current user (user)
"""
@router.get("/current_user_quotes",response_model=List[QuoteOut])
async def get_all_quote_by_current_user(db:Session=Depends(get_db),current_user: UserOut  = Depends(get_current_user)):
    if current_user.user_type != "user":
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    quotes = db.query(Quote).filter(and_(Quote.client_id == current_user.user_id, Quote.status == "Pending")).all()
    return quotes



""""
TO reject a quote from a service provider
"""
@router.post('/reject_quote/{quote_id}')
async def reject_quote_by_current_user(quote_id: str, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
  quote = db.query(Quote).filter(Quote.quote_id == quote_id).first()
  if not quote:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No response made with this ID: {quote_id}")
  order = db.query(Orders).filter(Orders.order_id == quote.order_id).first()
  if order.status != "Pending":
    raise HTTPException(status_code=400, detail="The Order has no bidding budget/ has been assigned")

  db.delete(quote)
  db.commit()
  
  return {"detail":"Quote Rejection Successful"}