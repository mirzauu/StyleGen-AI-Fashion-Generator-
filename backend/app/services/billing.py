from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.subscription import Subscription
from app.models.plan import Plan
from app.core.config import settings


class BillingService:
    def __init__(self, db: Session):
        self.db = db

    def create_checkout_session(self, user_id: int, plan_id: int):
        plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise ValueError("Plan not found")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=settings.FRONTEND_URL + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.FRONTEND_URL + "/cancel",
        )
        return session

    def handle_webhook(self, event):
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            self._create_subscription(session)

    def _create_subscription(self, session):
        user_id = session["client_reference_id"]
        plan_id = session["line_items"]["data"][0]["price"]["id"]

        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            status="active",
            current_period_end=session["current_period_end"],
        )

        try:
            self.db.add(subscription)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Subscription already exists")