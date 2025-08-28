import { useEffect } from "react";
import { initializePaddle } from '@paddle/paddle-js';

const PaddleCheckout = () => {
  useEffect(() => {
    initializePaddle({
      token: "test_1bfc72fb0d760e25abd16392579", // replace with your client token
      environment: "sandbox",
    });
  }, []);

  const itemsList = [
    {
      priceId: "pri_01k3n22vd29zpkj5k7b0hae0fc",
      quantity: 1,
    }
  ];

  const customerInfo = {
    email: "sam@example.com",
    
  };

  const openCheckout = () => {
    if (window.Paddle) {
      window.Paddle.Checkout.open({
        items: itemsList,
        customer: customerInfo,
      });
    } else {
      alert("Paddle SDK not loaded yet.");
    }
  };

  // Auto-open checkout on page load
  useEffect(() => {
    let opened = false;
    const tryOpen = () => {
      if (!opened && (window as any).Paddle) {
        opened = true;
        (window as any).Paddle.Checkout.open({
          items: itemsList,
          customer: customerInfo,
        });
      }
    };

    const id = setInterval(tryOpen, 100);
    // In case it's already available
    tryOpen();

    return () => clearInterval(id);
  }, []);

  return (
    <div>
      <button onClick={openCheckout}>
        Sign up now
      </button>
    </div>
  );
};

export default PaddleCheckout;

    