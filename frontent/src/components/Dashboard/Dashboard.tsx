import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store';
import Header from '../Layout/Header';
import Sidebar from '../Layout/Sidebar';
import TaskCreationModal from '../Tasks/TaskCreationModal';
import GenerationInterface from '../Generation/GenerationInterface';
import WelcomeScreen from './WelcomeScreen';
import { setCurrentTask } from '../../store/slices/appSlice';

const Dashboard: React.FC = () => {
  const { currentTask } = useSelector((state: RootState) => state.app);
  const [showGenerationInterface, setShowGenerationInterface] = React.useState(false);
  const [showWelcomeScreen, setShowWelcomeScreen] = React.useState(true);
  const dispatch = useDispatch();

  const handleNewTask = () => {
    dispatch(setCurrentTask(null)); // CLEAR THE TASK
    setShowWelcomeScreen(true);
    setShowGenerationInterface(false);
  };

  const handleTaskCreated = () => {
    setShowWelcomeScreen(false);
    setShowGenerationInterface(true);
  };

  const handleBackToDashboard = () => {
    setShowWelcomeScreen(true);
    setShowGenerationInterface(false);
  };

  React.useEffect(() => {
    if (currentTask && !showGenerationInterface) {
      setShowWelcomeScreen(false);
      setShowGenerationInterface(true);
    }
  }, [currentTask, showGenerationInterface]);

  const [mobileSidebarOpen, setMobileSidebarOpen] = React.useState(false);

  if (showGenerationInterface && currentTask) {
    return (
      <div className="h-screen bg-gray-50 flex flex-col">
        <div className="fixed top-0 left-0 right-0 z-30">
          <Header onToggleSidebar={() => setMobileSidebarOpen(true)} />
        </div>
        <div className="flex flex-1 pt-20 overflow-hidden">
          <div className="hidden md:block fixed left-0 top-20 bottom-0 z-20 w-64">
            <Sidebar onNewTask={handleNewTask} />
          </div>
          {mobileSidebarOpen && (
            <div className="fixed inset-0 z-40 md:hidden flex">
              <div className="w-64 bg-white border-r border-gray-200 h-full">
                <Sidebar onNewTask={() => { setMobileSidebarOpen(false); handleNewTask(); }} />
              </div>
              <div className="flex-1 bg-black/40" onClick={() => setMobileSidebarOpen(false)} />
            </div>
          )}
          <div
            className="flex-1 md:ml-64 overflow-y-auto px-2 sm:px-4"
            style={{ height: 'calc(100vh - 5rem)' }}
          >
            <GenerationInterface onBack={handleBackToDashboard} />
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="fixed top-0 left-0 right-0 z-30">
        <Header onToggleSidebar={() => setMobileSidebarOpen(true)} />
      </div>
      <div className="flex flex-1 pt-20 overflow-hidden">
        {/* Sidebar: hide on mobile, show on md+ */}
        <div className="hidden md:block fixed left-0 top-20 bottom-0 z-20 w-64">
          <Sidebar onNewTask={handleNewTask} />
        </div>
        {mobileSidebarOpen && (
          <div className="fixed inset-0 z-40 md:hidden flex">
            <div className="w-64 bg-white border-r border-gray-200 h-full">
              <Sidebar onNewTask={() => { setMobileSidebarOpen(false); handleNewTask(); }} />
            </div>
            <div className="flex-1 bg-black/40" onClick={() => setMobileSidebarOpen(false)} />
          </div>
        )}
        <div className="flex-1 md:ml-64 px-2 sm:px-4">
          {/* Content stacks and has padding on mobile */}
          {showGenerationInterface && currentTask ? (
            <GenerationInterface onBack={handleBackToDashboard} />
          ) : (
            showWelcomeScreen && <WelcomeScreen onTaskCreated={handleTaskCreated} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
