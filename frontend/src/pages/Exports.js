import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { exportsAPI } from '../services/api';
import { 
  ArrowDownTrayIcon,
  DocumentArrowDownIcon,
  TableCellsIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

function Exports() {
  const [exportFilters, setExportFilters] = useState({
    city: '',
    country: '',
    website_exists: '',
    is_zzp: '',
    source: '',
  });

  const exportCSVMutation = useMutation(
    exportsAPI.exportBusinessesCSV,
    {
      onSuccess: (response) => {
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `businesses_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('CSV export downloaded successfully');
      },
      onError: () => {
        toast.error('Failed to export CSV');
      },
    }
  );

  const exportExcelMutation = useMutation(
    exportsAPI.exportBusinessesExcel,
    {
      onSuccess: (response) => {
        // Create download link
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `businesses_export_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('Excel export downloaded successfully');
      },
      onError: () => {
        toast.error('Failed to export Excel');
      },
    }
  );

  const exportZZPWithoutWebsiteMutation = useMutation(
    exportsAPI.exportZZPWithoutWebsite,
    {
      onSuccess: (response) => {
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `zzp_without_website_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('ZZP without website export downloaded successfully');
      },
      onError: () => {
        toast.error('Failed to export ZZP data');
      },
    }
  );

  const handleExportCSV = () => {
    exportCSVMutation.mutate(exportFilters);
  };

  const handleExportExcel = () => {
    exportExcelMutation.mutate(exportFilters);
  };

  const handleExportZZPWithoutWebsite = () => {
    exportZZPWithoutWebsiteMutation.mutate();
  };

  const exportOptions = [
    {
      title: 'Export All Businesses (CSV)',
      description: 'Download all businesses data in CSV format with current filters',
      icon: TableCellsIcon,
      action: handleExportCSV,
      loading: exportCSVMutation.isLoading,
      color: 'bg-blue-500',
    },
    {
      title: 'Export All Businesses (Excel)',
      description: 'Download all businesses data in Excel format with summary sheet',
      icon: DocumentArrowDownIcon,
      action: handleExportExcel,
      loading: exportExcelMutation.isLoading,
      color: 'bg-green-500',
    },
    {
      title: 'Export ZZP Without Website',
      description: 'Download only ZZP businesses that don\'t have a website',
      icon: BuildingOfficeIcon,
      action: handleExportZZPWithoutWebsite,
      loading: exportZZPWithoutWebsiteMutation.isLoading,
      color: 'bg-red-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Exports</h1>
        <p className="mt-1 text-sm text-gray-500">
          Export business data in various formats
        </p>
      </div>

      {/* Export Filters */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Export Filters</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              City
            </label>
            <input
              type="text"
              value={exportFilters.city}
              onChange={(e) => setExportFilters(prev => ({ ...prev, city: e.target.value }))}
              placeholder="Enter city"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Country
            </label>
            <select
              value={exportFilters.country}
              onChange={(e) => setExportFilters(prev => ({ ...prev, country: e.target.value }))}
              className="input-field"
            >
              <option value="">All countries</option>
              <option value="Netherlands">Netherlands</option>
              <option value="Belgium">Belgium</option>
              <option value="Luxembourg">Luxembourg</option>
              <option value="Germany">Germany</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Website Status
            </label>
            <select
              value={exportFilters.website_exists}
              onChange={(e) => setExportFilters(prev => ({ ...prev, website_exists: e.target.value }))}
              className="input-field"
            >
              <option value="">All</option>
              <option value="true">Has website</option>
              <option value="false">No website</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Business Type
            </label>
            <select
              value={exportFilters.is_zzp}
              onChange={(e) => setExportFilters(prev => ({ ...prev, is_zzp: e.target.value }))}
              className="input-field"
            >
              <option value="">All types</option>
              <option value="true">ZZP</option>
              <option value="false">Company</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Source
            </label>
            <select
              value={exportFilters.source}
              onChange={(e) => setExportFilters(prev => ({ ...prev, source: e.target.value }))}
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
      </div>

      {/* Export Options */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {exportOptions.map((option, index) => (
          <div key={index} className="card">
            <div className="flex items-center mb-4">
              <div className={`flex-shrink-0 ${option.color} rounded-md p-3`}>
                <option.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">{option.title}</h3>
                <p className="text-sm text-gray-500">{option.description}</p>
              </div>
            </div>
            <button
              onClick={option.action}
              disabled={option.loading}
              className="w-full btn-primary disabled:opacity-50"
            >
              {option.loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Exporting...
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                  Download
                </div>
              )}
            </button>
          </div>
        ))}
      </div>

      {/* Export Information */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Export Information</h3>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-start">
            <div className="flex-shrink-0 w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3"></div>
            <p>CSV exports include all business fields and are compatible with Excel and other spreadsheet applications.</p>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0 w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3"></div>
            <p>Excel exports include a summary sheet with statistics and charts in addition to the detailed data.</p>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0 w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3"></div>
            <p>Large exports may take a few moments to process. Please wait for the download to complete.</p>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0 w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3"></div>
            <p>Exports are limited to 10,000 records per download for performance reasons.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Exports;
