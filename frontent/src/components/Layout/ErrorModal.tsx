import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store';
import { clearGlobalError } from '../../store/slices/uiSlice';

const ErrorModal: React.FC = () => {
  const dispatch = useDispatch();
  const message = useSelector((state: RootState) => state.ui.globalError);

  if (!message) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm">
      <div className="bg-red-600 text-white rounded-lg shadow-lg p-4 flex items-start gap-3 animate-slide-in">
        <div className="flex-1 text-sm whitespace-pre-line">{message}</div>
        <button
          aria-label="Close error"
          className="ml-2 text-white/90 hover:text-white"
          onClick={() => dispatch(clearGlobalError())}
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default ErrorModal;


