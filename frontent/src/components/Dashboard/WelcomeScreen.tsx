import React from 'react';
import MultiStepTaskCreation from '../Tasks/MultiStepTaskCreation';

interface WelcomeScreenProps {
  onTaskCreated: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onTaskCreated }) => {
  const handleTaskCreated = () => {
    onTaskCreated();
  };

  return (
    <div className="bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <MultiStepTaskCreation
          onTaskCreated={handleTaskCreated}
          onCancel={() => {}} // No cancel needed since this is the main interface
        />
      </div>
    </div>
  );
};

export default WelcomeScreen;