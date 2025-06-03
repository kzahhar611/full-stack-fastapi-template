'use client'

import React from 'react'
import { useQuery } from 'react-query'
import DashboardLayout from '@/components/layout/DashboardLayout'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import Button from '@/components/common/Button'
import { useAuth } from '@/contexts/AuthContext'
import { rfpService } from '@/services/rfp'
import { 
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  FolderIcon,
  ChartBarIcon,
  PlusIcon,
  EyeIcon
} from '@heroicons/react/24/outline'
import { useRouter } from 'next/navigation'

const DashboardPage: React.FC = () => {
  const { user } = useAuth()
  const router = useRouter()

  // Fetch recent RFPs
  const { data: rfps, isLoading: rfpsLoading } = useQuery(
    'recent-rfps',
    () => rfpService.getRFPs({ limit: 5 }),
    {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  )

  const stats = [
    {
      name: 'Total RFPs',
      value: rfps?.length || 0,
      icon: DocumentTextIcon,
      color: 'bg-blue-500',
      href: '/rfps'
    },
    {
      name: 'Active Proposals',
      value: '0',
      icon: ClipboardDocumentListIcon,
      color: 'bg-green-500',
      href: '/proposals'
    },
    {
      name: 'Projects',
      value: '0',
      icon: FolderIcon,
      color: 'bg-yellow-500',
      href: '/projects'
    },
    {
      name: 'Analytics',
      value: '0',
      icon: ChartBarIcon,
      color: 'bg-purple-500',
      href: '/analytics'
    }
  ]

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name}!
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Here's what's happening with your RFPs and proposals today.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-4">
            <Button
              leftIcon={<PlusIcon className="h-5 w-5" />}
              onClick={() => router.push('/rfps/create')}
            >
              Create RFP
            </Button>
            <Button
              variant="outline"
              leftIcon={<DocumentTextIcon className="h-5 w-5" />}
              onClick={() => router.push('/rfps')}
            >
              View All RFPs
            </Button>
            <Button
              variant="outline"
              leftIcon={<ClipboardDocumentListIcon className="h-5 w-5" />}
              onClick={() => router.push('/proposals')}
            >
              View Proposals
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {stats.map((stat) => (
            <div
              key={stat.name}
              className="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push(stat.href)}
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`p-3 rounded-md ${stat.color}`}>
                      <stat.icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stat.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Recent RFPs */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Recent RFPs
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/rfps')}
              >
                View All
              </Button>
            </div>

            {rfpsLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner size="lg" />
              </div>
            ) : rfps && rfps.length > 0 ? (
              <div className="overflow-hidden">
                <ul className="divide-y divide-gray-200">
                  {rfps.map((rfp) => (
                    <li key={rfp.id} className="py-4">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {rfp.title}
                          </p>
                          <p className="text-sm text-gray-500">
                            {rfp.rfp_number} • {rfp.organization}
                          </p>
                          <p className="text-xs text-gray-400">
                            Created {new Date(rfp.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex-shrink-0">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                            ${rfp.status === 'published' ? 'bg-green-100 text-green-800' :
                              rfp.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                            {rfp.status}
                          </span>
                        </div>
                        <div className="flex-shrink-0">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/rfps/${rfp.id}`)}
                            leftIcon={<EyeIcon className="h-4 w-4" />}
                          >
                            View
                          </Button>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="text-center py-8">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No RFPs</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Get started by creating your first RFP.
                </p>
                <div className="mt-6">
                  <Button
                    onClick={() => router.push('/rfps/create')}
                    leftIcon={<PlusIcon className="h-5 w-5" />}
                  >
                    Create RFP
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default DashboardPage