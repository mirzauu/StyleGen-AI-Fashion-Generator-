import React from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, X } from 'lucide-react';

interface GarmentUploadProps {
  onFilesSelected: (files: File[]) => void;
  selectedFiles: File[];
  onRemoveFile: (index: number) => void;
  isFirstBatch: boolean;
  maxFiles?: number;
}

const GarmentUpload: React.FC<GarmentUploadProps> = ({
  onFilesSelected,
  selectedFiles,
  onRemoveFile,
  isFirstBatch,
  maxFiles = 9,
}) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
    },
    maxFiles: maxFiles - selectedFiles.length,
    maxSize: 20 * 1024 * 1024, // 20MB
    onDrop: (acceptedFiles) => {
      const newFiles = [...selectedFiles, ...acceptedFiles].slice(0, maxFiles);
      onFilesSelected(newFiles);
    },
  });

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-4 text-center transition-all duration-200 cursor-pointer ${
          isDragActive
            ? 'border-purple-400 bg-purple-50'
            : selectedFiles.length === 0
            ? 'border-gray-300 hover:border-purple-400 hover:bg-purple-50'
            : 'border-gray-200 hover:border-gray-300'
        }`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-2">
          <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
            <Upload className="w-5 h-5 text-purple-600" />
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-1">
              {isFirstBatch ? 'Upload garment images to start generation' : 'Upload More Garments'}
            </h3>
            <p className="text-xs text-gray-600 mb-1">
              Drag and drop file here or <span className="text-purple-600 font-medium">upload here</span>
            </p>
            <p className="text-xs text-gray-500">
              A maximum of 5 uploads at a time, each size should not exceed 20MB, and GIF format is not supported
            </p>
          </div>
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-gray-700 mb-2">
            Support for Model Images, Mannequin Images, Flat-Lay Images. Video Generation is available now.
          </h4>
          
          <div className="flex flex-wrap gap-3">
            {selectedFiles.map((file, index) => (
              <div key={index} className="relative group">
                <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden shadow-sm">
                  {file.type.startsWith('image/') ? (
                    <img
                      src={URL.createObjectURL(file)}
                      alt={`Garment ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Image className="w-4 h-4 text-gray-400" />
                    </div>
                  )}
                </div>
                
                <button
                  onClick={() => onRemoveFile(index)}
                  className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 shadow-sm"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GarmentUpload;