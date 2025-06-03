'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import Textarea from '@/components/common/Textarea'
import Select from '@/components/common/Select'
import { proposalService } from '@/services/proposal'
import { rfpService } from '@/services/rfp'
import { CreateProposalData } from '@/types/proposal'
import { 
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface ProposalFormData {
  rfp_id: string
  title: string
  executive_summary: string
  technical_approach: string
  total_cost: string
  currency: string
  delivery_date: string
  cost_breakdown: string
  proposed_timeline: string
  compliance_matrix: string
}

const CreateProposalPage: React.FC = () => {
  const router = useRouter()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState<ProposalFormData>({
    rfp_id: '',
    title: '',
    executive_summary: '',
    technical_approach: '',
    total_cost: '',
    currency: 'USD',
    delivery_date: '',
    cost_breakdown: '',
    proposed_timeline: '',
    compliance_matrix: ''
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch published RFPs for selection
  const { data: rfps } = useQuery(
    ['rfps', { status: 'published' }],
    () => rfpService.getRFPs({ status: 'published' }),
    {
      staleTime: 60000, // 1 minute
    }
  )

  // Create mutation
  const createMutation = useMutation(
    (data: CreateProposalData) => proposalService.createProposal(data),
    {
      onSuccess: (proposal) => {
        toast.success('Proposal created successfully!')
        queryClient.invalidateQueries(['proposals'])
        router.push(`/proposals/${proposal.id}`)
      },
      onError: (error: any) => {
        console.error('Create failed:', error)
        toast.error('Failed to create proposal')
        if (error.response?.data?.detail) {
          // Handle validation errors
          if (Array.isArray(error.response.data.detail)) {
            const fieldErrors: Record<string, string> = {}
            error.response.data.detail.forEach((err: any) => {
              if (err.loc && err.loc.length > 1) {
                fieldErrors[err.loc[1]] = err.msg
              }
            })
            setErrors(fieldErrors)
          }
        }
      }
    }
  )

  const handleInputChange = (field: keyof ProposalFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.rfp_id) {
      newErrors.rfp_id = 'Please select an RFP'
    }

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }

    if (!formData.executive_summary.trim()) {
      newErrors.executive_summary = 'Executive summary is required'
    }

    if (formData.total_cost && isNaN(parseFloat(formData.total_cost))) {
      newErrors.total_cost = 'Please enter a valid cost amount'
    }

    // Validate JSON fields
    const jsonFields = ['cost_breakdown', 'proposed_timeline', 'compliance_matrix']
    jsonFields.forEach(field => {
      const value = formData[field as keyof ProposalFormData]
      if (value.trim()) {
        try {
          JSON.parse(value)
        } catch (e) {
          newErrors[field] = 'Please enter valid JSON format'
        }
      }
    })

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      toast.error('Please fix the errors before submitting')
      return
    }

    // Prepare data
    const createData: CreateProposalData = {
      rfp_id: parseInt(formData.rfp_id),
      title: formData.title,
      executive_summary: formData.executive_summary || undefined,
      technical_approach: formData.technical_approach || undefined,
      total_cost: formData.total_cost ? parseFloat(formData.total_cost) : undefined,
      currency: formData.currency,
      delivery_date: formData.delivery_date || undefined,
      cost_breakdown: formData.cost_breakdown ? JSON.parse(formData.cost_breakdown) : undefined,
      proposed_timeline: formData.proposed_timeline ? JSON.parse(formData.proposed_timeline) : undefined,
      compliance_matrix: formData.compliance_matrix ? JSON.parse(formData.compliance_matrix) : undefined
    }

    createMutation.mutate(createData)
  }

  const rfpOptions = rfps?.map(rfp => ({
    value: rfp.id.toString(),
    label: `${rfp.title} (${rfp.rfp_number})`
  })) || []

  const currencyOptions = [
    { value: 'USD', label: 'US Dollar (USD)' },
    { value: 'EUR', label: 'Euro (EUR)' },
    { value: 'GBP', label: 'British Pound (GBP)' },
    { value: 'CAD', label: 'Canadian Dollar (CAD)' },
    { value: 'AUD', label: 'Australian Dollar (AUD)' },
  ]

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={() => router.back()}
              leftIcon={<ArrowLeftIcon className="h-5 w-5" />}
            >
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Create Proposal</h1>
              <p className="mt-1 text-sm text-gray-600">
                Create a new proposal in response to an RFP.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">Basic Information</h2>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <Select
                  label="Select RFP *"
                  options={[
                    { value: '', label: 'Choose an RFP to respond to' },
                    ...rfpOptions
                  ]}
                  value={formData.rfp_id}
                  onChange={(e) => handleInputChange('rfp_id', e.target.value)}
                  error={errors.rfp_id}
                />
              </div>

              <div className="sm:col-span-2">
                <Input
                  label="Proposal Title *"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  error={errors.title}
                  placeholder="Enter proposal title"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Total Cost"
                  type="number"
                  value={formData.total_cost}
                  onChange={(e) => handleInputChange('total_cost', e.target.value)}
                  error={errors.total_cost}
                  placeholder="0.00"
                />
                <Select
                  label="Currency"
                  options={currencyOptions}
                  value={formData.currency}
                  onChange={(e) => handleInputChange('currency', e.target.value)}
                />
              </div>

              <Input
                label="Delivery Date"
                type="date"
                value={formData.delivery_date}
                onChange={(e) => handleInputChange('delivery_date', e.target.value)}
                error={errors.delivery_date}
              />
            </div>
          </div>

          {/* Proposal Content */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">Proposal Content</h2>
            
            <div className="space-y-6">
              <Textarea
                label="Executive Summary *"
                value={formData.executive_summary}
                onChange={(e) => handleInputChange('executive_summary', e.target.value)}
                error={errors.executive_summary}
                placeholder="Provide a high-level overview of your proposal"
                rows={4}
              />

              <Textarea
                label="Technical Approach"
                value={formData.technical_approach}
                onChange={(e) => handleInputChange('technical_approach', e.target.value)}
                error={errors.technical_approach}
                placeholder="Describe your technical approach and methodology"
                rows={6}
              />
            </div>
          </div>

          {/* Detailed Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">Detailed Information</h2>
            
            <div className="space-y-6">
              <Textarea
                label="Cost Breakdown (JSON format)"
                value={formData.cost_breakdown}
                onChange={(e) => handleInputChange('cost_breakdown', e.target.value)}
                error={errors.cost_breakdown}
                placeholder='{"labor": 30000, "materials": 10000, "overhead": 5000}'
                rows={4}
                helpText="Enter cost breakdown in JSON format"
              />

              <Textarea
                label="Proposed Timeline (JSON format)"
                value={formData.proposed_timeline}
                onChange={(e) => handleInputChange('proposed_timeline', e.target.value)}
                error={errors.proposed_timeline}
                placeholder='{"phase1": "4 weeks", "phase2": "6 weeks", "testing": "2 weeks"}'
                rows={4}
                helpText="Enter timeline breakdown in JSON format"
              />

              <Textarea
                label="Compliance Matrix (JSON format)"
                value={formData.compliance_matrix}
                onChange={(e) => handleInputChange('compliance_matrix', e.target.value)}
                error={errors.compliance_matrix}
                placeholder='{"ISO9001": "Certified", "SOC2": "Type II Compliant"}'
                rows={4}
                helpText="Enter compliance requirements in JSON format"
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-4 pb-8">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              leftIcon={<XMarkIcon className="h-5 w-5" />}
            >
              Cancel
            </Button>
            
            <Button
              type="submit"
              loading={createMutation.isLoading}
              leftIcon={<CheckIcon className="h-5 w-5" />}
            >
              Create Proposal
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}

export default CreateProposalPage