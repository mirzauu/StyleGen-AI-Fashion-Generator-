import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { setUser } from '../store/slices/authSlice';

export const useAuth = () => {
  const dispatch = useDispatch();
  const { user, token, isLoading } = useSelector((state: RootState) => state.auth);
  const [isInitialized, setIsInitialized] = React.useState(false);
  
  // Restore user session from localStorage on app start
  React.useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('access_token');
    
    if (storedUser && storedToken && !user) {
      try {
        const userData = JSON.parse(storedUser);
        dispatch(setUser(userData));
      } catch (error) {
        console.error('Failed to parse stored user data:', error);
        // Clear invalid data
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
      }
    }
    
    setIsInitialized(true);
  }, [user, dispatch]);
  
  return {
    user,
    token: token || localStorage.getItem('access_token'),
    isLoading: isLoading || !isInitialized,
    isAuthenticated: !!(user || localStorage.getItem('user')) && !!(token || localStorage.getItem('access_token')),
  };
}