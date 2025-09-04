from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.plan import Plan


class SubscriptionService:
    """Manage user subscriptions: creation, validity, updates, and plan changes."""

    def _get_plan_duration_days(self, plan: Plan) -> int:
        limits = getattr(plan, "limits", None) or {}
        duration_days = limits.get("duration_days") if isinstance(limits, dict) else None
        return int(duration_days) if duration_days is not None else 30

    def get_active_subscription(self, db: Session, user_id: int) -> Optional[Subscription]:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .first()
        )
        if not subscription:
            return None
        if subscription.status != "active":
            return None
        if subscription.current_period_end and subscription.current_period_end <= datetime.utcnow():
            return None
        return subscription

    def is_subscription_valid(self, db: Session, user_id: int, at: Optional[datetime] = None) -> bool:
        reference_time = at or datetime.utcnow()
        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .first()
        )
        if not subscription:
            return False
        if subscription.status != "active":
            return False
        if subscription.current_period_end is None:
            return False
        return subscription.current_period_end > reference_time

    def create_subscription_by_plan_id(
        self,
        db: Session,
        *,
        user_id: int,
        plan_id: int,
        start_time: Optional[datetime] = None,
    ) -> Subscription:
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if plan is None:
            raise ValueError(f"Plan with id {plan_id} not found")

        start = start_time or datetime.utcnow()
        duration_days = self._get_plan_duration_days(plan)
        end = start + timedelta(days=duration_days)

        # Upsert behavior: update existing or create new
        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .first()
        )
        if subscription:
            subscription.plan_id = plan.id
            subscription.status = "active"
            subscription.current_period_end = end
        else:
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan.id,
                status="active",
                current_period_end=end,
            )
            db.add(subscription)

        db.commit()
        db.refresh(subscription)
        return subscription

    def cancel_subscription(self, db: Session, *, user_id: int) -> Optional[Subscription]:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .first()
        )
        if not subscription:
            return None
        subscription.status = "canceled"
        subscription.current_period_end = datetime.utcnow()
        db.commit()
        db.refresh(subscription)
        return subscription

    def extend_subscription(self, db: Session, *, user_id: int, extra_days: int) -> Optional[Subscription]:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .first()
        )
        if not subscription:
            return None
        now = datetime.utcnow()
        current_end = subscription.current_period_end or now
        base = current_end if current_end > now else now
        subscription.current_period_end = base + timedelta(days=int(extra_days))
        subscription.status = "active"
        db.commit()
        db.refresh(subscription)
        return subscription

    def change_plan(self, db: Session, *, user_id: int, new_plan_id: int) -> Subscription:
        plan = db.query(Plan).filter(Plan.id == new_plan_id).first()
        if plan is None:
            raise ValueError(f"Plan with id {new_plan_id} not found")

        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .first()
        )
        if not subscription:
            # Create a fresh subscription if none exists
            return self.create_subscription_by_plan_id(db, user_id=user_id, plan_id=new_plan_id)

        duration_days = self._get_plan_duration_days(plan)
        subscription.plan_id = plan.id
        subscription.status = "active"
        subscription.current_period_end = datetime.utcnow() + timedelta(days=duration_days)
        db.commit()
        db.refresh(subscription)
        return subscription

    def upsert_on_payment_success(self, db: Session, *, user_id: int, plan_id: int) -> Subscription:
        """Helper to be called when a payment succeeds to activate/update subscription."""
        return self.create_subscription_by_plan_id(db, user_id=user_id, plan_id=plan_id)


subscription_service = SubscriptionService()


