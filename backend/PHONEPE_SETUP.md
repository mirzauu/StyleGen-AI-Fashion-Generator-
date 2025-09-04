# PhonePe Payment Gateway Setup

This guide explains how to set up PhonePe payment gateway integration for the VestureAI application.

## Environment Variables

Add the following environment variables to your `.env` file:

```bash
# PhonePe Payment Gateway Configuration
PHONEPE_MERCHANT_ID=PGTESTPAYUAT
PHONEPE_SALT_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHBpcmVzT24iOjE3NTY2NTE3NjY5OTMsIm1lcmNoYW50SWQiOiJURVNULU0yMzdMN0xLWTZINTcifQ.9pobjBT-YPdKbqZbqeHerHb6u44GaoBz1HW3lsewEtU
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=UAT  # UAT or PROD

# Application URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## Configuration Details

### Test Environment (UAT)
- **Merchant ID**: `PGTESTPAYUAT`
- **Salt Key**: `099eb0cd-02cf-4e2a-8aca-3e6c6aff0399`
- **Salt Index**: `1`
- **Base URL**: `https://api-preprod.phonepe.com`

### Production Environment
- **Merchant ID**: Your production merchant ID from PhonePe
- **Salt Key**: Your production salt key from PhonePe
- **Salt Index**: Your production salt index
- **Base URL**: `https://api.phonepe.com`

## API Endpoints

### 1. Create Payment Order
- **Endpoint**: `POST /api/payments/create-phonepe-order`
- **Description**: Creates a new PhonePe payment order
- **Authentication**: Required (Bearer token)

### 2. Payment Webhook
- **Endpoint**: `POST /api/payments/phonepe-webhook`
- **Description**: Handles PhonePe payment notifications
- **Authentication**: Not required (PhonePe calls this endpoint)

### 3. Payment Status Check
- **Endpoint**: `GET /api/payments/payment-status/{transaction_id}`
- **Description**: Checks the status of a payment transaction
- **Authentication**: Required (Bearer token)

## Frontend Integration

The frontend uses PhonePe's iframe PayPage integration:

1. **Script Loading**: PhonePe checkout script is loaded dynamically
2. **Payment Flow**: 
   - User clicks "Get Pro" button
   - Frontend calls backend to create payment order
   - PhonePe PayPage opens in iframe
   - User completes payment
   - Callback handles success/failure

## Webhook Configuration

Configure your PhonePe webhook URL in the PhonePe merchant dashboard:
```
https://your-domain.com/api/payments/phonepe-webhook
```

## Testing

### Test Card Details
- **Card Number**: `4111 1111 1111 1111`
- **Expiry**: Any future date
- **CVV**: Any 3 digits
- **OTP**: `123456`

### Test UPI
- **UPI ID**: `success@upi`

## Security Considerations

1. **Webhook Verification**: Implement proper webhook signature verification
2. **Environment Variables**: Never commit sensitive keys to version control
3. **HTTPS**: Use HTTPS in production for all webhook endpoints
4. **Error Handling**: Implement proper error handling for failed payments

## Troubleshooting

### Common Issues

1. **Payment Creation Fails**
   - Check merchant ID and salt key configuration
   - Verify network connectivity to PhonePe APIs
   - Check request payload format

2. **Webhook Not Received**
   - Verify webhook URL configuration in PhonePe dashboard
   - Check server logs for webhook requests
   - Ensure webhook endpoint is publicly accessible

3. **Payment Status Mismatch**
   - Implement proper webhook signature verification
   - Check transaction ID format and uniqueness
   - Verify database connection and transaction handling

## Support

For PhonePe integration issues:
- Check PhonePe developer documentation
- Contact PhonePe merchant support
- Review server logs for detailed error messages
