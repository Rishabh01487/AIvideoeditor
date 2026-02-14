import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle, Loader } from 'lucide-react';

const ProcessingStatus = ({ job, isPolling }) => {
  if (!job) return null;

  const getStatusIcon = () => {
    switch (job.status) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={24} />;
      case 'failed':
        return <AlertCircle className="text-red-500" size={24} />;
      case 'processing':
      case 'pending':
        return <Loader className="text-blue-500 animate-spin" size={24} />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (job.status) {
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'processing':
        return 'Processing';
      case 'pending':
        return 'Pending';
      default:
        return 'Unknown';
    }
  };

  const getBgColor = () => {
    switch (job.status) {
      case 'completed':
        return 'bg-green-50';
      case 'failed':
        return 'bg-red-50';
      case 'processing':
      case 'pending':
        return 'bg-blue-50';
      default:
        return 'bg-gray-50';
    }
  };

  return (
    <div className={`rounded-lg p-6 ${getBgColor()}`}>
      <div className="flex items-center gap-4 mb-4">
        {getStatusIcon()}
        <div>
          <h3 className="text-lg font-bold">{getStatusText()}</h3>
          {isPolling && job.status === 'processing' && (
            <p className="text-sm text-gray-600">Processing your video...</p>
          )}
          {job.error && (
            <p className="text-sm text-red-600">{job.error}</p>
          )}
        </div>
      </div>

      {job.progress > 0 && job.status === 'processing' && (
        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${job.progress}%` }}
          ></div>
        </div>
      )}

      {job.progress > 0 && (
        <p className="text-sm text-gray-600 text-right">{Math.round(job.progress)}%</p>
      )}
    </div>
  );
};

export default ProcessingStatus;
