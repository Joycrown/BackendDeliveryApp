from config.database import Base
from sqlalchemy import Column, Enum, String,Numeric,JSON,Boolean,Date,ForeignKey,Integer
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from enum import Enum 
from sqlalchemy.sql.sqltypes import Enum as PgEnum



class OrderType(str, Enum):
    budget = "budget"
    quote = "quote"


class Users(Base):
    __tablename__ = 'users'


    user_id = Column(String, unique=True,primary_key=True, nullable=False)
    full_name = Column(String, nullable=False)
    type = Column(String,nullable=False)
    company_name = Column(String,nullable=False,server_default='N/A')
    company_url = Column(String,nullable=False,server_default='N/A')
    email = Column(String,nullable=False, unique=True)
    country = Column(String,nullable=False,server_default='N/A')
    password = Column(String,nullable=False)
    phone_no = Column(String,nullable=False)
    is_verified = Column(Boolean,nullable=True,server_default='false')
    user_type = Column(String,nullable=False, server_default="user")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default= text('now()'))





class ServiceProvider(Base):
    __tablename__= 'serviceProvider'



    service_provider_id = Column(String, unique=True,primary_key=True, nullable=False)
    full_name = Column(String, nullable=False)
    type = Column(String,nullable=False)
    company_name = Column(String,nullable=False,server_default='N/A')
    company_url = Column(String,nullable=False,server_default='N/A')
    email = Column(String,nullable=False, unique=True)
    password = Column(String,nullable=False)
    service_offered = Column(String,nullable=False)
    street_address = Column(String,nullable=False)
    city = Column(String,nullable=False)
    country = Column(String,nullable=False)
    stripe_account = Column(String, nullable=False, server_default="N/A")
    rating = Column(String,nullable=False,server_default="N/A")
    gender = Column(String,nullable=False)
    user_type = Column(String,nullable=True, server_default="service provider")
    is_verified = Column(Boolean,nullable=True,server_default='false')
    phone_no = Column(Numeric,nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default= text('now()'))






class Orders(Base):
    __tablename__ = 'orders'

    order_id = Column(String, unique=True,primary_key=True, nullable=False)
    order_title = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    equipment_Category = Column(String, nullable=False)
    equipment_type = Column(String, nullable=False)
    dimension_length = Column(String,nullable=False, server_default="N/A")
    dimension_width = Column(String,nullable=False, server_default="N/A")
    dimension_weight = Column(String,nullable=False, server_default="N/A")
    dimension_height = Column(String,nullable=False, server_default="N/A")
    trailer_preference = Column(Boolean, nullable=False)
    on_trailer = Column(Boolean, nullable=False)
    collection_area = Column(String,nullable=False)
    collection_location = Column(String,nullable=False)
    loading_assistance = Column(Boolean, nullable=False)
    date_of_collection = Column(String,nullable=False)
    delivery_area = Column(String,nullable=False)
    delivery_location = Column(String,nullable=False)
    off_loading_assistance = Column(Boolean, nullable=False)
    date_of_delivery = Column(String,nullable=False)
    is_assigned = Column(Boolean,  default=False)
    is_completed = Column(Boolean,  default=False)
    no_of_pieces = Column(Numeric, nullable=False, server_default='0')
    order_type = Column(String, nullable=False, server_default="budget")
    bidding_budget =Column(String, nullable=False, server_default="N/A")
    assigned_to =Column(String, ForeignKey("serviceProvider.service_provider_id"), nullable=True)
    client_id = Column(String,ForeignKey("users.user_id"))
    quote_id = Column(String,ForeignKey("quotes.quote_id"))
    budget = Column(String, server_default="N/A")
    payment_intent_id = Column(String, server_default="N/A")
    status = Column(String, nullable=False, server_default="No Reaction")
    rejectedServiceProvider = Column(JSON)  # Add this column to save lists of service_provider_ids
    is_budget =Column(Boolean,  default=True)
    quotes = relationship("Quote", back_populates="order",foreign_keys=[quote_id])
    client = relationship("Users",foreign_keys=[client_id])
    carrier = relationship("ServiceProvider",foreign_keys=[assigned_to])
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default= text('now()'))
   


class Quote(Base):
    __tablename__ = 'quotes'

    quote_id = Column(String, unique=True, primary_key=True, nullable=False)
    service_provider_id = Column(String, ForeignKey("serviceProvider.service_provider_id",ondelete="CASCADE"), nullable=False)
    order_id = Column(String, ForeignKey("orders.order_id",ondelete="CASCADE"), nullable=False)
    quote_amount = Column(String, nullable=False)
    is_accepted = Column(Boolean, default=False)
    status = Column(String, nullable=False, server_default='Pending')
    client_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(Date, nullable=False, server_default=text('now()'))

    
    # Define a relationship to the Orders table
    order = relationship("Orders", foreign_keys=[order_id])
    service_provider= relationship("ServiceProvider", foreign_keys=[service_provider_id])



class Budget(Base):
    __tablename__ = 'budgets'

    budget_id = Column(String, unique=True, primary_key=True, nullable=False)
    service_provider_id = Column(String, ForeignKey("serviceProvider.service_provider_id",ondelete="CASCADE"), nullable=False)
    order_id = Column(String, ForeignKey("orders.order_id",ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(Date, nullable=False, server_default=text('now()'))
    order = relationship("Orders", foreign_keys=[order_id])
    service_provider= relationship("ServiceProvider", foreign_keys=[service_provider_id])
    client= relationship("Users", foreign_keys=[client_id])






class RejectedOrder(Base):
    __tablename__ = 'rejectedOrder'

    id = Column(Integer,primary_key=True,)
    service_provider_id = Column(String, ForeignKey("serviceProvider.service_provider_id",ondelete="CASCADE"), nullable=False)
    order_id = Column(String, ForeignKey("orders.order_id",ondelete="CASCADE"), nullable=False)
    created_at = Column(Date, nullable=False, server_default=text('now()'))
    status = Column(String, nullable=False)
    order = relationship("Orders", foreign_keys=[order_id])
    service_provider= relationship("ServiceProvider", foreign_keys=[service_provider_id])




class PaymentStatus(str, PgEnum):
    PAID_TO_COMPANY = "escrow"
    COMPLETED = "completed"

class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id = Column(String, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    description = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    transporter_email = Column(String, nullable=False)
    status = Column(String, nullable=False)