from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import  Orders,ServiceProvider,Budget,RejectedOrder,Quote
from schemas.order.orderSchema import OrderOut,ServiceProviderOut,BudgetOut,QuoteOut
from apps.users.auth import get_current_user
from config.database import get_db
from sqlalchemy.orm import Session 
from sqlalchemy import and_,desc
from typing import List, Union






router= APIRouter(
    tags=["Service Providers Budget"]
)


def generate_custom_id(prefix: str, n_digits: int) -> str:
    """Generate a custom ID with a given prefix and a certain number of random digits"""
    random_digits = ''.join([str(random.randint(0,9)) for i in range(n_digits)])
    return f"{prefix}{random_digits}"


"""
To get all order made
"""
@router.get("/all_orders", response_model=List[OrderOut])
async def get_all_orders(db:Session=Depends(get_db),current_user: ServiceProvider = Depends(get_current_user)):
    if current_user.user_type  != "service provider":
        raise HTTPException(status_code=403, detail="Not allowed")
    rejected_order_ids = [rejected_order.order_id for rejected_order in db.query(RejectedOrder).filter(RejectedOrder.service_provider_id == current_user.service_provider_id)]
    # Query all orders excluding the rejected ones
    quotes_id = [quote_id.order_id for quote_id in db.query(Quote).filter(Quote.order_id == Orders.order_id)]
    orders = db.query(Orders).order_by(desc(Orders.created_at)).filter(and_(Orders.status == "No Reaction", ~Orders.order_id.in_(rejected_order_ids),~Orders.order_id.in_(quotes_id)))
    return orders


"""
To get all budget order made
"""
@router.get("/all_orders/budget", response_model=List[OrderOut])
async def get_all_budget_orders_from_all_users(db:Session=Depends(get_db),current_user: ServiceProvider = Depends(get_current_user)):
    if current_user.user_type  != "service provider":
        raise HTTPException(status_code=403, detail="Not allowed")
    rejected_order_ids = [rejected_order.order_id for rejected_order in db.query(RejectedOrder).filter(RejectedOrder.service_provider_id == current_user.service_provider_id)]
    orders = db.query(Orders).order_by(desc(Orders.created_at)).filter(and_(Orders.order_type == "budget",Orders.status == "No Reaction", ~Orders.order_id.in_(rejected_order_ids)))
  
    return orders


"""
To get all quote orders made
"""
@router.get("/all_orders/quote", response_model=List[OrderOut])
async def get_all_quote_orders_from_all_users(db:Session=Depends(get_db),current_user: ServiceProvider = Depends(get_current_user)):
    if current_user.user_type  != "service provider":
        raise HTTPException(status_code=403, detail="Not allowed")
    rejected_order_ids = [rejected_order.order_id for rejected_order in db.query(RejectedOrder).filter(RejectedOrder.service_provider_id == current_user.service_provider_id)]
    quotes_id = [quote_id.order_id for quote_id in db.query(Quote).filter(Quote.order_id == Orders.order_id)]
    orders = db.query(Orders).order_by(desc(Orders.created_at)).filter(and_(Orders.order_type == "quote",Orders.status == "No Reaction", ~Orders.order_id.in_(rejected_order_ids),~Orders.order_id.in_(quotes_id)))

    return orders





# """
# To fetch the order by type (Budget) for a user
# """
# @router.get("/orders/budget", response_model=List[OrderOut])
# async def get_all_budget_orders_for_current_user(db:Session=Depends(get_db),current_user: ServiceProvider = Depends(get_current_user)):
#     if current_user.user_type != "service provider":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission for this action")
#     orders = db.query(Orders).order_by(Orders.created_at).filter(and_(Orders.client_id == current_user.service_provider_id, Orders.order_type =="budget")).all()
#     if not orders:
#         raise HTTPException(status_code=404, detail="No current order found")
#     return orders


"""
To accept an order with budget by service provider
"""


@router.post('/accept_budget/{order_id}', response_model=OrderOut)
async def accept_budget_as_service_provider(order_id: str, db: Session = Depends(get_db), current_user: ServiceProviderOut = Depends(get_current_user)):
    if current_user.user_type != "service provider":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't react to this order")
    order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with ID: {order_id} found")
    if order.order_type != "budget":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Order is not a budget but needs a quote ")
    if order.status ==  "Pending" or order.status =="Completed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="This order has already been completed/Assigned.")
    budget = db.query(Budget).filter((Budget.order_id == order_id) & (Budget.service_provider_id == current_user.service_provider_id)).first()
    if budget:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="You have already reacted to this order.")
    order.status ="Accepted"
    custom_id = generate_custom_id("Budget", 5)
    new_budget = Budget(service_provider_id = current_user.service_provider_id,
    status=order.status, 
    order_id=order.order_id,
    client_id = order.client_id,
    amount=order.budget,budget_id=custom_id)
    order.bidding_budget= current_user.service_provider_id
    db.add(new_budget)
    db.commit()
    db.refresh(order)
    db.refresh(new_budget)
    return order


"""
To fetch the order by type (Quote) for a user
"""
@router.get("/orders/quote", response_model=List[OrderOut])
async def get_all_quote_orders_from_current_user(db:Session=Depends(get_db),current_user: ServiceProvider = Depends(get_current_user)):
    if current_user.user_type != "service provider":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission for this action")
    orders = db.query(Orders).order_by(desc(Orders.created_at)).filter(and_(Orders.client_id == current_user.user_id, Orders.order_type =="quote")).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No current order(S) found")
    return orders

"""
To reject a user order(quote/budget) by a service provider 
"""

@router.post('/service_providers/reject_orders/{order_id}')
async def reject_orders_by_service_provider(order_id: str, db: Session = Depends(get_db), current_user: ServiceProviderOut = Depends(get_current_user)):
    order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this ID: {order_id}")
    if order.status != "No Reaction":
        raise HTTPException(status_code=400, detail="The Order has been accepted/assigned")
    if current_user.user_type != "service provider":
        raise HTTPException(status_code=400, detail="Not allowed")
    rejected_order= RejectedOrder(service_provider_id=current_user.service_provider_id,order_id=order_id,status="Rejected")
    
    db.add(rejected_order)
    db.commit()
    db.refresh(rejected_order)
    
    return {"message": "Service provider rejected successfully"}





"""
To get all pending orders (Quote and Budget) made
"""
@router.get("/pending/all_orders", response_model=List[Union[BudgetOut, QuoteOut]])
async def get_all_pending_orders(db:Session=Depends(get_db),current_user: ServiceProvider = Depends(get_current_user)):
    if current_user.user_type  != "service provider":
        raise HTTPException(status_code=403, detail="Not allowed")
    budget_orders = db.query(Budget).filter(
        Budget.status == "Accepted",
        Budget.service_provider_id == current_user.service_provider_id
    ).all()
    # Query Quote orders
    quote_orders = db.query(Quote).filter(
        Quote.status == "Accepted",
        Quote.service_provider_id == current_user.service_provider_id
    ).all()
    # Combine both types of orders
    all_orders = budget_orders + quote_orders
    
    return all_orders


"""
To fetch assigned orders for a service provider
"""
@router.get("/orders/assignedOrders", response_model=List[OrderOut])
async def get_all_budget_orders_for_current_user(db:Session=Depends(get_db),current_user: ServiceProvider = Depends(get_current_user)):
    if current_user.user_type != "service provider":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission for this action")
    orders = db.query(Orders).order_by(desc(Orders.created_at)).filter(and_(Orders.assigned_to == current_user.service_provider_id, Orders.status =="Pending")).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No current order found")
    return orders



"""
To fetch completed orders for a service provider
"""
@router.get("/orders/completedOrders", response_model=List[OrderOut])
async def get_all_budget_orders_for_current_user(db:Session=Depends(get_db),current_user: ServiceProvider = Depends(get_current_user)):
    if current_user.user_type != "service provider":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission for this action")
    orders = db.query(Orders).order_by(desc(Orders.created_at)).filter(and_(Orders.assigned_to == current_user.service_provider_id, Orders.status =="Completed")).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No current order found")
    return orders