import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { websiteChecksAPI } from '../services/api';
import { 
  GlobeAltIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

function WebsiteChecks() {
  const [filters, setFilters] = useState({
    business_id: '',
    check_type: '',
  });

  const { data: websiteChecks, isLoading } = useQuery(
    ['website-checks', filters],
    () => websiteChecksAPI.getWebsiteChecks(filters)
  );

  const getStatusIcon = (websiteExists) => {
    if (websiteExists === true) {
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    } else if (websiteExists === false) {
      return <XCircleIcon className="h-5 w-5 text-red-500" />;
    } else {
      return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (websiteExists) => {
    if (websiteExists === true) {
      return 'bg-green-100 text-green-800';
    } else if (websiteExists === false) {
      return 'bg-red-100 text-red-800';
    } else {
      return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getStatusText = (websiteExists) => {
    if (websiteExists === true) {
      return 'Website Found';
    } else if (websiteExists === false) {
      return 'No Website';
    } else {
      return 'Unknown';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Website Checks</h1>
        <p className="mt-1 text-sm text-gray-500">
          View website verification results and details
        </p>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Filters</h3>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Check Type
            </label>
            <select
              value={filters.check_type}
              onChange={(e) => setFilters(prev => ({ ...prev, check_type: e.target.value }))}
              className="input-field"
            >
              <option value="">All types</option>
              <option value="dns">DNS Check</option>
              <option value="http">HTTP Check</option>
              <option value="whois">WHOIS Check</option>
              <option value="google_search">Google Search</option>
            </select>
          </div>
        </div>
      </div>

      {/* Website Checks List */}
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
                    Business
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Check Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    URL Checked
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Response Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Checked At
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(websiteChecks?.items || []).map((check) => (
                  <tr key={check.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {check.business?.name || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-500">
                        {check.business?.city}, {check.business?.country}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {check.check_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {check.url_checked || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(check.website_exists)}
                        <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(check.website_exists)}`}>
                          {getStatusText(check.website_exists)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{ width: `${check.confidence_score || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-500">
                          {check.confidence_score || 0}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {check.response_time ? `${check.response_time}ms` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(check.checked_at).toLocaleDateString()}
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

export default WebsiteChecks;
