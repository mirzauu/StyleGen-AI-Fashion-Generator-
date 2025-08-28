import React, { useEffect } from 'react';
import { initializePaddle } from '@paddle/paddle-js';
import { CheckCircle, Image as ImageIcon, ShieldCheck, BadgeCheck } from 'lucide-react';

const ProPlansPage: React.FC = () => {
  // Initialize Paddle on mount
  useEffect(() => {
    initializePaddle({
      token: "test_1bfc72fb0d760e25abd16392579",
      environment: "sandbox",
    });
  }, []);

  const itemsList = [
    {
      priceId: "pri_01k3n22vd29zpkj5k7b0hae0fc",
      quantity: 1,
    },
  ];

  const customerInfo = {
    email: "sam@example.com",
  } as any;

  const openCheckout = () => {
    if ((window as any).Paddle) {
      (window as any).Paddle.Checkout.open({
        items: itemsList,
        customer: customerInfo,
      });
    } else {
      // Fallback: try shortly after if SDK hasn't attached yet
      const id = setInterval(() => {
        if ((window as any).Paddle) {
          clearInterval(id);
          (window as any).Paddle.Checkout.open({
            items: itemsList,
            customer: customerInfo,
          });
        }
      }, 100);
      setTimeout(() => clearInterval(id), 3000);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-white to-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-12 sm:py-16">
        <div className="text-center mb-10">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight">Choose Your Pro Plan</h2>
          <p className="mt-3 text-gray-600">Simple pricing. Powerful features to scale your image generation.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 md:gap-8">
          {/* Pro Plan */}
          <div className="relative bg-white border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
            <div className="p-6 sm:p-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-gray-900">Pro Plan</h3>
                <span className="inline-flex items-center gap-1 text-xs font-medium text-purple-700 bg-purple-50 px-2.5 py-1 rounded-full">
                  <BadgeCheck className="w-4 h-4" /> Best value
                </span>
              </div>
              <div className="flex items-end gap-2 mb-6">
                <span className="text-4xl font-extrabold text-gray-900">999</span>
                <span className="text-sm text-gray-500">INR (Monthly)</span>
              </div>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3 text-gray-700">
                  <ImageIcon className="w-5 h-5 text-purple-600 mt-0.5" />
                  <span><span className="font-medium">200 images</span> included</span>
                </li>
                <li className="flex items-start gap-3 text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <span><span className="font-medium">Free cancellation</span> anytime</span>
                </li>
                <li className="flex items-start gap-3 text-gray-700">
                  <ShieldCheck className="w-5 h-5 text-emerald-600 mt-0.5" />
                  <span><span className="font-medium">No watermark</span> on outputs</span>
                </li>
                <li className="flex items-start gap-3 text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <span>Priority support</span>
                </li>
              </ul>

              <button
                className="w-full inline-flex justify-center items-center gap-2 bg-amber-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-amber-700 active:bg-amber-800 transition-colors shadow-sm"
                onClick={openCheckout}
              >
                Get Pro
              </button>
            </div>
          </div>

          {/* Customisation Plan */}
          <div className="relative bg-white border border-gray-200 rounded-2xl shadow-sm">
            <div className="p-6 sm:p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Customisation</h3>
              <p className="text-gray-600 mb-6">Need higher limits, team seats, or custom features? We can help.</p>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3 text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <span>Custom image quotas</span>
                </li>
                <li className="flex items-start gap-3 text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <span>Dedicated support & SLAs</span>
                </li>
                <li className="flex items-start gap-3 text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <span>Onboarding & training</span>
                </li>
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