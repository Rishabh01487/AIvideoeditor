import { useState, useEffect } from 'react';
import { jobsAPI } from '../services/api';

export const useJobs = (projectId) => {
  const [job, setJob] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const getLatestJob = async () => {
    try {
      setIsLoading(true);
      const response = await jobsAPI.getLatest(projectId);
      setJob(response.data);
      setError(null);
    } catch (err) {
      if (err.response?.status !== 404) {
        setError(err.response?.data?.detail || 'Failed to fetch job status');
      }
      setJob(null);
    } finally {
      setIsLoading(false);
    }
  };

  const startEdit = async () => {
    try {
      setIsLoading(true);
      const response = await jobsAPI.startEdit(projectId);
      setJob(response.data);
      setError(null);
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to start editing';
      setError(errorMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const pollJobStatus = (jobId, interval = 2000) => {
    const intervalId = setInterval(async () => {
      try {
        const response = await jobsAPI.getStatus(jobId);
        setJob(response.data);

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error('Failed to poll job status:', err);
      }
    }, interval);

    return () => clearInterval(intervalId);
  };

  return { job, isLoading, error, getLatestJob, startEdit, pollJobStatus };
};
