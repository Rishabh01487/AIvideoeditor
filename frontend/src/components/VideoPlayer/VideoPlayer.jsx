import React from 'react';
import ReactPlayer from 'react-player';
import { Download } from 'lucide-react';

const VideoPlayer = ({ videoKey }) => {
  if (!videoKey) return null;

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const videoUrl = `${API_BASE_URL}/videos/${videoKey}`;

  const handleDownload = async () => {
    try {
      const response = await fetch(videoUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `video_${Date.now()}.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold mb-4">Generated Video</h3>

      <div className="mb-6 bg-black rounded-lg overflow-hidden">
        <ReactPlayer
          url={videoUrl}
          controls
          width="100%"
          height="100%"
          playing={false}
        />
      </div>

      <button
        onClick={handleDownload}
        className="flex items-center gap-2 bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition w-full justify-center"
      >
        <Download size={20} />
        Download Video
      </button>
    </div>
  );
};

export default VideoPlayer;
