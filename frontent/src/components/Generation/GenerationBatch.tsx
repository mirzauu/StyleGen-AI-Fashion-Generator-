import React, { useState } from 'react';
// import { useSelector } from 'react-redux';
// import { RootState } from '../../store';
import { GenerationBatch as GenerationBatchType } from '../../types';
import { Download, Star, Share2, Image, ChevronDown } from 'lucide-react';
import { appAPI } from '../../services/api';
import { format } from 'date-fns';

interface GenerationBatchProps {
  batch: GenerationBatchType;
  batchNumber: number;
}

const GenerationBatch: React.FC<GenerationBatchProps> = ({ batch, batchNumber }) => {
  // const { user } = useSelector((state: RootState) => state.auth);
  const [isExpanded, setIsExpanded] = useState(true);
  const [zoomedImageUrl, setZoomedImageUrl] = useState<string | null>(null);

  const handleDownload = async (imageUrl: string) => {
    try {
      const response = await fetch(imageUrl, { mode: 'cors' });
      if (!response.ok) throw new Error('Network response was not ok');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = `generated-image-${Date.now()}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading the image:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'done':
        return 'text-green-600 bg-green-100';
      case 'generating':
      case 'pending':
        return 'text-amber-700 bg-amber-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const handleDownloadBatchZip = async () => {
    try {
      const blob = await appAPI.downloadBatchZip(batch.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `batch-${batchNumber}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Failed to download batch zip', e);
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
      case 'done':
        return 'Completed';
      case 'generating':
        return 'Generating';
      case 'pending':
        return 'Pending';
      case 'failed':
        return 'Failed';
      default:
        return status;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
        <div className="flex items-center justify-between w-full p-6 pb-0">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
            >
              <ChevronDown
                className={`w-4 h-4 text-gray-500 transition-transform ${
                  isExpanded ? 'rotate-0' : '-rotate-90'
                }`}
              />
            </button>
            <h3 className="text-base font-semibold text-gray-900">Batch {batchNumber}</h3>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                batch.status
              )}`}
            >
              {getStatusText(batch.status)}
            </span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <span className="text-xs">Created: {format(new Date(batch.createdAt), 'MMM d, HH:mm')}</span>
            <button
              onClick={handleDownloadBatchZip}
              className="ml-3 inline-flex items-center px-3 py-1.5 rounded-md bg-purple-600 text-white hover:bg-purple-700 transition-colors"
              title="Download all images in this batch as ZIP"
            >
              <Download className="w-4 h-4 mr-1" />
              Download ZIP
            </button>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-6 pb-6 space-y-8">
          {batch.garmentImages.map((garmentImage, garmentIndex) => (
            <div
              key={garmentImage.garmentImageId}
              className="border-b border-gray-100 pb-8 last:border-b-0 last:pb-0"
            >
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                {/* Original Garment Image */}
                <div className="lg:col-span-1 space-y-3">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Original Garment</h4>
                  <div className="relative group">
                    <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden shadow-sm">
                      <img
                        src={garmentImage.imageUrl}
                        alt={`Garment ${garmentIndex + 1}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.src = 'https://images.pexels.com/photos/996329/pexels-photo-996329.jpeg';
                        }}
                      />
                    </div>
                    <div className="absolute top-2 left-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs font-medium">
                      Original
                    </div>
                  </div>
                </div>

                {/* Generated Images */}
                <div className="lg:col-span-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-4">Generated Images</h4>
                  {garmentImage.generatedImages.length > 0 ? (
                    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
                      {garmentImage.generatedImages.map((generatedImage) => (
                        <div key={generatedImage.generatedImageId} className="space-y-3">
                          <div className="relative group">
                            <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                              <img
                                src={generatedImage.outputUrl}
                                alt={`Generated ${generatedImage.poseLabel}`}
                                className="w-full h-full object-cover cursor-pointer"
                                onClick={() => setZoomedImageUrl(generatedImage.outputUrl)}
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement;
                                  target.src = 'https://images.pexels.com/photos/1065084/pexels-photo-1065084.jpeg';
                                }}
                              />
                            </div>

                            

                            {/* Action Buttons */}
                            <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity">
                              <div className="flex items-center space-x-2">
                                <button className="p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100 transition-all shadow-sm">
                                  <Star className="w-4 h-4 text-gray-600" />
                                </button>
                                <button className="p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100 transition-all shadow-sm">
                                  <Share2 className="w-4 h-4 text-gray-600" />
                                </button>
                              </div>

                              <button
                                onClick={() => handleDownload(generatedImage.outputUrl)}
                                className="p-2 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition-all shadow-sm"
                              >
                                <Download className="w-4 h-4" />
                              </button>
                            </div>
                          </div>

                          {/* Download Options */}
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-500">Pose: {generatedImage.poseLabel}</span>
                            <button
                              onClick={() => handleDownload(generatedImage.outputUrl)}
                              className="p-2 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition-all shadow-sm"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-32 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                      <div className="text-center">
                        <Image className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">No generated images available</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Image Zoom Modal */}
      {zoomedImageUrl && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70"
          onClick={() => setZoomedImageUrl(null)}
        >
          <div className="relative max-w-screen-md max-h-screen-md">
            <img
              src={zoomedImageUrl}
              alt="Zoomed"
              className="rounded shadow-lg max-w-full max-h-[80vh]"
              onClick={(e) => e.stopPropagation()}
            />
            <button
              onClick={() => setZoomedImageUrl(null)}
              className="absolute top-2 right-2 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
              aria-label="Close zoomed image"
            >
              &times;
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerationBatch;
