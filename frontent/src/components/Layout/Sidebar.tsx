import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { setCurrentTask, fetchTasks } from '../../store/slices/appSlice';
import { Task } from '../../types';
import { Plus, Search, Image, ChevronRight } from 'lucide-react';
import { format } from 'date-fns';

interface SidebarProps {
  onNewTask: () => void;
}

const TaskSkeleton: React.FC = () => (
  <div className="p-2 rounded-md border border-transparent">
    <div className="flex items-start space-x-2">
      {/* Thumbnail Skeleton */}
      <div className="w-16 h-16 rounded-md bg-gray-200 animate-pulse"></div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          {/* Title Skeleton */}
          <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
        </div>
        {/* Date Skeleton */}
        <div className="h-3 bg-gray-200 rounded animate-pulse w-1/2 mt-2"></div>
      </div>
    </div>
  </div>
);

const Sidebar: React.FC<SidebarProps> = ({ onNewTask }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { tasks, currentTask, loading } = useSelector((state: RootState) => state.app);
  const [isInitialLoad, setIsInitialLoad] = React.useState(true);

  React.useEffect(() => {
    const fetchData = async () => {
      setIsInitialLoad(true);
      await dispatch(fetchTasks());
      setIsInitialLoad(false);
    };
    
    fetchData();
  }, [dispatch]);

  const handleTaskClick = (task: Task) => {
    dispatch(setCurrentTask(task));
  };

  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'in_progress':
        return 'text-amber-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusText = (status: Task['status']) => {
    switch (status) {
      case 'not_started':
        return 'Not Started';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      default:
        return status;
    }
  };

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 h-full flex flex-col">
      {/* AI Model Section */}
      <div className="p-4 sm:p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Model</h3>
        <p className="text-sm text-gray-600 mb-4">
          Showcase clothing with a variety of models that aligns with your brand's aesthetic.
        </p>

        <button
          onClick={onNewTask}
          className="w-full bg-amber-600 text-white py-2.5 px-4 rounded-lg font-medium hover:bg-amber-700 active:bg-amber-800 transition-colors flex items-center justify-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Create New Model</span>
        </button>
      </div>

      {/* Tasks List */}
      <div className="flex-1 overflow-auto">
        <div className="p-3 sm:p-4">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search task"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div className="space-y-1">
            {(loading || isInitialLoad) ? (
              // Loading skeleton animation
              <>
                {[...Array(6)].map((_, index) => (
                  <TaskSkeleton key={index} />
                ))}
              </>
            ) : tasks.length === 0 ? (
              // Empty state
              <div className="text-center py-8">
                <Image className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-sm text-gray-500">No tasks found</p>
                <p className="text-xs text-gray-400 mt-1">Create your first model to get started</p>
              </div>
            ) : (
              // Actual tasks
              tasks.map((task) => (
                <div
                  key={task.id}
                  onClick={() => handleTaskClick(task)}
                  className={`p-2 rounded-md cursor-pointer transition-all duration-200 group ${
                    currentTask?.id === task.id
                      ? 'bg-purple-100 border border-purple-200'
                      : 'hover:bg-gray-100 border border-transparent'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {/* Thumbnail Image */}
                    <div className="w-16 h-16 rounded-md overflow-hidden bg-gray-100 flex items-center justify-center">
                      {task.modelImages && task.modelImages.length > 0 ? (
                        <img
                          src={task.modelImages[0]}
                          alt={task.name}
                          style={{ width: '60px', height: '60px', border: '1px solid #d1d5db' }}
                        />
                      ) : (
                        <Image className="w-4 h-4 text-gray-400" />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-[13px] font-medium text-gray-900 truncate">{task.name}</h4>
                        <ChevronRight className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {task.createdAt
                          ? format(new Date(task.createdAt), 'MMM d, yyyy')
                          : 'No date'}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;