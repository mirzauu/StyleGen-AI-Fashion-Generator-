import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { logout } from '../../store/slices/authSlice';
import { User, LogOut, HelpCircle, CreditCard, Menu, Image as ImageIcon, BadgeCheck, Sparkles } from 'lucide-react';
import { appAPI, userAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import ProPlansPage from '../Plans/ProPlansPage';

interface HeaderProps {
  onUnlockPro?: () => void;
  onToggleSidebar?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onUnlockPro, onToggleSidebar }) => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [open, setOpen] = React.useState(false);
  const menuRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [open]);
  const { user } = useSelector((state: RootState) => state.auth);
  const [displayName, setDisplayName] = React.useState<string | undefined>(user?.name);
  const [isProUser, setIsProUser] = React.useState<boolean>(!!user?.isPro);

  const handleLogout = () => {
    dispatch(logout());
  };

  const [remainingImages, setRemainingImages] = React.useState<number | null>(null);
  const [showTokensTooltip, setShowTokensTooltip] = React.useState(false);

  React.useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const { remaining } = await appAPI.getRemainingImageTokens();
        if (isMounted) setRemainingImages(remaining);
      } catch {}
    })();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch user profile for name and pro status
  React.useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const profile = await userAPI.getProfile();
        if (!isMounted) return;
        setDisplayName(profile.name);
        setIsProUser(profile.isPro);
      } catch {}
    })();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <header className="bg-white border-b px-2 sm:px-6 py-2 flex items-center justify-between">
      {/* Logo and nav */}
      <div className="flex items-center space-x-2 sm:space-x-6">
        <button
          type="button"
          className="md:hidden p-2 rounded hover:bg-gray-100"
          aria-label="Open menu"
          onClick={onToggleSidebar}
        >
          <Menu className="w-5 h-5 text-gray-700" />
        </button>
        <img src="/ChatGPT Image Aug 26, 2025, 08_24_33 PM.png" alt="Trylo Logo" className="h-12 w-auto" />
        <h1 className="text-xl font-bold text-gray-900">
          <span className="text-black-600">Trylo</span>
        </h1>
      </div>
      {/* Actions: stack on mobile */}
      <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4">
        <div className="flex items-center space-x-4">
          {isProUser && (
            <div className="flex items-center space-x-2 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-2.5 py-1 rounded-full text-xs font-medium">
              <BadgeCheck className="w-4 h-4" />
              <span>Pro</span>
            </div>
          )}
          
          {!isProUser && (
            <button
              onClick={() => navigate('/plans')}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-violet-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:from-indigo-600 hover:to-violet-700 transition-colors"
            >
              <Sparkles className="w-4 h-4" />
              <span>Upgrade</span>
            </button>
          )}

          <div className="flex items-center space-x-3">
            {/* Remaining tokens */}
            <div
              className="relative inline-flex items-center cursor-pointer"
              onMouseEnter={() => setShowTokensTooltip(true)}
              onMouseLeave={() => setShowTokensTooltip(false)}
              onClick={() => navigate('/plans')}
            >
              <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 transition-colors">
                <ImageIcon className="w-5 h-5 text-emerald-500" />
                {typeof remainingImages === 'number' && (
                  <span className="absolute -top-1 -right-1 text-[10px] leading-none bg-emerald-500 text-white px-1.5 py-0.5 rounded-full">
                    {remainingImages}
                  </span>
                )}
              </div>
              {showTokensTooltip && (
                <div className="absolute left-1/2 -translate-x-1/2 top-full mt-3 w-64 bg-white text-gray-800 text-sm px-4 py-3 rounded-xl shadow-2xl border border-gray-200 z-50">
                  You can generate {typeof remainingImages === 'number' ? remainingImages : '0'} amount of image
                </div>
              )}
            </div>
            <div className="relative" ref={menuRef}>
              <button
                type="button"
                className="flex items-center space-x-2 cursor-pointer select-none"
                onClick={() => setOpen((v) => !v)}
              >
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-gray-600" />
                </div>
                <span className="text-sm font-medium text-gray-700">{displayName || 'User'}</span>
              </button>
              {open && (
                <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-50">
                  <button
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    onClick={() => navigate('/account/subscription')}
                  >
                    <CreditCard className="w-4 h-4 text-amber-600" /> My Subscription
                  </button>
                  <button
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    onClick={() => navigate('/help')}
                  >
                    <HelpCircle className="w-4 h-4 text-amber-600" /> Help Center
                  </button>
                </div>
              )}
            </div>
            
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;