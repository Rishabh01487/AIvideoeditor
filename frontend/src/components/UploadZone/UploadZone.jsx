import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X } from 'lucide-react';
import { assetsAPI } from '../../services/api';

const UploadZone = ({ projectId, onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState({});

  const onDrop = async (acceptedFiles) => {
    setError('');
    setUploading(true);

    for (const file of acceptedFiles) {
      const fileType = file.type.startsWith('video') ? 'video' : 'image';

      try {
        // Get presigned URL
        const presignedResponse = await assetsAPI.getPresignedUrl(projectId, {
          filename: file.name,
          content_type: file.type,
          file_size: file.size,
        });

        const { presigned_url, storage_key } = presignedResponse.data;

        // Upload to S3
        setUploadProgress((prev) => ({ ...prev, [file.name]: 'uploading' }));

        const formData = new FormData();
        Object.keys(presignedResponse.data).forEach((key) => {
          if (key !== 'presigned_url' && key !== 'storage_key') {
            formData.append(key, presignedResponse.data[key]);
          }
        });
        formData.append('file', file);

        await fetch(presigned_url, {
          method: 'POST',
          body: formData,
        });

        // Confirm upload
        await assetsAPI.confirmUpload(
          projectId,
          storage_key,
          fileType,
          file.name,
          file.size
        );

        setUploadProgress((prev) => ({ ...prev, [file.name]: 'complete' }));
        onUploadComplete?.();
      } catch (err) {
        setError(`Failed to upload ${file.name}`);
        setUploadProgress((prev) => ({ ...prev, [file.name]: 'error' }));
      }
    }

    setUploading(false);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv'],
      'image/*': ['.jpg', '.jpeg', '.png', '.gif'],
    },
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload size={48} className="mx-auto mb-4 text-gray-400" />
        <p className="text-lg font-medium text-gray-700">
          {isDragActive ? 'Drop files here' : 'Drag videos or images here'}
        </p>
        <p className="text-sm text-gray-500 mt-2">
          or click to select files
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mt-4 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError('')}>
            <X size={20} />
          </button>
        </div>
      )}

      {uploading && (
        <div className="mt-4 space-y-2">
          <p className="text-sm text-gray-600">Uploading...</p>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full animate-pulse w-1/2"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadZone;
