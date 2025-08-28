import { configureStore, Middleware } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import appReducer from './slices/appSlice';
import uiReducer from './slices/uiSlice';
import { setGlobalError } from './slices/uiSlice';

const errorMiddleware: Middleware = (storeApi) => (next) => (action) => {
  if (typeof action?.type === 'string' && action.type.endsWith('/rejected')) {
    const payloadDetail = action?.payload?.detail || action?.payload?.message;
    const errorMessage = payloadDetail || action?.error?.message;
    const isGenericAxiosMessage =
      typeof errorMessage === 'string' && /Request failed with status code \d+/.test(errorMessage);
    if (errorMessage && !isGenericAxiosMessage) {
      storeApi.dispatch(setGlobalError(errorMessage));
    }
  }
  return next(action);
};

export const store = configureStore({
  reducer: {
    auth: authReducer,
    app: appReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(errorMiddleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;