from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import  Orders, OrderType, Users,ServiceProvider,Budget,Quote
from schemas.order.orderSchema import OrderIn, OrderOut, BudgetOut, QuoteOut
from schemas.user.usersSchema import UserOut
from apps.users.auth import get_current_user
from config.database import get_db
from sqlalchemy.orm import Session 
from sqlalchemy import and_
from typing import List,Union, Dict






router= APIRouter(
    tags=[" User Budget"]
)


def generate_custom_id(prefix: str, n_digits: int) -> str:
    """Generate a custom ID with a given prefix and a certain number of random digits"""
    random_digits = ''.join([str(random.randint(0,9)) for i in range(n_digits)])
    return f"{prefix}{random_digits}"





"""
Create/make an order
"""
@router.post('/order', status_code=status.HTTP_201_CREATED, response_model= OrderOut)
async def create_order(order: OrderIn, db: Session = Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    custom_id = generate_custom_id("OD", 5)
   
    # if current_user.user_type  == "service provider":
    if current_user.user_type  == "service provider":
        raise HTTPException(status_code=403, detail="Not allowed")
    rejectedServiceProvider = ["none"]
    # Check if the order has a budget
    if order.is_budget:
        new_order = Orders(order_id=custom_id, rejectedServiceProvider=rejectedServiceProvider, client_id=current_user.user_id, **order.dict(), order_type=OrderType.budget)
    else:
        new_order = Orders(order_id=custom_id,rejectedServiceProvider=rejectedServiceProvider, client_id=current_user.user_id, **order.dict(), order_type=OrderType.quote)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return  new_order




"""
To get all orders from budget and 
quotes reacted to made from a user
"""
@router.get("/orders", response_model=Dict[str, Union[List[BudgetOut], List[QuoteOut],int]])
async def get_all_orders_reacted_to_for_current_user(db:Session=Depends(get_db),current_user: Union[Users, ServiceProvider] = Depends(get_current_user)):
    if current_user.user_type == "user" :
        budget = db.query(Budget).order_by(Budget.created_at).filter(Budget.client_id == current_user.user_id).all()
        quote = db.query(Quote).filter(and_(Quote.client_id == current_user.user_id, Quote.status=="Pending")).all()
        total_count = len(budget) + len(quote)
    else: 
        raise HTTPException(status_code=404, detail="No orders found")
    # if not orders:
    #     raise HTTPException(status_code=404, detail="No orders found")
    return {"budget": budget, "quote": quote, "length":total_count}


"""
To get all order made from a user 
"""
@router.get("/orders/me", response_model=List[OrderOut])
async def get_all_orders(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    orders = db.query(Orders).order_by(Orders.created_at).filter(and_(Orders.client_id == current_user.user_id)).all()
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
    if current_user.user_type  != "user":
        raise HTTPException(status_code=403, detail="Not allowed")
   
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with ID: {order_id} found")

    # Check if the current user is the owner of the order (optional)
    if order.client_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this order")

    # Delete the order from the database
    db.delete(order)
    db.commit()

    return {"message": f"Order with ID: {order_id} deleted successfully"}



"""
To Assigned an order with a budget from a signed in user (user)
"""


@router.post('/pend_budget/{budget_id}', response_model=OrderOut)
async def accept_budget_by_current_user(budget_id: str, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No response made with this ID: {budget_id}")
    order = db.query(Orders).filter(Orders.order_id == budget.order_id).first()
    
    if order.status != "Accepted":
        raise HTTPException(status_code=400, detail="The Order has no bidding budget/ has been assigned")
    
    order.is_assigned = True
    order.assigned_to = order.bidding_budget
    order.status ="Pending"
    db.delete(budget)
    db.commit()
    db.refresh(order)
    return order


"""
To reject an order with a budget from a signed in user (user)
"""

@router.post('/reject_budget/{budget_id}')
async def reject_budget_by_current_user(budget_id: str, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No response made with this ID: {budget_id}")
    order = db.query(Orders).filter(Orders.order_id == budget.order_id).first()
    if order.status != "Accepted":
        raise HTTPException(status_code=400, detail="The Order has no bidding budget/ has been assigned")
  
    db.delete(budget)
    db.commit()
    
    return {"detail":"Budget Rejection Successful"}


"""
To get budget from the budget table reacted to by service_provider
"""
@router.get("/budget/accepted_service_provider", response_model=List[BudgetOut])
async def get_all_budgets_reacted_to(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    if current_user.user_type  != "user":
        raise HTTPException(status_code=403, detail="Not allowed")
    budget = db.query(Budget).filter(Budget.client_id == current_user.user_id).all()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No response from Service Provider on your request ")
    return budget



"""
To fetch assigned orders for a user/client
"""
@router.get("/orders/myAssignedOrders", response_model=List[OrderOut])
async def get_all_budget_orders_for_current_user(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    if current_user.user_type != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission for this action")
    orders = db.query(Orders).order_by(Orders.created_at).filter(and_(Orders.client_id == current_user.user_id, Orders.status =="Pending")).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No current order found")
    return orders



"""
To fetch completed orders for a user/client
"""
@router.get("/orders/myCompletedOrders", response_model=List[OrderOut])
async def get_all_budget_orders_for_current_user(db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    if current_user.user_type != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission for this action")
    orders = db.query(Orders).order_by(Orders.created_at).filter(and_(Orders.client_id == current_user.user_id, Orders.status =="Completed")).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No current order found")
    return orders



"""
To complete orders by users 
"""
@router.post("/orders/Complete_Orders/{order_id}", response_model=OrderOut)
async def to_complete_orders_by_user(order_id: str,db:Session=Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    if current_user.user_type != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission for this action")
    order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No response made with this ID: {order_id}")
    if order.status != "Pending":
        raise HTTPException(status_code=400, detail="This Order cannot be completed")
    
    order.status ="Completed"
    db.commit()
    db.refresh(order)
   
    
    return order