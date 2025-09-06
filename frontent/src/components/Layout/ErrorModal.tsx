import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store';
import { clearGlobalError } from '../../store/slices/uiSlice';

const ErrorModal: React.FC = () => {
  const dispatch = useDispatch();
  const message = useSelector((state: RootState) => state.ui.globalError);

  // Auto-close after 7 seconds
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        dispatch(clearGlobalError());
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [message, dispatch]);

  if (!message) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md">
      <div className="bg-red-600 text-white rounded-lg shadow-lg p-6 flex items-start gap-4 animate-slide-in">
        <div className="flex-1 text-base whitespace-pre-line">{message}</div>
        <button
          aria-label="Close error"
          className="ml-2 text-white/90 hover:text-white text-lg font-bold"
          onClick={() => dispatch(clearGlobalError())}
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default ErrorModal;


