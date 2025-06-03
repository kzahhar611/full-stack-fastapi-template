'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from 'react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import Textarea from '@/components/common/Textarea'
import Select from '@/components/common/Select'
import { rfpService } from '@/services/rfp'
import { CreateRFPData, RFPType } from '@/types/rfp'
import { 
  ArrowLeftIcon,
  DocumentTextIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'

const CreateRFPPage: React.FC = () => {
  const router = useRouter()
  const [formData, setFormData] = useState<CreateRFPData>({
    title: '',
    description: '',
    rfp_type: 'rfp' as RFPType,
    estimated_budget: undefined,
    currency: 'USD',
    submission_deadline: '',
    evaluation_period: undefined,
    project_start_date: '',
    project_end_date: '',
    organization: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const createRFPMutation = useMutation(rfpService.createRFP, {
    onSuccess: (data) => {
      toast.success('RFP created successfully!')
      router.push(`/rfps/${data.id}`)
    },
    onError: (error: any) => {
      console.error('Failed to create RFP:', error)
      toast.error('Failed to create RFP. Please try again.')
    }
  })

  const rfpTypeOptions = [
    { value: 'rfp', label: 'Request for Proposal (RFP)' },
    { value: 'rfq', label: 'Request for Quotation (RFQ)' },
    { value: 'itb', label: 'Invitation to Bid (ITB)' },
    { value: 'rfi', label: 'Request for Information (RFI)' },
  ]

  const currencyOptions = [
    { value: 'USD', label: 'USD ($)' },
    { value: 'EUR', label: 'EUR (€)' },
    { value: 'GBP', label: 'GBP (£)' },
    { value: 'CAD', label: 'CAD ($)' },
    { value: 'AUD', label: 'AUD ($)' },
  ]

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'estimated_budget' || name === 'evaluation_period' 
        ? value ? Number(value) : undefined 
        : value
    }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }

    if (!formData.rfp_type) {
      newErrors.rfp_type = 'RFP type is required'
    }

    if (formData.contact_email && !/\S+@\S+\.\S+/.test(formData.contact_email)) {
      newErrors.contact_email = 'Invalid email format'
    }

    if (formData.submission_deadline && formData.project_start_date) {
      const deadline = new Date(formData.submission_deadline)
      const startDate = new Date(formData.project_start_date)
      if (deadline >= startDate) {
        newErrors.project_start_date = 'Project start date must be after submission deadline'
      }
    }

    if (formData.project_start_date && formData.project_end_date) {
      const startDate = new Date(formData.project_start_date)
      const endDate = new Date(formData.project_end_date)
      if (startDate >= endDate) {
        newErrors.project_end_date = 'Project end date must be after start date'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      toast.error('Please fix the errors in the form')
      return
    }

    // Filter out empty values
    const cleanedData = Object.entries(formData).reduce((acc, [key, value]) => {
      if (value !== '' && value !== undefined && value !== null) {
        acc[key] = value
      }
      return acc
    }, {} as any)

    createRFPMutation.mutate(cleanedData)
  }

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
              <h1 className="text-2xl font-semibold text-gray-900">Create New RFP</h1>
              <p className="mt-1 text-sm text-gray-600">
                Fill out the form below to create a new Request for Proposal.
              </p>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-6">
              <DocumentTextIcon className="h-6 w-6 text-primary-600" />
              <h2 className="text-lg font-medium text-gray-900">Basic Information</h2>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <Input
                  label="RFP Title *"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  error={errors.title}
                  placeholder="Enter a descriptive title for your RFP"
                  required
                />
              </div>

              <Select
                label="RFP Type *"
                name="rfp_type"
                options={rfpTypeOptions}
                value={formData.rfp_type}
                onChange={handleInputChange}
                error={errors.rfp_type}
                required
              />

              <div className="flex space-x-4">
                <Input
                  label="Estimated Budget"
                  name="estimated_budget"
                  type="number"
                  value={formData.estimated_budget || ''}
                  onChange={handleInputChange}
                  placeholder="0"
                  min="0"
                  step="0.01"
                />
                <Select
                  label="Currency"
                  name="currency"
                  options={currencyOptions}
                  value={formData.currency}
                  onChange={handleInputChange}
                />
              </div>

              <div className="sm:col-span-2">
                <Textarea
                  label="Description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Provide a detailed description of what you're looking for..."
                  rows={4}
                />
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-6">
              <CalendarIcon className="h-6 w-6 text-primary-600" />
              <h2 className="text-lg font-medium text-gray-900">Timeline</h2>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input
                label="Submission Deadline"
                name="submission_deadline"
                type="datetime-local"
                value={formData.submission_deadline}
                onChange={handleInputChange}
                error={errors.submission_deadline}
              />

              <Input
                label="Evaluation Period (days)"
                name="evaluation_period"
                type="number"
                value={formData.evaluation_period || ''}
                onChange={handleInputChange}
                placeholder="30"
                min="1"
              />

              <Input
                label="Project Start Date"
                name="project_start_date"
                type="date"
                value={formData.project_start_date}
                onChange={handleInputChange}
                error={errors.project_start_date}
              />

              <Input
                label="Project End Date"
                name="project_end_date"
                type="date"
                value={formData.project_end_date}
                onChange={handleInputChange}
                error={errors.project_end_date}
              />
            </div>
          </div>

          {/* Contact Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-6">
              <BuildingOfficeIcon className="h-6 w-6 text-primary-600" />
              <h2 className="text-lg font-medium text-gray-900">Contact Information</h2>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input
                label="Organization"
                name="organization"
                value={formData.organization}
                onChange={handleInputChange}
                placeholder="Your organization name"
              />

              <Input
                label="Contact Person"
                name="contact_person"
                value={formData.contact_person}
                onChange={handleInputChange}
                placeholder="John Smith"
              />

              <Input
                label="Contact Email"
                name="contact_email"
                type="email"
                value={formData.contact_email}
                onChange={handleInputChange}
                error={errors.contact_email}
                placeholder="john@company.com"
              />

              <Input
                label="Contact Phone"
                name="contact_phone"
                type="tel"
                value={formData.contact_phone}
                onChange={handleInputChange}
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              loading={createRFPMutation.isLoading}
              leftIcon={<DocumentTextIcon className="h-5 w-5" />}
            >
              Create RFP
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}

export default CreateRFPPage