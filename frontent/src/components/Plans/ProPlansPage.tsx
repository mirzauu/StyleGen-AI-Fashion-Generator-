import React, { useEffect, useState, useCallback, useRef } from 'react';
import { CheckCircle, Image as ImageIcon, ShieldCheck, BadgeCheck, Crown } from 'lucide-react';
import { paymentsAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';

// PhonePe callback moved inside component to access state and navigation

const ProPlansPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [transactionId, setTransactionId] = useState<string | undefined>(undefined);
  const transactionIdRef = useRef<string | undefined>(undefined);
  const navigate = useNavigate();

  const phonePeCallback = useCallback(async (response: string) => {
    console.log('PhonePe callback response:', response);
    if (response === 'USER_CANCEL') {
      console.log('Payment cancelled by user');
    } else if (response === 'CONCLUDED') {
      console.log('Payment completed successfully');
      try {
        const txId = transactionIdRef.current;
        console.log('Transaction ID in callback:', txId);
        if (txId) {
          const { status } = await paymentsAPI.getPaymentStatus(txId);
          console.log('Payment status:', status);
        }
        
      } catch (e) {
        console.error('Failed to verify payment status:', e);
      } finally {
        navigate('/');
      }
    }
  }, [navigate]);

  // Initialize PhonePe Checkout script
  useEffect(() => {
    // Add PhonePe Checkout script to the page
    const script = document.createElement('script');
    script.src = 'https://mercury.phonepe.com/web/bundle/checkout.js';
    script.async = true;
    script.onload = () => {
      console.log('PhonePe Checkout script loaded');
    };
    document.head.appendChild(script);

    return () => {
      // Cleanup script on component unmount
      const existingScript = document.querySelector('script[src*="checkout.js"]');
      if (existingScript) {
        existingScript.remove();
      }
    };
  }, []);

  const openPhonePeCheckout = async (plan: number, amountPaise: number) => {
    setIsLoading(true);
    try {
      // Call backend via services to create payment and get tokenUrl
      const { tokenUrl, transactionId } = await paymentsAPI.createPhonePeOrder(amountPaise, plan=plan, 'INR');
      console.log('Transaction ID from create order:', transactionId);
      setTransactionId(transactionId);
      transactionIdRef.current = transactionId;

      // Open PhonePe PayPage in iframe mode
      if ((window as any).PhonePeCheckout) {
        (window as any).PhonePeCheckout.transact({
          tokenUrl,
          callback: phonePeCallback,
          type: "IFRAME"
        });
      } else {
        // Fallback: try shortly after if SDK hasn't attached yet
        const id = setInterval(() => {
          if ((window as any).PhonePeCheckout) {
            clearInterval(id);
            (window as any).PhonePeCheckout.transact({
              tokenUrl,
              callback: phonePeCallback,
              type: "IFRAME"
            });
          }
        }, 100);
        setTimeout(() => {
          clearInterval(id);
          setIsLoading(false);
        }, 3000);
      }
    } catch (error) {
      console.error('Error opening PhonePe checkout:', error);
      alert('Failed to open payment gateway. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#FFFCEB]">
      <div className="max-w-6xl mx-auto px-4 py-12 sm:py-16">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-medium mb-3">
            <Crown className="w-4 h-4" />
            Premium Access
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight">Choose a plan</h2>
          <p className="mt-3 text-gray-600">Full access. Simple pricing. Cancel anytime.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Basic (Monthly) */}
          <div className="rounded-2xl overflow-hidden bg-white border border-gray-200 shadow-sm">
            <div className="bg-[#2F52FF] text-white p-6">
              <h3 className="text-xl font-bold">Basic</h3>
              <p className="text-xs opacity-90 mt-1">Full access monthly. No commitment.</p>
              <div className="flex items-end gap-1 mt-6">
                <span className="text-4xl font-extrabold">₹299</span>
                <span className="text-sm ml-1">/ month</span>
              </div>
            </div>
            <div className="p-6">
              <ul className="space-y-3 mb-6 text-gray-700">
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />Billed Monthly</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited recording time</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited recording length</li>
                <li className="flex items-start gap-3"><ImageIcon className="w-5 h-5 text-purple-600 mt-0.5" />Record audio or phone calls</li>
                <li className="flex items-start gap-3"><ShieldCheck className="w-5 h-5 text-emerald-600 mt-0.5" />Background recording in iOS</li>
                <li className="flex items-start gap-3"><BadgeCheck className="w-5 h-5 text-pink-600 mt-0.5" />Best-in-class transcription</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited summary customizations</li>
              </ul>
              <button
                className="w-full inline-flex justify-center items-center gap-2 bg-amber-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-amber-700 active:bg-amber-800 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={() => openPhonePeCheckout(1, 29900)}
                disabled={isLoading}
              >
                {isLoading ? 'Processing...' : 'Get Basic'}
              </button>
            </div>
          </div>

          {/* Pro (Monthly) */}
          <div className="rounded-2xl overflow-hidden bg-white border border-gray-200 shadow-sm">
            <div className="bg-[#D9ECF7] text-gray-900 p-6 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-black text-white text-xs px-3 py-1 rounded-full flex items-center gap-1 shadow">
                <span className="text-yellow-400">✦</span> Popular
              </div>
              <h3 className="text-xl font-bold">Pro</h3>
              <p className="text-xs opacity-80 mt-1">Unlimited access monthly. Simple and flexible.</p>
              <div className="flex items-end gap-1 mt-6">
                <span className="text-4xl font-extrabold">₹999</span>
                <span className="text-sm ml-1">/ month</span>
              </div>
            </div>
            <div className="p-6">
              <ul className="space-y-3 mb-6 text-gray-700">
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />Billed Monthly</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited recording time</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited recording length</li>
                <li className="flex items-start gap-3"><ImageIcon className="w-5 h-5 text-purple-600 mt-0.5" />Record audio or phone calls</li>
                <li className="flex items-start gap-3"><ShieldCheck className="w-5 h-5 text-emerald-600 mt-0.5" />Background recording in iOS</li>
                <li className="flex items-start gap-3"><BadgeCheck className="w-5 h-5 text-pink-600 mt-0.5" />Best-in-class transcription</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited summary customizations</li>
              </ul>
              <button
                className="w-full inline-flex justify-center items-center gap-2 bg-amber-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-amber-700 active:bg-amber-800 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={() => openPhonePeCheckout(2, 99900)}
                disabled={isLoading}
              >
                {isLoading ? 'Processing...' : 'Get Pro'}
              </button>
            </div>
          </div>

          {/* Elite (Monthly) */}
          <div className="rounded-2xl overflow-hidden bg-white border border-gray-200 shadow-sm relative">
            <div className="bg-gradient-to-br from-pink-500 to-fuchsia-600 text-white p-6">
              <h3 className="text-xl font-bold">Elite</h3>
              <p className="text-xs opacity-90 mt-1">Maximum access and priority everything.</p>
              <div className="flex items-end gap-1 mt-6">
                <span className="text-4xl font-extrabold">₹1,999</span>
                <span className="text-sm ml-1">/ month</span>
              </div>
            </div>
            <div className="p-6">
              <ul className="space-y-3 mb-6 text-gray-700">
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />Billed Monthly</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited recording time</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited recording length</li>
                <li className="flex items-start gap-3"><ImageIcon className="w-5 h-5 text-purple-200 mt-0.5" />Record audio or phone calls</li>
                <li className="flex items-start gap-3"><ShieldCheck className="w-5 h-5 text-emerald-200 mt-0.5" />Background recording in iOS</li>
                <li className="flex items-start gap-3"><BadgeCheck className="w-5 h-5 text-white mt-0.5" />Best-in-class transcription</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Unlimited summary customizations</li>
              </ul>
              <button
                className="w-full inline-flex justify-center items-center gap-2 bg-amber-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-amber-700 active:bg-amber-800 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={() => openPhonePeCheckout(3, 199900)}
                disabled={isLoading}
              >
                {isLoading ? 'Processing...' : 'Get Elite'}
              </button>
            </div>
          </div>

          {/* Customization */}
          <div className="rounded-2xl overflow-hidden bg-white border border-gray-200 shadow-sm">
            <div className="bg-gray-50 text-gray-900 p-6">
              <h3 className="text-xl font-bold">Customization</h3>
              <p className="text-xs opacity-80 mt-1">Need higher limits or team seats? We can help.</p>
            </div>
            <div className="p-6">
              <ul className="space-y-3 mb-6 text-gray-700">
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Custom image quotas</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Dedicated support & SLAs</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Onboarding & training</li>
                <li className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />Web based dashboard</li>
              </ul>
              <button
                className="w-full inline-flex justify-center items-center gap-2 bg-gray-900 text-white px-6 py-3 rounded-xl font-medium hover:bg-black transition-colors shadow-sm"
                onClick={() => window.open('mailto:sales@example.com', '_blank')}
              >
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProPlansPage;