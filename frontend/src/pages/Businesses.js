import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { businessAPI } from '../services/api';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  EyeIcon,
  GlobeAltIcon,
  BuildingOfficeIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

function Businesses() {
  const [filters, setFilters] = useState({
    city: '',
    country: '',
    website_exists: '',
    is_zzp: '',
    source: '',
    search: '',
  });

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);

  const { data: businesses, isLoading, error } = useQuery(
    ['businesses', filters, currentPage],
    () => businessAPI.getBusinesses({
      ...filters,
      skip: (currentPage - 1) * pageSize,
      limit: pageSize,
    }),
    {
      keepPreviousData: true,
    }
  );

  const { data: stats } = useQuery('business-stats', businessAPI.getBusinessStats);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({
      city: '',
      country: '',
      website_exists: '',
      is_zzp: '',
      source: '',
      search: '',
    });
    setCurrentPage(1);
  };

  const totalPages = Math.ceil((businesses?.total || 0) / pageSize);

  if (error) {
    toast.error('Failed to load businesses');
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Businesses</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage and view all discovered businesses
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            Total: {stats?.total_businesses || 0}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Filters</h3>
          <button
            onClick={clearFilters}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Clear all
          </button>
        </div>

        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  placeholder="Search by name, city, industry..."
                  className="input-field pl-10"
                />
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              </div>
            </div>

            {/* City */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                value={filters.city}
                onChange={(e) => handleFilterChange('city', e.target.value)}
                placeholder="Enter city"
                className="input-field"
              />
            </div>

            {/* Country */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <select
                value={filters.country}
                onChange={(e) => handleFilterChange('country', e.target.value)}
                className="input-field"
              >
                <option value="">All countries</option>
                <option value="Netherlands">Netherlands</option>
                <option value="Belgium">Belgium</option>
                <option value="Luxembourg">Luxembourg</option>
                <option value="Germany">Germany</option>
              </select>
            </div>

            {/* Website exists */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Website Status
              </label>
              <select
                value={filters.website_exists}
                onChange={(e) => handleFilterChange('website_exists', e.target.value)}
                className="input-field"
              >
                <option value="">All</option>
                <option value="true">Has website</option>
                <option value="false">No website</option>
              </select>
            </div>

            {/* ZZP */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Type
              </label>
              <select
                value={filters.is_zzp}
                onChange={(e) => handleFilterChange('is_zzp', e.target.value)}
                className="input-field"
              >
                <option value="">All types</option>
                <option value="true">ZZP</option>
                <option value="false">Company</option>
              </select>
            </div>

            {/* Source */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Source
              </label>
              <select
                value={filters.source}
                onChange={(e) => handleFilterChange('source', e.target.value)}
                className="input-field"
              >
                <option value="">All sources</option>
                <option value="google_maps">Google Maps</option>
                <option value="linkedin">LinkedIn</option>
                <option value="facebook">Facebook</option>
                <option value="manual">Manual</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end">
            <button type="submit" className="btn-primary">
              <FunnelIcon className="h-4 w-4 mr-2" />
              Apply Filters
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      <div className="card">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Business
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Website
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Source
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Confidence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {(businesses?.items || []).map((business) => (
                    <tr key={business.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {business.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {business.industry || 'N/A'}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {business.city}, {business.country}
                        </div>
                        <div className="text-sm text-gray-500">
                          {business.postal_code}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          business.is_zzp 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {business.is_zzp ? 'ZZP' : 'Company'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {business.website_exists ? (
                          <div className="flex items-center">
                            <GlobeAltIcon className="h-4 w-4 text-green-500 mr-1" />
                            <span className="text-sm text-green-600">Yes</span>
                          </div>
                        ) : (
                          <div className="flex items-center">
                            <XCircleIcon className="h-4 w-4 text-red-500 mr-1" />
                            <span className="text-sm text-red-600">No</span>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {business.source}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className="bg-primary-600 h-2 rounded-full" 
                              style={{ width: `${business.confidence_score || 0}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-500">
                            {business.confidence_score || 0}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-primary-600 hover:text-primary-900">
                          <EyeIcon className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 sm:px-6">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    className="btn-secondary disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="btn-secondary disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing{' '}
                      <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span>
                      {' '}to{' '}
                      <span className="font-medium">
                        {Math.min(currentPage * pageSize, businesses?.total || 0)}
                      </span>
                      {' '}of{' '}
                      <span className="font-medium">{businesses?.total || 0}</span>
                      {' '}results
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                        <button
                          key={page}
                          onClick={() => setCurrentPage(page)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            page === currentPage
                              ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      ))}
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Businesses;
