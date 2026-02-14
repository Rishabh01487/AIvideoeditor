import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Play } from 'lucide-react';
import { projectsAPI, assetsAPI } from '../../services/api';
import { useJobs } from '../../hooks/useJobs';
import UploadZone from '../UploadZone/UploadZone';
import ProcessingStatus from '../ProcessingStatus/ProcessingStatus';
import VideoPlayer from '../VideoPlayer/VideoPlayer';

const Editor = () => {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [assets, setAssets] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [prompt, setPrompt] = useState('');
  const { job, isLoading: isJobLoading, startEdit, pollJobStatus } = useJobs(projectId);

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  useEffect(() => {
    if (job?.status === 'processing') {
      const unsubscribe = pollJobStatus(job.id);
      return unsubscribe;
    }
  }, [job]);

  const fetchProject = async () => {
    try {
      setIsLoading(true);
      const [projectRes, assetsRes] = await Promise.all([
        projectsAPI.get(projectId),
        assetsAPI.getProjectAssets(projectId),
      ]);
      setProject(projectRes.data);
      setAssets(assetsRes.data);
      setPrompt(projectRes.data.prompt || '');
      setError('');
    } catch (err) {
      setError('Failed to load project');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePrompt = async () => {
    try {
      await projectsAPI.update(projectId, { prompt });
      setProject((prev) => ({ ...prev, prompt }));
    } catch (err) {
      setError('Failed to update prompt');
    }
  };

  const handleStartEdit = async () => {
    try {
      await startEdit();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start editing');
    }
  };

  const handleDeleteAsset = async (assetId) => {
    if (window.confirm('Delete this asset?')) {
      try {
        await assetsAPI.delete(assetId);
        setAssets((prev) => prev.filter((a) => a.id !== assetId));
      } catch (err) {
        setError('Failed to delete asset');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading project...</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-600">Project not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-blue-500 hover:text-blue-600 mb-4"
          >
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{project.title}</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Upload & Assets */}
          <div className="lg:col-span-2 space-y-8">
            {/* Upload Zone */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold mb-4">Upload Videos & Images</h2>
              <UploadZone projectId={projectId} onUploadComplete={fetchProject} />
            </div>

            {/* Assets List */}
            {assets.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Uploaded Assets ({assets.length})</h2>
                <div className="space-y-3">
                  {assets.map((asset) => (
                    <div key={asset.id} className="flex items-center justify-between bg-gray-50 p-4 rounded">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{asset.original_filename}</p>
                        <p className="text-sm text-gray-500">
                          {asset.type === 'video' && asset.duration
                            ? `${asset.duration.toFixed(1)}s`
                            : asset.type}
                        </p>
                      </div>
                      <button
                        onClick={() => handleDeleteAsset(asset.id)}
                        className="text-red-500 hover:text-red-700 font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Results */}
            {job?.status === 'completed' && job.result?.output_key && (
              <VideoPlayer videoKey={job.result.output_key} />
            )}
          </div>

          {/* Right Column: Prompt & Actions */}
          <div className="space-y-6">
            {/* Prompt Input */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold mb-4">Editing Prompt</h2>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe what edits you want. E.g., 'Make it 30 seconds, vintage look, upbeat music'"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 h-32 resize-none"
              />
              <button
                onClick={handleUpdatePrompt}
                className="w-full mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
              >
                Save Prompt
              </button>
            </div>

            {/* Job Status */}
            {job && (
              <ProcessingStatus
                job={job}
                isPolling={isJobLoading && job?.status === 'processing'}
              />
            )}

            {/* Start Editing Button */}
            {(!job || ['draft', 'failed'].includes(job.status)) && assets.length > 0 && (
              <button
                onClick={handleStartEdit}
                disabled={isJobLoading}
                className="w-full flex items-center justify-center gap-2 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition font-bold text-lg"
              >
                <Play size={20} />
                {isJobLoading ? 'Starting...' : 'Start Editing'}
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Editor;
