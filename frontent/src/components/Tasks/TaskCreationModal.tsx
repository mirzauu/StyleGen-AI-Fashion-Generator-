import React, { useState } from 'react';
import { X } from 'lucide-react';

const ModernTaskModal = ({ onClose, onSubmit, models = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedModelId, setSelectedModelId] = useState(null);
  const [errors, setErrors] = useState({});
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });

  // Mock models data for demonstration
  const mockModels = models.length ? models : [
    { id: '1', name: 'GPT-4', thumbnail: null },
    { id: '2', name: 'Claude', thumbnail: null },
    { id: '3', name: 'Llama 2', thumbnail: null },
    { id: '4', name: 'Gemini', thumbnail: null },
    { id: '5', name: 'PaLM', thumbnail: null },
    { id: '6', name: 'Mistral', thumbnail: null },
  ];

  const filteredModels = mockModels.filter(model =>
    model.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Task name is required';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    onSubmit({
      ...formData,
      modelId: selectedModelId
    });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 className="text-lg font-medium text-gray-900">Create Task</h2>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {/* Task Details */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Model Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                placeholder="Enter task name"
              />
              {errors.name && (
                <p className="mt-1 text-xs text-red-500">{errors.name}</p>
              )}
            </div>

          
          </div>

          {/* Model Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Model
            </label>
            
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 mb-3"
              placeholder="Search models..."
            />

            {/* Model List */}
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {filteredModels.map((model) => (
                <div
                  key={model.id}
                  onClick={() => setSelectedModelId(model.id)}
                  className={`flex items-center px-3 py-2 rounded cursor-pointer transition-colors ${
                    selectedModelId === model.id
                      ? 'bg-amber-50 border border-amber-200'
                      : 'hover:bg-gray-50 border border-transparent'
                  }`}
                >
                  <div className={`w-3 h-3 rounded-full border-2 mr-3 ${
                    selectedModelId === model.id
                      ? 'border-amber-500 bg-amber-500'
                      : 'border-gray-300'
                  }`}>
                    {selectedModelId === model.id && (
                      <div className="w-full h-full rounded-full bg-white scale-50" />
                    )}
                  </div>
                  <span className="text-sm text-gray-700 font-medium">
                    {model.name}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-4 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedModelId}
              className="px-4 py-2 text-sm bg-amber-600 text-white rounded hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Create Task
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ModernTaskModal;