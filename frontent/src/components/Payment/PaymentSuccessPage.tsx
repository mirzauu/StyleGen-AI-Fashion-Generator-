import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, ArrowRight } from 'lucide-react';
import { paymentsAPI } from '../../services/api';

const PaymentSuccessPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [paymentStatus, setPaymentStatus] = useState<'success' | 'pending' | 'failed'>('pending');

  useEffect(() => {
    // Get transaction details from URL params
    const transactionId = searchParams.get('transactionId');
    const code = searchParams.get('code');
    
    if (code === 'PAYMENT_SUCCESS') {
      setPaymentStatus('success');
      // You can verify the payment status with your backend here
      verifyPaymentStatus(transactionId);
    } else if (code === 'PAYMENT_ERROR') {
      setPaymentStatus('failed');
    }
    
    setIsLoading(false);
  }, [searchParams]);

  const verifyPaymentStatus = async (transactionId: string | null) => {
    if (!transactionId) return;
    
    try {
      const { status } = await paymentsAPI.getPaymentStatus(transactionId);
      if (status === 'PAYMENT_SUCCESS') {
        setPaymentStatus('success');
      } else {
        setPaymentStatus('failed');
      }
    } catch (error) {
      console.error('Error verifying payment status:', error);
    }
  };

  const handleContinue = () => {
    navigate('/dashboard');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verifying payment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full mx-auto px-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          {paymentStatus === 'success' ? (
            <>
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
              <p className="text-gray-600 mb-8">
                Your Pro subscription has been activated. You now have access to all premium features.
              </p>
              
              <div className="bg-green-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-green-800 mb-2">What's included:</h3>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• 200 images per month</li>
                  <li>• No watermarks</li>
                  <li>• Priority support</li>
                  <li>• Advanced features</li>
                </ul>
              </div>
            </>
          ) : paymentStatus === 'failed' ? (
            <>
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
                <div className="h-8 w-8 text-red-600 text-2xl">✕</div>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Failed</h1>
              <p className="text-gray-600 mb-8">
                We couldn't process your payment. Please try again or contact support if the issue persists.
              </p>
            </>
          ) : (
            <>
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100 mb-6">
                <div className="h-8 w-8 text-yellow-600 text-2xl">⏳</div>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Processing</h1>
              <p className="text-gray-600 mb-8">
                Your payment is being processed. You'll receive a confirmation shortly.
              </p>
            </>
          )}

          <button
            onClick={handleContinue}
            className="w-full inline-flex justify-center items-center gap-2 bg-amber-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-amber-700 active:bg-amber-800 transition-colors shadow-sm"
          >
            {paymentStatus === 'success' ? 'Continue to Dashboard' : 'Back to Plans'}
            <ArrowRight className="w-4 h-4" />
          </button>

          {paymentStatus === 'failed' && (
            <button
              onClick={() => navigate('/plans')}
              className="w-full mt-3 inline-flex justify-center items-center gap-2 bg-gray-100 text-gray-700 px-6 py-3 rounded-xl font-medium hover:bg-gray-200 transition-colors"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccessPage;
