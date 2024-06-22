from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 
from config.database import get_db
from config import stripe
from models.users.usersModel import ServiceProvider,Orders
from schemas.payment.paymentSchema import PaymentRequest,ConfirmDeliveryRequest
from models.users.usersModel import PaymentIntent, PaymentStatus
from schemas.user.usersSchema import UserOut
from apps.users.auth import get_current_user 

router = APIRouter(
    tags=["Payment"]
)


@router.post("/create-payment-intent/")
async def create_payment_intent(payment_request: PaymentRequest, db: Session = Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    try:
        payment_intent = stripe.stripe.PaymentIntent.create(
            amount=payment_request.amount,
            currency=payment_request.currency,
            description=payment_request.description,
            receipt_email=payment_request.customer_email,
            payment_method_types=["card"],
            capture_method='automatic',  # Capture automatically
        )
        payment_intent_record = PaymentIntent(
            id=payment_intent['id'],
            amount=payment_request.amount,
            currency=payment_request.currency,
            description=payment_request.description,
            customer_email=payment_request.customer_email,
            transporter_email=payment_request.transporter_email,
            status=PaymentStatus.PAID_TO_COMPANY
        )
        order = db.query(Orders).filter(Orders.order_id == payment_request.order_id).first()
        order.payment_intent_id = payment_intent_record.id
        db.add(payment_intent_record)
        db.commit()
        db.refresh(payment_intent_record)
        db.refresh(order)
        return {"client_secret": payment_intent['client_secret']}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    





@router.post("/confirm-delivery/{order_id}")
async def confirm_delivery(order_id:str, db: Session = Depends(get_db),current_user: UserOut = Depends(get_current_user)):
    order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="payment has not been received for this order")
    payment_record = db.query(PaymentIntent).filter(PaymentIntent.id == order.payment_intent_id).first()
    if not payment_record or payment_record.status != PaymentStatus.PAID_TO_COMPANY:
        raise HTTPException(status_code=400, detail="Invalid payment intent or not paid to company")
    transporter_details = db.query(ServiceProvider).filter(ServiceProvider.email == payment_record.transporter_email).first()
    if not transporter_details:
        raise HTTPException(status_code=400, detail="No transporter found")
    try:
        # Create a transfer to the transporter's connected account
        transfer = stripe.stripe.Transfer.create(
            amount=payment_record.amount,
            currency=payment_record.currency,
            destination=transporter_details.stripe_account,
            transfer_group=order.payment_intent_id,
        )

        # Update payment status
        payment_record.status = PaymentStatus.COMPLETED
        db.commit()

        return {"status": "success", "transfer_id": transfer.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




