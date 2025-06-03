'use client'

import React, { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import Textarea from '@/components/common/Textarea'
import Select from '@/components/common/Select'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { rfpService } from '@/services/rfp'
import { RFPType, RFPStatus } from '@/types/rfp'
import { 
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface RFPFormData {
  title: string
  description: string
  rfp_type: RFPType
  estimated_budget: string
  currency: string
  organization: string
  contact_person: string
  contact_email: string
  contact_phone: string
  submission_deadline: string
  evaluation_period: string
  project_start_date: string
  project_end_date: string
  technical_requirements: string
  evaluation_criteria: string
  compliance_requirements: string
}

const RFPEditPage: React.FC = () => {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const rfpId = parseInt(params.id as string)

  const [formData, setFormData] = useState<RFPFormData>({
    title: '',
    description: '',
    rfp_type: 'rfp',
    estimated_budget: '',
    currency: 'USD',
    organization: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    submission_deadline: '',
    evaluation_period: '',
    project_start_date: '',
    project_end_date: '',
    technical_requirements: '',
    evaluation_criteria: '',
    compliance_requirements: ''
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch RFP details
  const { data: rfp, isLoading, error } = useQuery(
    ['rfp', rfpId],
    () => rfpService.getRFP(rfpId),
    {
      enabled: !!rfpId,
    }
  )

  // Update mutation
  const updateMutation = useMutation(
    (data: Partial<RFPFormData>) => rfpService.updateRFP(rfpId, {
      ...data,
      estimated_budget: data.estimated_budget ? parseFloat(data.estimated_budget) : undefined,
      evaluation_period: data.evaluation_period ? parseInt(data.evaluation_period) : undefined,
      technical_requirements: data.technical_requirements ? JSON.parse(data.technical_requirements) : undefined,
      evaluation_criteria: data.evaluation_criteria ? JSON.parse(data.evaluation_criteria) : undefined,
      compliance_requirements: data.compliance_requirements ? JSON.parse(data.compliance_requirements) : undefined
    }),
    {
      onSuccess: () => {
        toast.success('RFP updated successfully!')
        queryClient.invalidateQueries(['rfp', rfpId])
        queryClient.invalidateQueries(['rfps'])
        router.push(`/rfps/${rfpId}`)
      },
      onError: (error: any) => {
        console.error('Update failed:', error)
        toast.error('Failed to update RFP')
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

  // Populate form when RFP data is loaded
  useEffect(() => {
    if (rfp) {
      setFormData({
        title: rfp.title || '',
        description: rfp.description || '',
        rfp_type: rfp.rfp_type || 'rfp',
        estimated_budget: rfp.estimated_budget ? rfp.estimated_budget.toString() : '',
        currency: rfp.currency || 'USD',
        organization: rfp.organization || '',
        contact_person: rfp.contact_person || '',
        contact_email: rfp.contact_email || '',
        contact_phone: rfp.contact_phone || '',
        submission_deadline: rfp.submission_deadline ? 
          new Date(rfp.submission_deadline).toISOString().slice(0, 16) : '',
        evaluation_period: rfp.evaluation_period ? rfp.evaluation_period.toString() : '',
        project_start_date: rfp.project_start_date ? 
          new Date(rfp.project_start_date).toISOString().slice(0, 10) : '',
        project_end_date: rfp.project_end_date ? 
          new Date(rfp.project_end_date).toISOString().slice(0, 10) : '',
        technical_requirements: rfp.technical_requirements ? 
          JSON.stringify(rfp.technical_requirements, null, 2) : '',
        evaluation_criteria: rfp.evaluation_criteria ? 
          JSON.stringify(rfp.evaluation_criteria, null, 2) : '',
        compliance_requirements: rfp.compliance_requirements ? 
          JSON.stringify(rfp.compliance_requirements, null, 2) : ''
      })
    }
  }, [rfp])

  const handleInputChange = (field: keyof RFPFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required'
    }

    if (formData.estimated_budget && isNaN(parseFloat(formData.estimated_budget))) {
      newErrors.estimated_budget = 'Please enter a valid budget amount'
    }

    if (formData.evaluation_period && isNaN(parseInt(formData.evaluation_period))) {
      newErrors.evaluation_period = 'Please enter a valid number of days'
    }

    if (formData.contact_email && !/\S+@\S+\.\S+/.test(formData.contact_email)) {
      newErrors.contact_email = 'Please enter a valid email address'
    }

    // Validate JSON fields
    const jsonFields = ['technical_requirements', 'evaluation_criteria', 'compliance_requirements']
    jsonFields.forEach(field => {
      const value = formData[field as keyof RFPFormData]
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

    // Filter out empty fields
    const updateData = Object.entries(formData).reduce((acc, [key, value]) => {
      if (value && value.toString().trim()) {
        acc[key as keyof RFPFormData] = value
      }
      return acc
    }, {} as Partial<RFPFormData>)

    updateMutation.mutate(updateData)
  }

  const rfpTypeOptions = [
    { value: 'rfp', label: 'Request for Proposal (RFP)' },
    { value: 'rfq', label: 'Request for Quotation (RFQ)' },
    { value: 'itb', label: 'Invitation to Bid (ITB)' },
    { value: 'rfi', label: 'Request for Information (RFI)' },
  ]

  const currencyOptions = [
    { value: 'USD', label: 'US Dollar (USD)' },
    { value: 'EUR', label: 'Euro (EUR)' },
    { value: 'GBP', label: 'British Pound (GBP)' },
    { value: 'CAD', label: 'Canadian Dollar (CAD)' },
    { value: 'AUD', label: 'Australian Dollar (AUD)' },
  ]

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
          <p className="mt-2 text-gray-600">The RFP you're trying to edit doesn't exist or you don't have permission to edit it.</p>
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
      <div className="px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
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
                <h1 className="text-2xl font-semibold text-gray-900">Edit RFP</h1>
                <p className="mt-1 text-sm text-gray-600">{rfp.rfp_number}</p>
              </div>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">Basic Information</h2>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <Input
                  label="Title *"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  error={errors.title}
                  placeholder="Enter RFP title"
                />
              </div>

              <Select
                label="RFP Type *"
                options={rfpTypeOptions}
                value={formData.rfp_type}
                onChange={(e) => handleInputChange('rfp_type', e.target.value as RFPType)}
                error={errors.rfp_type}
              />

              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Estimated Budget"
                  type="number"
                  value={formData.estimated_budget}
                  onChange={(e) => handleInputChange('estimated_budget', e.target.value)}
                  error={errors.estimated_budget}
                  placeholder="0.00"
                />
                <Select
                  label="Currency"
                  options={currencyOptions}
                  value={formData.currency}
                  onChange={(e) => handleInputChange('currency', e.target.value)}
                />
              </div>

              <div className="sm:col-span-2">
                <Textarea
                  label="Description *"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  error={errors.description}
                  placeholder="Describe the project requirements and objectives"
                  rows={4}
                />
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">Timeline</h2>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input
                label="Submission Deadline"
                type="datetime-local"
                value={formData.submission_deadline}
                onChange={(e) => handleInputChange('submission_deadline', e.target.value)}
                error={errors.submission_deadline}
              />

              <Input
                label="Evaluation Period (days)"
                type="number"
                value={formData.evaluation_period}
                onChange={(e) => handleInputChange('evaluation_period', e.target.value)}
                error={errors.evaluation_period}
                placeholder="30"
              />

              <Input
                label="Project Start Date"
                type="date"
                value={formData.project_start_date}
                onChange={(e) => handleInputChange('project_start_date', e.target.value)}
                error={errors.project_start_date}
              />

              <Input
                label="Project End Date"
                type="date"
                value={formData.project_end_date}
                onChange={(e) => handleInputChange('project_end_date', e.target.value)}
                error={errors.project_end_date}
              />
            </div>
          </div>

          {/* Contact Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">Contact Information</h2>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input
                label="Organization"
                value={formData.organization}
                onChange={(e) => handleInputChange('organization', e.target.value)}
                error={errors.organization}
                placeholder="Organization name"
              />

              <Input
                label="Contact Person"
                value={formData.contact_person}
                onChange={(e) => handleInputChange('contact_person', e.target.value)}
                error={errors.contact_person}
                placeholder="Contact person name"
              />

              <Input
                label="Contact Email"
                type="email"
                value={formData.contact_email}
                onChange={(e) => handleInputChange('contact_email', e.target.value)}
                error={errors.contact_email}
                placeholder="contact@organization.com"
              />

              <Input
                label="Contact Phone"
                type="tel"
                value={formData.contact_phone}
                onChange={(e) => handleInputChange('contact_phone', e.target.value)}
                error={errors.contact_phone}
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>

          {/* Requirements & Criteria */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">Requirements & Evaluation</h2>
            
            <div className="space-y-6">
              <Textarea
                label="Technical Requirements (JSON format)"
                value={formData.technical_requirements}
                onChange={(e) => handleInputChange('technical_requirements', e.target.value)}
                error={errors.technical_requirements}
                placeholder='{"requirements": ["Requirement 1", "Requirement 2"]}'
                rows={4}
                helpText="Enter technical requirements in JSON format"
              />

              <Textarea
                label="Evaluation Criteria (JSON format)"
                value={formData.evaluation_criteria}
                onChange={(e) => handleInputChange('evaluation_criteria', e.target.value)}
                error={errors.evaluation_criteria}
                placeholder='{"criteria": [{"name": "Technical Capability", "weight": 40}, {"name": "Price", "weight": 30}]}'
                rows={4}
                helpText="Enter evaluation criteria in JSON format"
              />

              <Textarea
                label="Compliance Requirements (JSON format)"
                value={formData.compliance_requirements}
                onChange={(e) => handleInputChange('compliance_requirements', e.target.value)}
                error={errors.compliance_requirements}
                placeholder='{"compliance": ["ISO 9001", "SOC 2 Type II"]}'
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
              loading={updateMutation.isLoading}
              leftIcon={<CheckIcon className="h-5 w-5" />}
            >
              Save Changes
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}

export default RFPEditPage