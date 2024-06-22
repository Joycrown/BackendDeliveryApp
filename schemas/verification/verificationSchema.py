from typing import List,Optional
from pydantic import BaseModel, EmailStr




class SecurityQuestionAnswer(BaseModel):
    question: str
    answer: str

class SecurityQuestionsUpdate(BaseModel):
    security_questions: List[SecurityQuestionAnswer]


class SecurityAnswer(BaseModel):
    question: str
    answer: str

class SecurityCheck(BaseModel):
    answers: List[SecurityAnswer]
    stripe_id: Optional[str]

    

class SecurityQuestion(BaseModel):
    question: str



class StripeIn(BaseModel):
    stripe_id: str
