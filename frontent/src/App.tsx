import React from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { store } from './store';
import { useAuth } from './hooks/useAuth';
import LoginForm from './components/Auth/LoginForm';
import RegisterForm from './components/Auth/RegisterForm';
import Dashboard from './components/Dashboard/Dashboard';
import ProPlansPage from './components/Plans/ProPlansPage';
import PaymentSuccessPage from './components/Payment/PaymentSuccessPage';
import SubscriptionPage from './components/Support/SubscriptionPage';
import HelpCenterPage from './components/Support/HelpCenterPage';
import { Toaster } from 'react-hot-toast';
import ErrorModal from './components/Layout/ErrorModal';

const AuthWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthFlow />;
  }

  return <>{children}</>;
};

const AuthFlow: React.FC = () => {
  const [isLogin, setIsLogin] = React.useState(true);

  return isLogin ? (
    <LoginForm onSwitchToRegister={() => setIsLogin(false)} />
  ) : (
    <RegisterForm onSwitchToLogin={() => setIsLogin(true)} />
  );
};

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <Router>
        <div className="App">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
          <ErrorModal />
          
          <Routes>
            <Route
              path="/*"
              element={
                <AuthWrapper>
                  <Dashboard />
                </AuthWrapper>
              }
            />
            <Route path="/plans" element={<ProPlansPage />} />
           
            <Route path="/payment/success" element={<PaymentSuccessPage />} />
            <Route path="/account/subscription" element={<SubscriptionPage />} />
            <Route path="/help" element={<HelpCenterPage />} />
          </Routes>
        </div>
      </Router>
    </Provider>
  );
};

export default App;