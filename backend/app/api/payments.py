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

@router.post("/create-phonepe-order")
async def create_phonepe_order(request: Dict[str, Any], db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    try:
        amount = request.get("amount", 1000)
        plan_id = request.get("plan")
        try:
            plan_id = int(plan_id) if plan_id is not None else None
        except Exception:
            plan_id = None
        result = payment_service.create_phonepe_order(amount_paise=amount, user_id=current_user.id, plan_id=plan_id, db=db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating payment order: {str(e)}")

    
@router.post("/phonepe-webhook")
async def phonepe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle PhonePe webhook notifications"""
    try:
        body = await request.body()
        result = payment_service.handle_phonepe_webhook(body=body, db=db, SubscriptionModel=Subscription)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@router.post("/phonepe-order-status")
async def phonepe_order_status(request: Dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        merchant_order_id = request.get("merchantOrderId")
        access_token = request.get("accessToken")
        token_type = request.get("tokenType")
        if not merchant_order_id:
            raise HTTPException(status_code=422, detail="merchantOrderId is required")
        result = payment_service.get_order_status(
            merchant_order_id=merchant_order_id,
            access_token=access_token,
            token_type=token_type,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order status: {str(e)}")


@router.get("/phonepe-order-status/{transactionId}")
async def phonepe_order_status_by_id(transactionId: str, planId: int | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if not transactionId:
            raise HTTPException(status_code=422, detail="transactionId is required")
        result = payment_service.get_order_status(
            merchant_order_id=transactionId,
            access_token=None,
            token_type=None,
        )
        # If completed, finalize transaction, subscription, and tokens
        try:
            if result.get("success") and isinstance(result.get("data"), dict):
                state = result["data"].get("state")
                if state == "COMPLETED":
                    # Resolve plan id: prefer query param; else derive from stored transaction
                    resolved_plan_id = planId
                    if resolved_plan_id is None:
                        try:
                            resolved_plan_id = payment_service.get_plan_id_by_transaction_id(merchant_order_id=transactionId, db=db)
                        except Exception:
                            resolved_plan_id = None

                    # Update transaction status to COMPLETED and persist gateway details
                    try:
                        details_list = result["data"].get("paymentDetails")
                        payment_details = details_list[0] if isinstance(details_list, list) and len(details_list) > 0 else None
                        gateway_txn_id = payment_details.get("transactionId") if isinstance(payment_details, dict) else None
                        payment_mode = payment_details.get("paymentMode") if isinstance(payment_details, dict) else None

                        txn = (
                            db.query(Transaction)
                            .filter(Transaction.merchant_order_id == transactionId)
                            .first()
                        )
                        if txn:
                            txn.status = "COMPLETED"
                            txn.gateway_transaction_id = gateway_txn_id
                            txn.payment_mode = payment_mode
                            txn.response_payload = result["data"]
                            db.commit()
                    except Exception:
                        pass

                    # Create or update subscription if we have a plan id
                    subscription = None
                    if resolved_plan_id is not None:
                        subscription = subscription_service.upsert_on_payment_success(db, user_id=current_user.id, plan_id=int(resolved_plan_id))

                        # Allocate tokens from plan to user
                        try:
                            token_service = get_token_service(db)
                            token_service.allocate_tokens_from_plan(user_id=current_user.id, subscription_id=subscription.id)
                        except Exception as e:
                            # Debug why token allocation failed
                            print(f"Token allocation error for user {current_user.id}, subscription {subscription.id}: {e}")
                    else:
                        # Debug missing plan id
                        try:
                            print(f"No resolved_plan_id for merchant_order_id={transactionId}")
                        except Exception:
                            pass

                    return {
                        "success": True,
                        "data": result["data"],
                        "subscriptionId": subscription.id if subscription else None,
                        "planId": int(resolved_plan_id) if resolved_plan_id is not None else None,
                    }
        except Exception:
            # Do not fail status fetch if subscription creation fails; surface original status
            pass
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order status: {str(e)}")
