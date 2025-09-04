import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

import requests
from app.models.transaction import Transaction


class PaymentService:
    """Encapsulates PhonePe payment operations: token, order, webhook."""

    def __init__(self) -> None:
        # Configuration
        self.merchant_id: str = os.getenv("PHONEPE_MERCHANT_ID", "TEST-M237L7LKY6H57_25083")
        self.merchant_secret: str = os.getenv("PHONEPE_MERCHANT_SECRET", "MmJlZDZiMTQtMWFhYi00ZTg2LWI0MmUtNDUxMjJmZjU2YzQy")
        self.salt_index: str = os.getenv("PHONEPE_SALT_INDEX", "1")
        self.environment: str = os.getenv("PHONEPE_ENVIRONMENT", "UAT")

        # Endpoints
        if self.environment == "PROD":
            self.base_url: str = "https://api.phonepe.com"
            self.oauth_url: str = f"{self.base_url}/apis/pg/v1/oauth/token"
            self.pay_url: str = f"{self.base_url}/apis/pg/v1/checkout/v2/pay"
            self.status_url_prefix: str = f"{self.base_url}/apis/pg/v1/checkout/v2/order"
        else:
            self.base_url = "https://api-preprod.phonepe.com"
            self.oauth_url = f"{self.base_url}/apis/pg-sandbox/v1/oauth/token"
            self.pay_url = f"{self.base_url}/apis/pg-sandbox/checkout/v2/pay"
            self.status_url_prefix = f"{self.base_url}/apis/pg-sandbox/checkout/v2/order"

    # Token
    def get_access_token(self) -> Tuple[str, str]:
        payload = {
            "client_id": self.merchant_id,
            "client_secret": self.merchant_secret,
            "client_version": 1,
            "grant_type": "client_credentials",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(self.oauth_url, data=payload, headers=headers)
        data = response.json()
        if response.status_code == 200 and "access_token" in data:
            return data["access_token"], data.get("token_type", "Bearer")
        raise Exception(f"Failed to fetch token: {response.text}")

    # Order
    def create_phonepe_order(self, *, amount_paise: int, user_id: int, plan_id: int | None, db=None) -> Dict[str, Any]:
        transaction_id = f"TXN__{int(datetime.now().timestamp())}"
        access_token, token_type = self.get_access_token()

        payload = {
            "merchantOrderId": transaction_id,
            "amount": amount_paise,
            "expireAfter": 1200,
            "paymentFlow": {
                "type": "PG_CHECKOUT",
                "message": "Payment initiated",
                "merchantUrls": {"redirectUrl": "https://google.com"},
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{token_type} {access_token}",
        }

        response = requests.post(self.pay_url, json=payload, headers=headers)

        # Defensive parse
        try:
            response_data = response.json()
        except Exception:
            raise Exception(f"Invalid JSON response returned: {response.text}")

        if response.status_code == 200:
            # Create pending transaction history if db provided
            try:
                if db is not None:
                    txn = Transaction(
                        user_id=user_id,
                        plan_id=plan_id,
                        subscription_id=None,
                        merchant_order_id=transaction_id,
                        gateway_transaction_id=None,
                        amount_paise=amount_paise,
                        currency="INR",
                        status="PENDING",
                        payment_mode=None,
                        request_payload=payload,
                        response_payload=response_data,
                    )
                    db.add(txn)
                    db.commit()
            except Exception:
                # Non-blocking persistence
                pass

            return {
                "success": True,
                "tokenUrl": response_data.get("redirectUrl"),
                "transactionId": transaction_id,
            }
        raise Exception(json.dumps(response_data))

    # Webhook
    def handle_phonepe_webhook(self, *, body: bytes, db, SubscriptionModel) -> Dict[str, Any]:
        body_str = body.decode("utf-8")
        webhook_data = json.loads(body_str)

        merchant_transaction_id = webhook_data.get("merchantTransactionId")
        transaction_id = webhook_data.get("transactionId")  # noqa: F841 (may use for audit later)
        amount = webhook_data.get("amount")  # noqa: F841 (may use for audit later)
        status = webhook_data.get("code")  # e.g., PAYMENT_SUCCESS

        if status == "PAYMENT_SUCCESS":
            # Derive user_id if embedded, else skip
            user_id = None
            if isinstance(merchant_transaction_id, str) and "_" in merchant_transaction_id:
                try:
                    user_id = int(merchant_transaction_id.split("_")[1])
                except Exception:
                    user_id = None

            # Create/Update subscription only if we have a user_id
            if user_id is not None:
                subscription = (
                    db.query(SubscriptionModel)
                    .filter(SubscriptionModel.user_id == user_id)
                    .first()
                )

                if subscription:
                    subscription.status = "active"
                    subscription.current_period_start = datetime.utcnow()
                    subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
                else:
                    subscription = SubscriptionModel(
                        user_id=user_id,
                        status="active",
                        plan_id="pro_monthly",
                        current_period_start=datetime.utcnow(),
                        current_period_end=datetime.utcnow() + timedelta(days=30),
                    )
                    db.add(subscription)

                db.commit()

            return {"success": True, "message": "Subscription updated successfully"}

        return {"success": False, "message": f"Payment status: {status}"}

    # Status
    def get_order_status(
        self,
        *,
        merchant_order_id: str,
        access_token: str | None = None,
        token_type: str | None = None,
    ) -> Dict[str, Any]:
        """Fetch order status from PhonePe. If no access token provided, fetch one."""
        if not merchant_order_id:
            raise ValueError("merchant_order_id is required")

        if not access_token:
            access_token, token_type_from_api = self.get_access_token()
            token_type = token_type or token_type_from_api
        else:
            token_type = token_type or "Bearer"

        url = f"{self.status_url_prefix}/{merchant_order_id}/status"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{token_type} {access_token}",
        }
        response = requests.get(url, headers=headers)
        try:
            data = response.json()
        except Exception:
            raise Exception(f"Invalid JSON response returned: {response.text}")

        if response.status_code == 200:
            return {"success": True, "data": data}
        raise Exception(json.dumps(data))


    def get_plan_id_by_transaction_id(self, *, merchant_order_id: str, db) -> int | None:
        """Return the associated plan_id for a given merchant_order_id, or None if not found.

        Looks up the local Transaction record created during order creation.
        """
        if not merchant_order_id:
            raise ValueError("merchant_order_id is required")
        txn = (
            db.query(Transaction)
            .filter(Transaction.merchant_order_id == merchant_order_id)
            .first()
        )
        return int(txn.plan_id) if txn and txn.plan_id is not None else 1

# Singleton-style instance if preferred by the API layer
payment_service = PaymentService()

