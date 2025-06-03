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
import { proposalService } from '@/services/proposal'
import { ProposalListItem, ProposalStatus, ProposalFilters } from '@/types/proposal'
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  DocumentTextIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline'

const ProposalsPage: React.FC = () => {
  const router = useRouter()
  const [filters, setFilters] = useState<ProposalFilters>({
    search: '',
    status: undefined,
    my_proposals: false,
    order_by: 'created_at',
    order_direction: 'desc'
  })

  // Fetch proposals with filters
  const { data: proposals, isLoading, refetch } = useQuery(
    ['proposals', filters],
    () => proposalService.getProposals(filters),
    {
      staleTime: 30000, // 30 seconds
    }
  )

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'draft', label: 'Draft' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'under_review', label: 'Under Review' },
    { value: 'submitted', label: 'Submitted' },
    { value: 'accepted', label: 'Accepted' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'withdrawn', label: 'Withdrawn' },
  ]

  const getStatusVariant = (status: ProposalStatus) => {
    switch (status) {
      case 'submitted': return 'info'
      case 'draft': return 'warning'
      case 'in_progress': return 'info'
      case 'under_review': return 'info'
      case 'accepted': return 'success'
      case 'rejected': return 'error'
      case 'withdrawn': return 'default'
      default: return 'default'
    }
  }

  const columns = [
    {
      key: 'title' as keyof ProposalListItem,
      header: 'Proposal',
      render: (value: string, item: ProposalListItem) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{item.proposal_number}</div>
        </div>
      ),
      width: '25%'
    },
    {
      key: 'rfp_title' as keyof ProposalListItem,
      header: 'RFP',
      render: (value: string, item: ProposalListItem) => (
        <div>
          <div className="font-medium text-gray-900">{value || 'N/A'}</div>
          <div className="text-sm text-gray-500">{item.rfp_number || ''}</div>
          {item.rfp_organization && (
            <div className="text-xs text-gray-400">{item.rfp_organization}</div>
          )}
        </div>
      ),
      width: '25%'
    },
    {
      key: 'status' as keyof ProposalListItem,
      header: 'Status',
      render: (value: ProposalStatus) => (
        <Badge variant={getStatusVariant(value)} size="sm">
          {value.replace('_', ' ').toUpperCase()}
        </Badge>
      ),
      width: '12%'
    },
    {
      key: 'total_cost' as keyof ProposalListItem,
      header: 'Total Cost',
      render: (value: number, item: ProposalListItem) => {
        if (!value) return '-'
        return (
          <div className="flex items-center">
            <CurrencyDollarIcon className="h-4 w-4 text-gray-400 mr-1" />
            {item.currency} {value.toLocaleString()}
          </div>
        )
      },
      width: '15%'
    },
    {
      key: 'compliance_score' as keyof ProposalListItem,
      header: 'Compliance',
      render: (value: number) => {
        if (!value) return '-'
        return (
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
              <div 
                className="bg-primary-600 h-2 rounded-full" 
                style={{ width: `${value}%` }}
              />
            </div>
            <span className="text-sm text-gray-600">{value}%</span>
          </div>
        )
      },
      width: '15%'
    },
    {
      key: 'created_at' as keyof ProposalListItem,
      header: 'Created',
      render: (value: string) => new Date(value).toLocaleDateString(),
      width: '10%'
    },
    {
      key: 'id' as keyof ProposalListItem,
      header: 'Actions',
      render: (_: any, item: ProposalListItem) => (
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              router.push(`/proposals/${item.id}`)
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
              router.push(`/proposals/${item.id}/edit`)
            }}
            leftIcon={<PencilIcon className="h-4 w-4" />}
          >
            Edit
          </Button>
        </div>
      ),
      width: '15%'
    }
  ]

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, search: e.target.value }))
  }

  const handleStatusFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters(prev => ({ 
      ...prev, 
      status: e.target.value as ProposalStatus || undefined 
    }))
  }

  const toggleMyProposals = () => {
    setFilters(prev => ({ ...prev, my_proposals: !prev.my_proposals }))
  }

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="sm:flex sm:items-center">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">Proposals</h1>
            <p className="mt-2 text-sm text-gray-700">
              Manage proposal responses to RFPs and track submission status.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
            <Button
              onClick={() => router.push('/proposals/create')}
              leftIcon={<PlusIcon className="h-5 w-5" />}
            >
              Create Proposal
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Input
            placeholder="Search proposals..."
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
              id="my-proposals"
              checked={filters.my_proposals}
              onChange={toggleMyProposals}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="my-proposals" className="ml-2 block text-sm text-gray-900">
              My proposals only
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
            data={proposals || []}
            columns={columns}
            loading={isLoading}
            emptyMessage="No proposals found. Create your first proposal to get started."
            onRowClick={(item) => router.push(`/proposals/${item.id}`)}
          />
        </div>

        {/* Stats */}
        {proposals && proposals.length > 0 && (
          <div className="mt-6 text-sm text-gray-500">
            Showing {proposals.length} proposal{proposals.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

export default ProposalsPage