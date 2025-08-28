# from fastapi.testclient import TestClient
# from app.main import app
# from app.models.plan import Plan
# from app.models.subscription import Subscription
# from app.models.user import User
# from app.schemas.plan import PlanCreate
# from app.schemas.subscription import SubscriptionCreate
# from app.core.utils import get_password_hash
# from sqlalchemy.orm import Session

# client = TestClient(app)

# def create_test_user(db: Session):
#     user = User(email="testuser@example.com", password_hash=get_password_hash("password"))
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user

# def create_test_plan(db: Session):
#     plan = Plan(name="Basic Plan", price=9.99, limits="5 batches per month")
#     db.add(plan)
#     db.commit()
#     db.refresh(plan)
#     return plan

# def test_get_plans(db: Session):
#     create_test_plan(db)
#     response = client.get("/plans/")
#     assert response.status_code == 200
#     assert len(response.json()) > 0

# def test_create_subscription(db: Session):
#     user = create_test_user(db)
#     plan = create_test_plan(db)
#     subscription_data = SubscriptionCreate(user_id=user.id, plan_id=plan.id)
#     response = client.post("/subscriptions/", json=subscription_data.dict())
#     assert response.status_code == 201
#     assert response.json()["user_id"] == user.id
#     assert response.json()["plan_id"] == plan.id

# def test_get_subscription(db: Session):
#     user = create_test_user(db)
#     plan = create_test_plan(db)
#     subscription_data = SubscriptionCreate(user_id=user.id, plan_id=plan.id)
#     client.post("/subscriptions/", json=subscription_data.dict())
#     response = client.get(f"/subscriptions/{user.id}/")
#     assert response.status_code == 200
#     assert response.json()["user_id"] == user.id
#     assert response.json()["plan_id"] == plan.id