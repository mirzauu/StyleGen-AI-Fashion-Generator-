from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionBase(BaseModel):
    user_id: int
    plan_id: int
    status: str
    current_period_end: datetime



class SubscriptionUpdate(SubscriptionBase):
    status: Optional[str] = None
    current_period_end: Optional[datetime] = None

class Subscription(SubscriptionBase):
    id: int

    class Config:
        orm_mode = True

class SubscriptionResponse(Subscription):
    pass



from pydantic import BaseModel
from datetime import datetime

class SubscriptionCreate(BaseModel):
    plan_id: int   # user chooses which plan to subscribe to

class SubscriptionOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: str
    current_period_end: datetime

    class Config:
        orm_mode = True
