import React from 'react';
import { useForm } from 'react-hook-form';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { createTask, fetchModels, uploadModel } from '../../store/slices/appSlice';
import { Upload, X, Check, Search, FileText, Image as ImageIcon, Settings, Wand2 } from 'lucide-react';

interface TaskFormData {
  name: string;
  description: string;
  modelId: string;
  modelType: 'upload' | 'existing' | 'template';
  garmentType: 'top' | 'bottom' | 'onepiece';
  uploadedImages: File[];
  pose?: string;
}

interface MultiStepTaskCreationProps {
  onTaskCreated: () => void;
  onCancel: () => void;
}

const MultiStepTaskCreation: React.FC<MultiStepTaskCreationProps> = ({ onTaskCreated, onCancel }) => {
  const dispatch: AppDispatch = useDispatch();
  const { models } = useSelector((state: RootState) => state.app);
  const [selectedModelType, setSelectedModelType] = React.useState<'upload' | 'existing' | 'template' | ''>('');
  const [selectedGarmentType, setSelectedGarmentType] = React.useState<'top' | 'bottom' | 'onepiece' | null>(null);
  const [uploadedFiles, setUploadedFiles] = React.useState<File[]>([]);
  const [dragActive, setDragActive] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [isUploadingModel, setIsUploadingModel] = React.useState(false);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<TaskFormData>();

  const watchedName = watch('name');

  React.useEffect(() => {
    if (models.length === 0) {
      dispatch(fetchModels());
    }
  }, [models.length, dispatch]);

  const filteredModels = models.filter(model =>
    model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    model.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const onSubmit = async (data: TaskFormData) => {
    try {
      let modelId = data.modelId;

      if (selectedModelType === 'upload') {
        if (!data.name || uploadedFiles.length === 0) {
          throw new Error('Model name and at least one image are required for upload.');
        }
        for (const f of uploadedFiles) {
          if (!f) throw new Error('Each uploaded image must be a valid file.');
        }

        setIsUploadingModel(true);
        const modelRes = await dispatch(
          uploadModel({ name: data.name, images: uploadedFiles })
        ).unwrap();
        modelId = modelRes.id;
        setValue('modelId', modelId);
        setValue('modelType', 'upload');
        setValue('garmentType', selectedGarmentType as 'top' | 'bottom' | 'onepiece');
        setIsUploadingModel(false);
      } else {
        setValue('modelType', selectedModelType as 'upload' | 'existing' | 'template');
        setValue('garmentType', selectedGarmentType as 'top' | 'bottom' | 'onepiece');
      }

      await new Promise(r => setTimeout(r, 0));
      await dispatch(createTask({
        name: data.name,
        description: data.description,
        modelId: modelId,
        garmentType: selectedGarmentType as 'top' | 'bottom' | 'onepiece',
        pose: data.pose,
      }));

      onTaskCreated();
    } catch (error) {
      setIsUploadingModel(false);
      console.error('Failed to create task:', error);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files).slice(0, 5);
      setUploadedFiles(files);
      setValue('uploadedImages', files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).slice(0, 5);
      setUploadedFiles(files);
      setValue('uploadedImages', files);
    }
  };

  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(newFiles);
    setValue('uploadedImages', newFiles);
  };

  const canSubmit = () => {
    const hasValidModel = selectedModelType === 'upload'
      ? uploadedFiles.length > 0
      : selectedModelType === 'existing'
        ? Boolean(watch('modelId'))
        : selectedModelType === 'template';

    return watchedName && selectedModelType && selectedGarmentType && hasValidModel;
  };

  const steps = [
    { number: 1, title: 'Details', completed: !!watchedName },
    { number: 2, title: 'Model', completed: !!selectedModelType },
    { number: 3, title: 'Configure', completed: !!selectedGarmentType },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col py-6 px-4">
      <div className="max-w-6xl w-full mx-auto flex flex-col lg:flex-row gap-6 flex-1">
        {/* Left Sidebar - Progress */}
        <div className="w-full lg:w-56 flex-shrink-0">
          <div className="bg-white rounded-lg border border-gray-200 p-4 sticky top-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Wand2 className="w-4 h-4 text-amber-600" /> Progress
            </h3>
            <div className="space-y-3">
              {steps.map((step) => (
                <div key={step.number} className="flex items-center space-x-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                    step.completed ? 'bg-amber-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}>
                    {step.completed ? <Check className="w-3 h-3" /> : step.number}
                  </div>
                  <span className={`text-sm font-medium ${
                    step.completed ? 'text-amber-600' : 'text-gray-600'
                  }`}>
                    {step.title}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-5 pt-4 border-t border-gray-200">
              <div className="w-full bg-gray-200 rounded-full h-1">
                <div
                  className="bg-amber-600 h-1 rounded-full transition-all duration-300"
                  style={{ width: `${(steps.filter(s => s.completed).length / steps.length) * 100}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {steps.filter(s => s.completed).length} of {steps.length} completed
              </p>
            </div>
          </div>
        </div>

        {/* Form Area */}
        <div className="flex-1 bg-white rounded-lg border border-gray-200 p-6 overflow-visible">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Step 1: Model Details */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-amber-600" /> Model Details
              </h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model Name *
                  </label>
                  <input
                    type="text"
                    {...register('name', { required: 'Model name is required' })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-sm transition"
                    placeholder="e.g., Summer Collection Try-On"
                  />
                  {errors.name && (
                    <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Step 2: AI Model Selection */}
            <div className="pt-6 border-t border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-amber-600" /> Choose AI Model
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  type="button"
                  className={`p-3 rounded-lg border-2 text-left transition-all ${
                    selectedModelType === 'upload'
                      ? 'border-amber-600 bg-amber-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onClick={() => {
                    setSelectedModelType('upload');
                    setValue('modelType', 'upload');
                  }}
                >
                  <h4 className="font-medium text-gray-900 text-sm flex items-center gap-2">
                    <Upload className="w-4 h-4 text-amber-600" /> Upload Model
                  </h4>
                  <p className="text-xs text-gray-600 mt-1">Upload your own images</p>
                </button>

                <button
                  type="button"
                  className={`p-3 rounded-lg border-2 text-left transition-all ${
                    selectedModelType === 'existing'
                      ? 'border-amber-600 bg-amber-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onClick={() => {
                    setSelectedModelType('existing');
                    setValue('modelType', 'existing');
                    setValue('modelId', '');
                  }}
                >
                  <h4 className="font-medium text-gray-900 text-sm flex items-center gap-2">
                    <ImageIcon className="w-4 h-4 text-amber-600" /> Existing Model
                  </h4>
                  <p className="text-xs text-gray-600 mt-1">Choose from library</p>
                </button>

                {/* Placeholder for future template option */}
              </div>

              {/* Upload Area */}
              {selectedModelType === 'upload' && (
                <div className="mt-4">
                  <div
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-md p-6 text-center bg-gray-50 cursor-pointer transition-colors ${
                      dragActive ? 'bg-amber-50 border-amber-400' : 'border-gray-300'
                    }`}
                  >
                    <p className="text-sm text-gray-600 mb-2">
                      Drag and drop up to 5 images, or click to browse
                    </p>
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleFileInput}
                      className="hidden"
                      id="model-upload"
                    />
                    <label
                      htmlFor="model-upload"
                      className="inline-flex items-center px-4 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 cursor-pointer text-sm font-semibold select-none"
                    >
                      <Upload className="w-5 h-5 mr-2" />
                      Choose Files
                    </label>
                    {uploadedFiles.length > 0 && (
                      <div className="mt-4 grid grid-cols-5 gap-3">
                        {uploadedFiles.map((file, index) => (
                          <div key={index} className="relative group rounded-md overflow-hidden shadow-sm">
                            <img
                              src={URL.createObjectURL(file)}
                              alt={`Upload ${index + 1}`}
                              className="w-full h-24 object-cover"
                            />
                            <button
                              type="button"
                              onClick={() => removeFile(index)}
                              className="absolute top-1 right-1 w-6 h-6 bg-red-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity focus:outline-none"
                              aria-label="Remove file"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Existing Models Grid */}
              {selectedModelType === 'existing' && (
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-base font-medium text-gray-900">Available Models</h4>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-amber-500"
                        placeholder="Search..."
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-3 max-h-96 overflow-y-auto rounded-md border border-gray-200 p-2">
                    {filteredModels.map((model) => (
                      <div
                        key={model.id}
                        onClick={() => {
                          setValue('modelId', model.id);
                          setSelectedModelType('existing');
                          setValue('modelType', 'existing');
                        }}
                        className={`relative cursor-pointer rounded-md overflow-hidden border-2 transition-all ${
                          watch('modelId') === model.id 
                            ? 'border-amber-600' 
                            : 'border-gray-300 hover:border-gray-400'
                        }`}
                      >
                        <div className="aspect-square bg-gray-100 relative group">
                          {model.images ? (
                            <>
                              <img
                                src={model.images[0]}
                                alt={model.name}
                                className="w-full h-full object-cover"
                              />
                              {model.images.length > 1 && (
                                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-200 flex items-center justify-center">
                                  <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-white/90 backdrop-blur-sm rounded-lg p-2 shadow-lg">
                                    <div className="flex gap-1">
                                      {model.images.slice(0, 4).map((image, index) => (
                                        <img
                                          key={index}
                                          src={image}
                                          alt={`${model.name} ${index + 1}`}
                                          className="w-12 h-12 object-cover rounded border border-gray-200"
                                        />
                                      ))}
                                      {model.images.length > 4 && (
                                        <div className="w-12 h-12 bg-gray-200 rounded border border-gray-200 flex items-center justify-center">
                                          <span className="text-xs font-medium text-gray-600">+{model.images.length - 4}</span>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </>
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <div className="w-6 h-6 bg-gray-300 rounded" />
                            </div>
                          )}
                        </div>
                        <div className="absolute bottom-0 left-0 right-0 bg-black/60 p-1">
                          <p className="text-white text-xs font-medium truncate">{model.name}</p>
                        </div>
                        {watch('modelId') === model.id && (
                          <div className="absolute top-1 right-1 w-5 h-5 bg-amber-600 rounded-full flex items-center justify-center">
                            <Check className="w-3 h-3 text-white" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Step 3: Configuration */}
            <div className="pt-6 border-t border-gray-100 space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <Settings className="w-5 h-5 text-amber-600" /> Configure Settings
              </h2>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Garment Type *
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { key: 'top', label: 'Top', desc: 'Shirts, blouses, jackets' },
                  { key: 'bottom', label: 'Bottom', desc: 'Pants, skirts, shorts' },
                  { key: 'onepiece', label: 'One Piece', desc: 'Dresses, jumpsuits' },
                ].map(({ key, label, desc }) => (
                  <button
                    key={key}
                    type="button"
                    className={`p-3 rounded-lg border-2 text-left transition-all ${
                      selectedGarmentType === key
                        ? 'border-amber-600 bg-amber-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onClick={() => {
                      setSelectedGarmentType(key as 'top' | 'bottom' | 'onepiece');
                      setValue('garmentType', key as 'top' | 'bottom' | 'onepiece');
                    }}
                  >
                    <h4 className="font-medium text-gray-900 text-sm">{label}</h4>
                    <p className="text-xs text-gray-600 mt-1">{desc}</p>
                  </button>
                ))}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pose Instructions
                </label>
                <input
                  type="text"
                  {...register('pose')}
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-sm transition"
                  placeholder="e.g., standing, sitting, walking"
                />
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={onCancel}
                className="px-5 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100 text-sm font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!canSubmit() || isUploadingModel}
                className="px-5 py-3 bg-amber-600 text-white rounded-md hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition"
              >
                {isUploadingModel ? 'Uploading Model...' : 'Create Model'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default MultiStepTaskCreation;
