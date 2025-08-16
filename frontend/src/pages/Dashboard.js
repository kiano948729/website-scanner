import React from 'react';
import { useQuery } from 'react-query';
import { dashboardAPI } from '../services/api';
import { 
  BuildingOfficeIcon, 
  GlobeAltIcon, 
  CogIcon, 
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B'];

function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery('dashboard-stats', dashboardAPI.getStats);
  const { data: recentActivity, isLoading: activityLoading } = useQuery('recent-activity', dashboardAPI.getRecentActivity);
  const { data: topCities, isLoading: citiesLoading } = useQuery('top-cities', dashboardAPI.getTopCities);
  const { data: topIndustries, isLoading: industriesLoading } = useQuery('top-industries', dashboardAPI.getTopIndustries);

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      name: 'Total Businesses',
      value: stats?.total_businesses || 0,
      icon: BuildingOfficeIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Without Website',
      value: stats?.businesses_without_website || 0,
      icon: GlobeAltIcon,
      color: 'bg-red-500',
    },
    {
      name: 'ZZP Businesses',
      value: stats?.zzp_businesses || 0,
      icon: BuildingOfficeIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Active Jobs',
      value: stats?.active_jobs || 0,
      icon: CogIcon,
      color: 'bg-yellow-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your business scanning activities
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className={`flex-shrink-0 ${stat.color} rounded-md p-3`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                  <dd className="text-lg font-medium text-gray-900">{stat.value.toLocaleString()}</dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top Cities */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Cities</h3>
          {citiesLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topCities || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="city" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Top Industries */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Industries</h3>
          {industriesLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Array.isArray(topIndustries) ? topIndustries : []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(Array.isArray(topIndustries) ? topIndustries : []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        {activityLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="flow-root">
            <ul className="-mb-8">
              {(recentActivity?.recent_businesses || []).slice(0, 5).map((business, businessIdx) => (
                <li key={business.id}>
                  <div className="relative pb-8">
                    {businessIdx !== (recentActivity?.recent_businesses || []).length - 1 ? (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    ) : null}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                          <BuildingOfficeIcon className="h-5 w-5 text-white" />
                        </span>
                      </div>
                      <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                        <div>
                          <p className="text-sm text-gray-500">
                            New business found: <span className="font-medium text-gray-900">{business.name}</span>
                          </p>
                          <p className="text-sm text-gray-500">
                            {business.city}, {business.country}
                          </p>
                        </div>
                        <div className="whitespace-nowrap text-right text-sm text-gray-500">
                          {new Date(business.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
