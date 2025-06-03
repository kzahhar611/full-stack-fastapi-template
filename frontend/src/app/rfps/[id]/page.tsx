'use client'

import React, { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Button from '@/components/common/Button'
import Badge from '@/components/common/Badge'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { rfpService } from '@/services/rfp'
import { RFPStatus } from '@/types/rfp'
import { 
  ArrowLeftIcon,
  PencilIcon,
  DocumentArrowUpIcon,
  SparklesIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  EnvelopeIcon,
  PhoneIcon,
  TrashIcon
} from '@heroicons/react/24/outline'

const RFPDetailPage: React.FC = () => {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const rfpId = parseInt(params.id as string)

  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // Fetch RFP details
  const { data: rfp, isLoading, error } = useQuery(
    ['rfp', rfpId],
    () => rfpService.getRFP(rfpId),
    {
      enabled: !!rfpId,
    }
  )

  // Status update mutation
  const statusMutation = useMutation(
    ({ status }: { status: RFPStatus }) => rfpService.updateRFPStatus(rfpId, status),
    {
      onSuccess: () => {
        toast.success('RFP status updated successfully!')
        queryClient.invalidateQueries(['rfp', rfpId])
        queryClient.invalidateQueries(['rfps'])
      },
      onError: () => {
        toast.error('Failed to update RFP status')
      }
    }
  )

  // Analysis mutation
  const analysisMutation = useMutation(
    () => rfpService.analyzeRFP(rfpId, {
      analyze_complexity: true,
      analyze_risks: true,
      generate_recommendations: true
    }),
    {
      onSuccess: (data) => {
        toast.success('RFP analysis completed!')
        queryClient.invalidateQueries(['rfp', rfpId])
        // Show analysis results (could open a modal or navigate to analysis page)
        console.log('Analysis results:', data)
      },
      onError: () => {
        toast.error('Failed to analyze RFP')
      }
    }
  )

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

  const handleStatusChange = (status: RFPStatus) => {
    statusMutation.mutate({ status })
  }

  const handleAnalyze = () => {
    setIsAnalyzing(true)
    analysisMutation.mutate()
    setTimeout(() => setIsAnalyzing(false), 3000) // Reset after animation
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    )
  }

  if (error || !rfp) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-semibold text-gray-900">RFP Not Found</h2>
          <p className="mt-2 text-gray-600">The RFP you're looking for doesn't exist or you don't have permission to view it.</p>
          <Button
            className="mt-4"
            onClick={() => router.push('/rfps')}
            leftIcon={<ArrowLeftIcon className="h-5 w-5" />}
          >
            Back to RFPs
          </Button>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => router.back()}
                leftIcon={<ArrowLeftIcon className="h-5 w-5" />}
              >
                Back
              </Button>
              <div>
                <div className="flex items-center space-x-3">
                  <h1 className="text-2xl font-semibold text-gray-900">{rfp.title}</h1>
                  <Badge variant={getStatusVariant(rfp.status)}>
                    {rfp.status.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
                <p className="mt-1 text-sm text-gray-600">{rfp.rfp_number}</p>
              </div>
            </div>

            <div className="flex space-x-3">
              <Button
                variant="outline"
                onClick={() => router.push(`/rfps/${rfpId}/documents`)}
                leftIcon={<DocumentArrowUpIcon className="h-5 w-5" />}
              >
                Documents
              </Button>
              
              <Button
                variant="outline"
                onClick={handleAnalyze}
                loading={isAnalyzing || analysisMutation.isLoading}
                leftIcon={<SparklesIcon className="h-5 w-5" />}
              >
                Analyze with AI
              </Button>

              <Button
                onClick={() => router.push(`/rfps/${rfpId}/edit`)}
                leftIcon={<PencilIcon className="h-5 w-5" />}
              >
                Edit
              </Button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        {rfp.status === 'draft' && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-blue-800">Ready to publish?</h3>
                <p className="text-sm text-blue-600">Once published, vendors will be able to view and respond to this RFP.</p>
              </div>
              <Button
                onClick={() => handleStatusChange('published')}
                loading={statusMutation.isLoading}
                size="sm"
              >
                Publish RFP
              </Button>
            </div>
          </div>
        )}

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Description</h2>
              <div className="prose max-w-none">
                {rfp.description ? (
                  <p className="text-gray-700 whitespace-pre-wrap">{rfp.description}</p>
                ) : (
                  <p className="text-gray-500 italic">No description provided</p>
                )}
              </div>
            </div>

            {/* Technical Requirements */}
            {rfp.technical_requirements && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Technical Requirements</h2>
                <pre className="bg-gray-50 p-4 rounded-md text-sm text-gray-700 overflow-x-auto">
                  {JSON.stringify(rfp.technical_requirements, null, 2)}
                </pre>
              </div>
            )}

            {/* Evaluation Criteria */}
            {rfp.evaluation_criteria && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Evaluation Criteria</h2>
                <pre className="bg-gray-50 p-4 rounded-md text-sm text-gray-700 overflow-x-auto">
                  {JSON.stringify(rfp.evaluation_criteria, null, 2)}
                </pre>
              </div>
            )}

            {/* AI Analysis */}
            {rfp.ai_analysis_summary && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  <SparklesIcon className="h-5 w-5 text-primary-600 mr-2" />
                  AI Analysis
                </h2>
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-900">Summary</h3>
                    <p className="text-gray-700 mt-1">{rfp.ai_analysis_summary}</p>
                  </div>
                  
                  {rfp.complexity_score && (
                    <div>
                      <h3 className="font-medium text-gray-900">Complexity Score</h3>
                      <div className="flex items-center mt-1">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{ width: `${(rfp.complexity_score / 10) * 100}%` }}
                          />
                        </div>
                        <span className="ml-2 text-sm text-gray-600">{rfp.complexity_score}/10</span>
                      </div>
                    </div>
                  )}

                  {rfp.go_no_go_recommendation && (
                    <div>
                      <h3 className="font-medium text-gray-900">Recommendation</h3>
                      <Badge 
                        variant={rfp.go_no_go_recommendation === 'GO' ? 'success' : 'warning'}
                        className="mt-1"
                      >
                        {rfp.go_no_go_recommendation}
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Key Information */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Key Information</h2>
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">{rfp.rfp_type.toUpperCase()}</dd>
                </div>
                
                {rfp.estimated_budget && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                      Budget
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {rfp.currency} {rfp.estimated_budget.toLocaleString()}
                    </dd>
                  </div>
                )}

                <div>
                  <dt className="text-sm font-medium text-gray-500 flex items-center">
                    <CalendarIcon className="h-4 w-4 mr-1" />
                    Created
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(rfp.created_at).toLocaleDateString()}
                  </dd>
                </div>

                {rfp.submission_deadline && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Submission Deadline</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {new Date(rfp.submission_deadline).toLocaleString()}
                    </dd>
                  </div>
                )}

                {rfp.evaluation_period && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Evaluation Period</dt>
                    <dd className="mt-1 text-sm text-gray-900">{rfp.evaluation_period} days</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Contact Information */}
            {(rfp.organization || rfp.contact_person || rfp.contact_email || rfp.contact_phone) && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  <BuildingOfficeIcon className="h-5 w-5 mr-2" />
                  Contact Information
                </h2>
                <dl className="space-y-3">
                  {rfp.organization && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Organization</dt>
                      <dd className="mt-1 text-sm text-gray-900">{rfp.organization}</dd>
                    </div>
                  )}
                  
                  {rfp.contact_person && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Contact Person</dt>
                      <dd className="mt-1 text-sm text-gray-900">{rfp.contact_person}</dd>
                    </div>
                  )}

                  {rfp.contact_email && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500 flex items-center">
                        <EnvelopeIcon className="h-4 w-4 mr-1" />
                        Email
                      </dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        <a href={`mailto:${rfp.contact_email}`} className="text-primary-600 hover:text-primary-700">
                          {rfp.contact_email}
                        </a>
                      </dd>
                    </div>
                  )}

                  {rfp.contact_phone && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500 flex items-center">
                        <PhoneIcon className="h-4 w-4 mr-1" />
                        Phone
                      </dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        <a href={`tel:${rfp.contact_phone}`} className="text-primary-600 hover:text-primary-700">
                          {rfp.contact_phone}
                        </a>
                      </dd>
                    </div>
                  )}
                </dl>
              </div>
            )}

            {/* Status Actions */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Actions</h2>
              <div className="space-y-3">
                {rfp.status === 'draft' && (
                  <Button
                    variant="outline"
                    fullWidth
                    onClick={() => handleStatusChange('published')}
                    loading={statusMutation.isLoading}
                  >
                    Publish RFP
                  </Button>
                )}
                
                {rfp.status === 'published' && (
                  <Button
                    variant="outline"
                    fullWidth
                    onClick={() => handleStatusChange('closed')}
                    loading={statusMutation.isLoading}
                  >
                    Close RFP
                  </Button>
                )}

                <Button
                  variant="outline"
                  fullWidth
                  onClick={() => router.push(`/rfps/${rfpId}/edit`)}
                  leftIcon={<PencilIcon className="h-4 w-4" />}
                >
                  Edit RFP
                </Button>

                <Button
                  variant="outline"
                  fullWidth
                  onClick={() => router.push(`/rfps/${rfpId}/documents`)}
                  leftIcon={<DocumentArrowUpIcon className="h-4 w-4" />}
                >
                  Manage Documents
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default RFPDetailPage