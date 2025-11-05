from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core.config import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.subscription import Subscription
from typing import Dict, Any
import json

from app.services.payment import payment_service
from app.services.subscription import subscription_service
from app.services.token import get_token_service
from app.models.transaction import Transaction

router = APIRouter()

@router.post("/paypal/create-order")
async def create_paypal_order(request: Dict[str, Any], db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    try:
        amount = request.get("amount", 1000)
        plan_id = request.get("plan")
 
        try:
            plan_id = int(plan_id) if plan_id is not None else None
        except Exception:
            plan_id = None
        result = payment_service.create_paypal_order(amount_paise=amount, user_id=current_user.id, plan_id=plan_id, db=db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating payment order: {str(e)}")


@router.post("/paypal/webhook")
async def paypal_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.body()
        result = payment_service.handle_paypal_webhook(body=body, db=db, SubscriptionModel=Subscription)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@router.post("/paypal/order-status")
async def paypal_order_status(request: Dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        merchant_order_id = request.get("orderId") or request.get("merchantOrderId")
        if not merchant_order_id:
            raise HTTPException(status_code=422, detail="orderId is required")
        result = payment_service.get_order_status(
            merchant_order_id=merchant_order_id,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order status: {str(e)}")


@router.get("/paypal/order-status/{orderId}")
async def paypal_order_status_by_id(orderId: str, planId: int | None = Query(default=None), db: Session = Depends(get_db)):
    try:
        if not orderId:
            raise HTTPException(status_code=422, detail="orderId is required")
        
        txn = (
                 db.query(Transaction)
                .filter(Transaction.merchant_order_id == orderId).first()
                        )
        result = payment_service.get_order_status(
            merchant_order_id=orderId,
            
        )
        # If completed, finalize transaction, subscription, and tokens
        try:
            if result.get("success") and isinstance(result.get("data"), dict):
                state = result["data"].get("status")  # PayPal order status
                if state == "COMPLETED":
                    # Resolve plan id: prefer query param; else derive from stored transaction
                    resolved_plan_id = planId
                    if resolved_plan_id is None:
                        try:
                            resolved_plan_id = payment_service.get_plan_id_by_transaction_id(merchant_order_id=orderId, db=db)
                        except Exception:
                            resolved_plan_id = None

                    # Update transaction status to COMPLETED and persist gateway details
                    try:
                        if txn:
                            txn.status = "COMPLETED"
                            txn.payment_mode = "paypal"
                            txn.response_payload = result["data"]
                            db.commit()
                    except Exception:
                        pass

                    # Create or update subscription if we have a plan id
                    subscription = None
                    if resolved_plan_id is not None and txn is not None:
                        subscription = subscription_service.upsert_on_payment_success(db, user_id=txn.user_id, plan_id=int(resolved_plan_id))

                        # Allocate tokens from plan to user
                        try:
                            token_service = get_token_service(db)
                            token_service.allocate_tokens_from_plan(user_id=txn.user_id, subscription_id=subscription.id)
                        except Exception as e:
                            print(f"Token allocation error for user {txn.user_id}, subscription {subscription.id}: {e}")
                    else:
                        try:
                            print(f"No resolved_plan_id for order_id={orderId}")
                        except Exception:
                            pass

                    return {
                        "success": True,
                        "data": result["data"],
                        "subscriptionId": subscription.id if subscription else None,
                        "planId": int(resolved_plan_id) if resolved_plan_id is not None else None,
                    }
        except Exception:
            pass
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order status: {str(e)}")
