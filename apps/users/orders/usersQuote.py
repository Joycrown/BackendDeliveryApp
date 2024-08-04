from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import Orders,Quote
from schemas.order.orderSchema import QuoteOut
from schemas.user.usersSchema import UserOut
from config.database import get_db
from sqlalchemy.orm import Session 
from sqlalchemy import and_,desc
from typing import List
from apps.users.auth import get_current_user 





router= APIRouter(
    tags=["Users Quotes"]
)


def generate_custom_id(prefix: str, n_digits: int) -> str:
  """Generate a custom ID with a given prefix and a certain number of random digits"""
  random_digits = ''.join([str(random.randint(0,9)) for _ in range(n_digits)])
  return f"{prefix}{random_digits}"


"""
To get all quote made
"""
@router.get("/quotes",response_model=List[QuoteOut])
async def get_all_quote(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
  quotes = db.query(Quote).order_by(desc(Quote.created_at)).all()
  return quotes




"""
To get all quote made by current user (user)
"""
@router.get("/current_user_quotes",response_model=List[QuoteOut])
async def get_all_quote_by_current_user(db:Session=Depends(get_db),current_user: UserOut  = Depends(get_current_user)):
    if current_user.user_type != "user":
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    quotes = db.query(Quote).order_by(desc(Quote.created_at)).filter(and_(Quote.client_id == current_user.user_id, Quote.status == "Pending")).all()
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