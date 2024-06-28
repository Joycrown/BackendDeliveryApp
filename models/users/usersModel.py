from config.database import Base
from sqlalchemy import Column, Enum, String,Numeric,JSON,Boolean,Date,ForeignKey,Integer,DateTime,event,Text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from enum import Enum 
from sqlalchemy.sql.sqltypes import Enum as PgEnum
from sqlalchemy.ext.declarative import declared_attr


class OrderType(str, Enum):
    budget = "budget"
    quote = "quote"


def update_users_is_verified(mapper, connection, target):
    if target.email_is_verified and target.profile_picture != "N/A" and target.security_question_status:
        target.is_verified = True
    else:
        target.is_verified = False



def update_serviceProvider_is_verified(mapper, connection, target):
    if target.email_is_verified and target.profile_picture != "N/A" and target.stripe_account != "N/A" and target.security_question_status:
        target.is_verified = True
    else:
        target.is_verified = False



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
    profile_picture = Column(String, nullable=False, server_default="N/A")
    email_is_verified = Column(Boolean,nullable=True,server_default='false')
    is_verified = Column(Boolean,nullable=True,server_default='false')
    user_type = Column(String,nullable=False, server_default="user")
    otp = Column(Integer)
    otp_expiry = Column(DateTime)
    security_question_1 = Column(Text, nullable=True)
    security_answer_1 = Column(String, nullable=True)
    security_question_2 = Column(Text, nullable=True)
    security_answer_2 = Column(String, nullable=True)
    security_question_status = Column(Boolean,nullable=True,server_default='false')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default= text('now()'))

event.listen(Users, 'before_insert', update_users_is_verified)
event.listen(Users, 'before_update', update_users_is_verified)





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
    profile_picture = Column(String, nullable=False, server_default="N/A")
    email_is_verified = Column(Boolean,nullable=True,server_default='false')
    is_verified = Column(Boolean,nullable=True,server_default='false')
    otp = Column(Integer)
    otp_expiry = Column(DateTime)
    security_question_1 = Column(Text, nullable=True)
    security_answer_1 = Column(String, nullable=True)
    security_question_2 = Column(Text, nullable=True)
    security_answer_2 = Column(String, nullable=True)
    security_question_status = Column(Boolean,nullable=True,server_default='false')
    stripeId_status = Column(Boolean,nullable=True,server_default='false')
    phone_no = Column(String,nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default= text('now()'))


event.listen(ServiceProvider, 'before_insert', update_serviceProvider_is_verified)
event.listen(ServiceProvider, 'before_update', update_serviceProvider_is_verified)




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



class ChatRoom(Base):
    __tablename__ = 'chat_rooms'

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(String, nullable=False)
    sender_type = Column(String, nullable=False)
    receiver_id = Column(String, nullable=False)
    receiver_type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    @declared_attr
    def sender(cls):
        return relationship(
            'Users',
            primaryjoin='and_(ChatRoom.sender_id == Users.user_id, ChatRoom.sender_type == "user")',
            foreign_keys=[cls.sender_id],
            uselist=False,overlaps="sender_provider"
        )

    @declared_attr
    def sender_provider(cls):
        return relationship(
            'ServiceProvider',
            primaryjoin='and_(ChatRoom.sender_id == ServiceProvider.service_provider_id, ChatRoom.sender_type == "service_provider")',
            foreign_keys=[cls.sender_id],
            uselist=False,
            overlaps="sender"
        )

    @declared_attr
    def receiver(cls):
        return relationship(
            'Users',
            primaryjoin='and_(ChatRoom.receiver_id == Users.user_id, ChatRoom.receiver_type == "user")',
            foreign_keys=[cls.receiver_id],
            uselist=False,
            overlaps="receiver_provider"
        )

    @declared_attr
    def receiver_provider(cls):
        return relationship(
            'ServiceProvider',
            primaryjoin='and_(ChatRoom.receiver_id == ServiceProvider.service_provider_id, ChatRoom.receiver_type == "service_provider")',
            foreign_keys=[cls.receiver_id],
            uselist=False,
            overlaps="receiver"
        )

    messages = relationship("Messages", back_populates="chat_room")




class Messages(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_room_id = Column(Integer, ForeignKey('chat_rooms.room_id'), nullable=False)
    sender_id = Column(String, nullable=False)
    sender_type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    chat_room = relationship("ChatRoom", back_populates="messages")

    @declared_attr
    def sender(cls):
        return relationship(
            'Users',
            primaryjoin='and_(Messages.sender_id == Users.user_id, Messages.sender_type == "user")',
            foreign_keys=[cls.sender_id],
            uselist=False,
            overlaps="sender_provider"
        )

    @declared_attr
    def sender_provider(cls):
        return relationship(
            'ServiceProvider',
            primaryjoin='and_(Messages.sender_id == ServiceProvider.service_provider_id, Messages.sender_type == "service_provider")',
            foreign_keys=[cls.sender_id],
            uselist=False,
            overlaps="sender"
        )