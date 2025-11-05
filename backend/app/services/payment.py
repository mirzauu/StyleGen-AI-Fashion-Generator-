import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

import requests
from app.models.transaction import Transaction


class PaymentService:
    """Encapsulates PayPal Orders v2 operations: create, capture/webhook, status."""

    def __init__(self) -> None:
        # Configuration
        self.client_id: str = os.getenv("PAYPAL_CLIENT_ID", "TEST_CLIENT_ID")
        self.client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "TEST_CLIENT_SECRET")
        self.environment: str = os.getenv("PAYPAL_ENVIRONMENT", "SANDBOX")

        # Endpoints (PayPal)
        if self.environment.upper() == "PROD":
            self.base_url: str = "https://api-m.paypal.com"
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"

        # OAuth token cache
        self._access_token = None
        self._token_expiry_utc = None

        # Common endpoints
        self.orders_url: str = f"{self.base_url}/v2/checkout/orders"
        self.oauth_token_url: str = f"{self.base_url}/v1/oauth2/token"

    def _get_access_token(self) -> str:
        """Fetch and cache PayPal OAuth access token using client credentials."""
        if self._access_token and self._token_expiry_utc and datetime.utcnow() < self._token_expiry_utc:
            return self._access_token

        auth = (self.client_id, self.client_secret)
        data = {"grant_type": "client_credentials"}
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        response = requests.post(self.oauth_token_url, data=data, headers=headers, auth=auth)

        try:
            token_data = response.json()
        except Exception:
            raise Exception(f"Invalid token response: {response.text}")

        if response.status_code not in (200, 201) or "access_token" not in token_data:
            raise Exception(json.dumps(token_data))

        self._access_token = token_data["access_token"]
        expires_in = int(token_data.get("expires_in", 300))
        self._token_expiry_utc = datetime.utcnow() + timedelta(seconds=max(60, expires_in - 30))
        return self._access_token

    def _paypal_headers(self) -> Dict[str, str]:
        access_token = self._get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    # Create PayPal order (Orders v2)
    def create_paypal_order(
        self,
        *,
        amount_paise: int,
        user_id: int,
        plan_id: int | None,
        db=None,
        return_url: str = "https://app.trylo.space/paypal/return",
        cancel_url: str = "https://app.trylo.space/paypal/cancel",
    ) -> Dict[str, Any]:
        """Create a PayPal order and return approval link."""
        amount_value = f"{amount_paise / 100:.2f}"

        payload = {
            "intent": "CAPTURE",
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "return_url": return_url,
                        "cancel_url": cancel_url,
                        "user_action": "PAY_NOW",
                    }
                }
            },
            "purchase_units": [
                {
                    "reference_id": f"plan_{plan_id}" if plan_id is not None else "plan_0",
                    "custom_id": f"user:{user_id}|plan:{plan_id if plan_id is not None else ''}",
                    "amount": {
                        "currency_code": "USD",
                        "value": amount_value,
                    },
                }
            ],
        }

        headers = self._paypal_headers()
        response = requests.post(self.orders_url, json=payload, headers=headers)

        try:
            response_data = response.json()
        except Exception:
            raise Exception(f"Invalid JSON response returned: {response.text}")

        if response.status_code in (200, 201) and response_data.get("id"):
            order_id = response_data["id"]

            # Persist pending transaction if db provided
            try:
                if db is not None:
                    txn = Transaction(
                        user_id=user_id,
                        plan_id=plan_id,
                        subscription_id=None,
                        merchant_order_id=order_id,
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
                pass

            approval_url = None
            for link in response_data.get("links", []):
                if link.get("rel") == "approve":
                    approval_url = link.get("href")
                    break

            return {
                "success": True,
                "approvalUrl": approval_url,
                "orderId": order_id,
                "raw": response_data,
            }

        raise Exception(json.dumps(response_data))

    # Webhook handler for Cashfree
    def handle_cashfree_webhook(self, *, body: bytes, db, SubscriptionModel) -> Dict[str, Any]:
        """
        Handle Cashfree webhook payload. Typical keys: orderId, referenceId, txStatus (SUCCESS/FAILED), orderAmount, etc.
        Maps successful payments to activate/update subscription.
        """
        body_str = body.decode("utf-8")
        try:
            webhook_data = json.loads(body_str)
        except Exception:
            # Some setups send form-encoded payloads; try to parse if needed
            raise Exception("Invalid webhook payload")

        merchant_order_id = webhook_data.get("orderId") or webhook_data.get("order_id") or webhook_data.get("orderid")
        tx_status = webhook_data.get("txStatus") or webhook_data.get("status") or webhook_data.get("txstatus")  # e.g., SUCCESS

        if tx_status and tx_status.upper() in ("SUCCESS", "PAID"):
            # Try derive user_id from merchant_order_id if embedded, else lookup Transaction record
            user_id = None
            if isinstance(merchant_order_id, str) and "_" in merchant_order_id:
                try:
                    user_id = int(merchant_order_id.split("_")[1])
                except Exception:
                    user_id = None

            if user_id is None and merchant_order_id:
                # fall back to transaction lookup
                try:
                    txn = db.query(Transaction).filter(Transaction.merchant_order_id == merchant_order_id).first()
                    if txn:
                        user_id = txn.user_id
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
                        current_period_end = datetime.utcnow() + timedelta(days=30),
                    )
                    db.add(subscription)

                db.commit()

            return {"success": True, "message": "Subscription updated successfully"}

        return {"success": False, "message": f"Payment status: {tx_status}"}

    # Webhook handler for PayPal
    def handle_paypal_webhook(self, *, body: bytes, db, SubscriptionModel) -> Dict[str, Any]:
        """Handle PayPal webhook events and activate subscription on successful capture."""
        body_str = body.decode("utf-8")
        try:
            webhook_data = json.loads(body_str)
        except Exception:
            raise Exception("Invalid webhook payload")

        event_type = webhook_data.get("event_type")
        resource = webhook_data.get("resource", {})

        # Attempt to extract order id and user/plan context
        order_id = resource.get("id") or resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")
        custom_id = None
        try:
            units = resource.get("purchase_units") or []
            if isinstance(units, list) and units:
                custom_id = units[0].get("custom_id")
        except Exception:
            custom_id = None

        user_id: int | None = None
        plan_id: int | None = None
        if custom_id and "user:" in custom_id:
            try:
                parts = dict(item.split(":", 1) for item in custom_id.split("|") if ":" in item)
                user_id = int(parts.get("user")) if parts.get("user") else None
                plan_id = int(parts.get("plan")) if parts.get("plan") else None
            except Exception:
                user_id = None

        if user_id is None and order_id:
            try:
                txn = db.query(Transaction).filter(Transaction.merchant_order_id == order_id).first()
                if txn:
                    user_id = txn.user_id
                    if plan_id is None:
                        plan_id = txn.plan_id
            except Exception:
                user_id = None

        successful = False
        if event_type in ("PAYMENTS.CAPTURE.COMPLETED", "CHECKOUT.ORDER.COMPLETED"):
            successful = True

        if successful and user_id is not None:
            # Mark transaction as completed if present
            try:
                if order_id:
                    txn = db.query(Transaction).filter(Transaction.merchant_order_id == order_id).first()
                    if txn:
                        txn.status = "COMPLETED"
                        txn.response_payload = webhook_data
                        db.commit()
            except Exception:
                pass

            # Create/Update subscription
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
                    plan_id=plan_id or None,
                    current_period_start=datetime.utcnow(),
                    current_period_end = datetime.utcnow() + timedelta(days=30),
                )
                db.add(subscription)

            db.commit()
            return {"success": True, "message": "Subscription updated successfully"}

        return {"success": False, "message": f"Unhandled event or incomplete payment: {event_type}"}

    # Status
    def get_order_status(
        self,
        *,
        merchant_order_id: str,
    ) -> Dict[str, Any]:
        """Fetch order status from PayPal."""
        if not merchant_order_id:
            raise ValueError("merchant_order_id is required")

        url = f"{self.orders_url}/{merchant_order_id}"
        headers = self._paypal_headers()
        response = requests.get(url, headers=headers)

        try:
            data = response.json()
        except Exception:
            raise Exception(f"Invalid JSON response returned: {response.text}")

        if response.status_code in (200, 201):
            return {"success": True, "data": data}
        raise Exception(json.dumps(data))

    def capture_order(self, *, merchant_order_id: str, db=None) -> Dict[str, Any]:
        """Capture an approved PayPal order."""
        if not merchant_order_id:
            raise ValueError("merchant_order_id is required")

        url = f"{self.orders_url}/{merchant_order_id}/capture"
        headers = self._paypal_headers()
        response = requests.post(url, headers=headers)

        try:
            data = response.json()
        except Exception:
            raise Exception(f"Invalid JSON response returned: {response.text}")

        if response.status_code in (200, 201):
            # Update transaction record
            try:
                if db is not None:
                    txn = db.query(Transaction).filter(Transaction.merchant_order_id == merchant_order_id).first()
                    if txn:
                        txn.status = "COMPLETED"
                        # capture id if present
                        capture_id = None
                        try:
                            captures = data.get("purchase_units", [])[0].get("payments", {}).get("captures", [])
                            if captures:
                                capture_id = captures[0].get("id")
                        except Exception:
                            capture_id = None
                        txn.gateway_transaction_id = capture_id
                        txn.response_payload = data
                        db.commit()
            except Exception:
                pass
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