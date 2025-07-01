from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionBase(BaseModel):
    user_id: int
    plan_id: int
    status: str
    current_period_end: datetime

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(SubscriptionBase):
    status: Optional[str] = None
    current_period_end: Optional[datetime] = None

class Subscription(SubscriptionBase):
    id: int

    class Config:
        orm_mode = True

class SubscriptionResponse(Subscription):
    pass
class SubscriptionOut(Subscription):
    pass