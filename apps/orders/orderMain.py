from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import  Orders, OrderType, Users,ServiceProvider
from schemas.order.orderSchema import OrderIn, OrderOut
from schemas.user.usersSchema import UserOut
from apps.users.auth import get_current_user
from config.database import get_db
from sqlalchemy.orm import Session 
from sqlalchemy import and_
from typing import List,Union






router= APIRouter(
    tags=["Orders"]
)


def generate_custom_id(prefix: str, n_digits: int) -> str:
    """Generate a custom ID with a given prefix and a certain number of random digits"""
    random_digits = ''.join([str(random.randint(0,9)) for i in range(n_digits)])
    return f"{prefix}{random_digits}"


"""
Create/make an order

"""
@router.post('/order/', status_code=status.HTTP_201_CREATED, response_model= OrderOut)
async def create_order(order: OrderIn, db: Session = Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    custom_id = generate_custom_id("OD", 5)
   
    # if current_user.user_type  == "service provider":
    if current_user.user_type  == "service proider":
        raise HTTPException(status_code=403, detail="Not allowed")
    # Check if the order has a budget
    if order.is_budget:
        new_order = Orders(order_id=custom_id, client_id=current_user.user_id, **order.dict(), order_type=OrderType.budget)
    else:
        new_order = Orders(order_id=custom_id, client_id=current_user.user_id, **order.dict(), order_type=OrderType.quote)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return  new_order


"""
To get all order made
"""
@router.get("/all_orders/", response_model=List[OrderOut])
async def get_all_orders(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    orders = db.query(Orders).order_by(Orders.created_at).all()
    return orders


"""
To get all order made from a user
"""
@router.get("/orders/", response_model=List[OrderOut])
async def get_all_orders(db:Session=Depends(get_db),current_user: Union[Users, ServiceProvider] = Depends(get_current_user)):
    if current_user.user_type == "user" :
        orders = db.query(Orders).order_by(Orders.created_at).filter(Orders.client_id == current_user.user_id).all()
    elif current_user.user_type == "service_provider" :
        orders = db.query(Orders).order_by(Orders.created_at).filter(Orders.client_id == current_user.service_provider_id).all()
    else: 
        raise HTTPException(status_code=404, detail="No orders found")
    # if not orders:
    #     raise HTTPException(status_code=404, detail="No orders found")
    return orders



"""
To get all order made from a user which are 
still pending or without a bid or quote yet

"""
@router.get("/orders_pending_user/", response_model=List[OrderOut])
async def get_all_orders(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    orders = db.query(Orders).order_by(Orders.created_at).filter(and_(Orders.client_id == current_user.user_id, Orders.status != "Pending")).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No current order(S) found")
    return orders


"""
To get order made by ID 
"""
@router.get("/order/{order_id}",response_model=OrderOut)
async def get_an_order(order_id:str,db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    orders = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with: {order_id} found")
    return orders


"""
To make update to the Order

"""
@router.put('/orders/{order_id}')
async def update_order(
    order_id: str,
    order_update: OrderIn,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    
    existing_order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not existing_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id {order_id} not found")
    
     # Checking if the user is trying to edit another users's order
    if existing_order.client_id != current_user.user_id :
        raise HTTPException(status_code=403,detail='You can only edit your own orders!')
    # Update user details
    for field, value in order_update.dict().items():
        setattr(existing_order, field, value)

    db.commit()
    db.refresh(existing_order)

    return existing_order




"""
To delete an order
"""

@router.delete("/orders/{order_id}")
async def delete_order(order_id: str, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    # Check if the order exists
    order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with ID: {order_id} found")

    # Check if the current user is the owner of the order (optional)
    if order.client_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this order")

    # Delete the order from the database
    db.delete(order)
    db.commit()

    return {"message": f"Order with ID: {order_id} deleted successfully"}




