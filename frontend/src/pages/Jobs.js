import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { jobsAPI } from '../services/api';
import { 
  PlayIcon, 
  StopIcon, 
  ArrowPathIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

function Jobs() {
  const [filters, setFilters] = useState({
    status: '',
    job_type: '',
  });

  const queryClient = useQueryClient();

  const { data: jobs, isLoading } = useQuery(
    ['jobs', filters],
    () => jobsAPI.getJobs(filters)
  );

  const startGoogleMapsMutation = useMutation(
    jobsAPI.startGoogleMapsCrawl,
    {
      onSuccess: () => {
        toast.success('Google Maps crawl started successfully');
        queryClient.invalidateQueries('jobs');
      },
      onError: () => {
        toast.error('Failed to start Google Maps crawl');
      },
    }
  );

  const startWebsiteCheckMutation = useMutation(
    jobsAPI.startWebsiteCheck,
    {
      onSuccess: () => {
        toast.success('Website check started successfully');
        queryClient.invalidateQueries('jobs');
      },
      onError: () => {
        toast.error('Failed to start website check');
      },
    }
  );

  const cancelJobMutation = useMutation(
    jobsAPI.cancelJob,
    {
      onSuccess: () => {
        toast.success('Job cancelled successfully');
        queryClient.invalidateQueries('jobs');
      },
      onError: () => {
        toast.error('Failed to cancel job');
      },
    }
  );

  const retryJobMutation = useMutation(
    jobsAPI.retryJob,
    {
      onSuccess: () => {
        toast.success('Job retry started successfully');
        queryClient.invalidateQueries('jobs');
      },
      onError: () => {
        toast.error('Failed to retry job');
      },
    }
  );

  const handleStartGoogleMapsCrawl = () => {
    startGoogleMapsMutation.mutate({
      target_location: 'Amsterdam, Netherlands',
      target_industry: 'all',
    });
  };

  const handleStartWebsiteCheck = () => {
    startWebsiteCheckMutation.mutate({
      business_ids: [], // Empty array means check all unchecked businesses
    });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <ClockIcon className="h-5 w-5 text-blue-500" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'cancelled':
        return <StopIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage crawling and processing jobs
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleStartGoogleMapsCrawl}
            disabled={startGoogleMapsMutation.isLoading}
            className="btn-primary"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            Start Google Maps Crawl
          </button>
          <button
            onClick={handleStartWebsiteCheck}
            disabled={startWebsiteCheckMutation.isLoading}
            className="btn-secondary"
          >
            <GlobeAltIcon className="h-4 w-4 mr-2" />
            Start Website Check
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Filters</h3>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="input-field"
            >
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Job Type
            </label>
            <select
              value={filters.job_type}
              onChange={(e) => setFilters(prev => ({ ...prev, job_type: e.target.value }))}
              className="input-field"
            >
              <option value="">All types</option>
              <option value="google_maps_crawl">Google Maps Crawl</option>
              <option value="website_check">Website Check</option>
              <option value="data_processing">Data Processing</option>
            </select>
          </div>
        </div>
      </div>

      {/* Jobs List */}
      <div className="card">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Job
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(jobs?.items || []).map((job) => (
                  <tr key={job.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {job.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {job.target_location || 'N/A'}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {job.job_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(job.status)}
                        <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                          {job.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{ width: `${job.progress_percentage || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-500">
                          {job.progress_percentage || 0}%
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {job.processed_items || 0} / {job.total_items || 0}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(job.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        {job.status === 'running' && (
                          <button
                            onClick={() => cancelJobMutation.mutate(job.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Cancel job"
                          >
                            <StopIcon className="h-4 w-4" />
                          </button>
                        )}
                        {job.status === 'failed' && job.can_retry && (
                          <button
                            onClick={() => retryJobMutation.mutate(job.id)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Retry job"
                          >
                            <ArrowPathIcon className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Jobs;
