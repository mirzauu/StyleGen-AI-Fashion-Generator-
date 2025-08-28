import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { ArrowLeft } from 'lucide-react';
import { RootState, AppDispatch } from '../../store';
import { generateImages, fetchTaskBatches } from '../../store/slices/appSlice';
import GarmentUpload from './GarmentUpload';
import GenerationBatch from './GenerationBatch';

interface GenerationInterfaceProps {
  onBack: () => void;
}

const GenerationInterface: React.FC<GenerationInterfaceProps> = ({ onBack }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentTask, generations, isLoading } = useSelector((state: RootState) => state.app);
  const [currentFiles, setCurrentFiles] = React.useState<File[]>([]);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [showLoading, setShowLoading] = React.useState(false);
  const [recentBatchId, setRecentBatchId] = React.useState<string | null>(null);
  const [isVisible, setIsVisible] = React.useState(true); // Controls rendering for full reset

  React.useEffect(() => {
    if (currentTask) {
      dispatch(fetchTaskBatches(currentTask.id));
    }
    setRecentBatchId(null);
  }, [currentTask, dispatch]);

  React.useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;

    if (isGenerating) {
      timer = setTimeout(() => {
        const runReload = async () => {
          if (currentTask) {
            await dispatch(fetchTaskBatches(currentTask.id));
          }
          setIsVisible(false);
          setTimeout(() => {
            setIsGenerating(false);
            setShowLoading(false);
            setCurrentFiles([]);
            setRecentBatchId(null);
            setIsVisible(true);
          }, 50);
        };
        runReload();
      }, 60000);
    }

    return () => clearTimeout(timer);
  }, [isGenerating, currentTask, dispatch]);

  const handleGenerate = async () => {
    if (!currentTask || currentFiles.length === 0) return;

    setIsGenerating(true);
    setShowLoading(true);
    let batchId = null;
    try {
      const result = await dispatch(generateImages({
        taskId: currentTask.id,
        garmentImages: currentFiles,
      })).unwrap();
      batchId = result && result.id ? result.id : null;
      // Do not immediately refetch here; we will refetch after 1 minute to allow processing time
    } catch (error) {
      console.error('Generation failed:', error);
    }

    setRecentBatchId(batchId);
  };

  const removeFile = (index: number) => {
    setCurrentFiles(files => files.filter((_, i) => i !== index));
  };

  const isFirstBatch = generations.length === 0;
  const canGenerate = currentFiles.length > 0 && !isGenerating;

  let displayedBatches = generations;
  if (recentBatchId) {
    const recentBatch = generations.find(b => b.id === recentBatchId);
    displayedBatches = recentBatch ? [recentBatch] : [];
  }

  if (!isVisible) {
    return null; // Unmounting content for reset
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="flex-shrink-0 bg-white border-b border-gray-200 px-2 sm:px-4 md:px-6 py-3 md:py-4">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">{currentTask?.name}</h1>
            <p className="text-xs text-gray-500">Task #{currentTask?.id}</p>
          </div>
        </div>
      </div>
      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2 sm:p-4 md:p-6">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="w-6 h-6 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                <p className="text-gray-600">Loading task batches...</p>
              </div>
            </div>
          )}

          {!isLoading && !showLoading && (
            <div className="space-y-6 mb-8">
              {displayedBatches.map((batch, index) => (
                <GenerationBatch key={batch.id} batch={batch} batchNumber={index + 1} />
              ))}
            </div>
          )}

          {!isLoading && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6 mb-6 relative">
              <GarmentUpload
                onFilesSelected={setCurrentFiles}
                selectedFiles={currentFiles}
                onRemoveFile={removeFile}
                isFirstBatch={isFirstBatch}
              />

              {currentFiles.length > 0 && (
                <div className="mt-6 flex justify-center">
                  <button
                    onClick={handleGenerate}
                    disabled={!canGenerate}
                    className="px-8 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm"
                  >
                    {isGenerating
                      ? (
                        <span className="flex items-center gap-2">
                          <span className="w-5 h-5 border-2 border-white border-t-purple-600 rounded-full animate-spin"></span>
                          Generating...
                        </span>
                      )
                      : isFirstBatch
                        ? 'Generate Images'
                        : 'Generate Next Batch'
                    }
                  </button>
                </div>
              )}

              {showLoading && (
                <div className="absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center z-10">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mb-2"></div>
                    <span className="text-purple-700 font-semibold">Generating images... Please wait for 1 minute.</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GenerationInterface;
