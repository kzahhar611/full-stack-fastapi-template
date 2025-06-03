'use client'

import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { useRouter } from 'next/navigation'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Table from '@/components/common/Table'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import Select from '@/components/common/Select'
import Badge from '@/components/common/Badge'
import { rfpService } from '@/services/rfp'
import { RFPListItem, RFPStatus, RFPType, RFPFilters } from '@/types/rfp'
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

const RFPsPage: React.FC = () => {
  const router = useRouter()
  const [filters, setFilters] = useState<RFPFilters>({
    search: '',
    status: undefined,
    my_rfps: false,
    order_by: 'created_at',
    order_direction: 'desc'
  })

  // Fetch RFPs with filters
  const { data: rfps, isLoading, refetch } = useQuery(
    ['rfps', filters],
    () => rfpService.getRFPs(filters),
    {
      staleTime: 30000, // 30 seconds
    }
  )

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'draft', label: 'Draft' },
    { value: 'published', label: 'Published' },
    { value: 'under_review', label: 'Under Review' },
    { value: 'closed', label: 'Closed' },
    { value: 'awarded', label: 'Awarded' },
    { value: 'cancelled', label: 'Cancelled' },
  ]

  const getStatusVariant = (status: RFPStatus) => {
    switch (status) {
      case 'published': return 'success'
      case 'draft': return 'warning'
      case 'under_review': return 'info'
      case 'closed': return 'default'
      case 'awarded': return 'success'
      case 'cancelled': return 'error'
      default: return 'default'
    }
  }

  const getRFPTypeLabel = (type: RFPType) => {
    switch (type) {
      case 'rfp': return 'RFP'
      case 'rfq': return 'RFQ'
      case 'itb': return 'ITB'
      case 'rfi': return 'RFI'
      default: return type.toUpperCase()
    }
  }

  const columns = [
    {
      key: 'title' as keyof RFPListItem,
      header: 'Title',
      render: (value: string, item: RFPListItem) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{item.rfp_number}</div>
        </div>
      ),
      width: '30%'
    },
    {
      key: 'rfp_type' as keyof RFPListItem,
      header: 'Type',
      render: (value: RFPType) => (
        <Badge variant="info" size="sm">
          {getRFPTypeLabel(value)}
        </Badge>
      ),
      width: '10%'
    },
    {
      key: 'status' as keyof RFPListItem,
      header: 'Status',
      render: (value: RFPStatus) => (
        <Badge variant={getStatusVariant(value)} size="sm">
          {value.replace('_', ' ').toUpperCase()}
        </Badge>
      ),
      width: '12%'
    },
    {
      key: 'organization' as keyof RFPListItem,
      header: 'Organization',
      render: (value: string) => value || '-',
      width: '20%'
    },
    {
      key: 'estimated_budget' as keyof RFPListItem,
      header: 'Budget',
      render: (value: number, item: RFPListItem) => {
        if (!value) return '-'
        return `${item.currency} ${value.toLocaleString()}`
      },
      width: '15%'
    },
    {
      key: 'created_at' as keyof RFPListItem,
      header: 'Created',
      render: (value: string) => new Date(value).toLocaleDateString(),
      width: '10%'
    },
    {
      key: 'id' as keyof RFPListItem,
      header: 'Actions',
      render: (_: any, item: RFPListItem) => (
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              router.push(`/rfps/${item.id}`)
            }}
            leftIcon={<EyeIcon className="h-4 w-4" />}
          >
            View
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              router.push(`/rfps/${item.id}/edit`)
            }}
            leftIcon={<PencilIcon className="h-4 w-4" />}
          >
            Edit
          </Button>
        </div>
      ),
      width: '13%'
    }
  ]

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, search: e.target.value }))
  }

  const handleStatusFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters(prev => ({ 
      ...prev, 
      status: e.target.value as RFPStatus || undefined 
    }))
  }

  const toggleMyRFPs = () => {
    setFilters(prev => ({ ...prev, my_rfps: !prev.my_rfps }))
  }

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="sm:flex sm:items-center">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">RFPs</h1>
            <p className="mt-2 text-sm text-gray-700">
              Manage your Request for Proposals and track their progress.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
            <Button
              onClick={() => router.push('/rfps/create')}
              leftIcon={<PlusIcon className="h-5 w-5" />}
            >
              Create RFP
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Input
            placeholder="Search RFPs..."
            value={filters.search}
            onChange={handleSearch}
            leftIcon={<MagnifyingGlassIcon className="h-5 w-5" />}
          />
          
          <Select
            placeholder="Filter by status"
            options={statusOptions}
            value={filters.status || ''}
            onChange={handleStatusFilter}
          />

          <div className="flex items-center">
            <input
              type="checkbox"
              id="my-rfps"
              checked={filters.my_rfps}
              onChange={toggleMyRFPs}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="my-rfps" className="ml-2 block text-sm text-gray-900">
              My RFPs only
            </label>
          </div>

          <Button
            variant="outline"
            onClick={() => refetch()}
            className="justify-center"
          >
            Refresh
          </Button>
        </div>

        {/* Table */}
        <div className="mt-8">
          <Table
            data={rfps || []}
            columns={columns}
            loading={isLoading}
            emptyMessage="No RFPs found. Create your first RFP to get started."
            onRowClick={(item) => router.push(`/rfps/${item.id}`)}
          />
        </div>

        {/* Stats */}
        {rfps && rfps.length > 0 && (
          <div className="mt-6 text-sm text-gray-500">
            Showing {rfps.length} RFP{rfps.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

export default RFPsPage