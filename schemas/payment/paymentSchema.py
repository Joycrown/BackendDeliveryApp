from pydantic import BaseModel



class PaymentRequest(BaseModel):
    amount: int
    currency: str
    order_id : str
    description: str
    customer_email: str
    transporter_email: str


class ConfirmDeliveryRequest(BaseModel):
    payment_intent_id: str
   

