'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ProposalService } from '@/services/proposal'
import { useAuth } from '@/contexts/AuthContext'
import type { Proposal, UpdateProposalData } from '@/types/proposal'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  Save, 
  X, 
  ArrowLeft,
  DollarSign,
  Calendar,
  FileText
} from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function ProposalEditPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const proposalId = parseInt(params.id as string)

  const [formData, setFormData] = useState<UpdateProposalData>({
    title: '',
    executive_summary: '',
    technical_approach: '',
    total_cost: undefined,
    currency: 'USD',
    cost_breakdown: {},
    proposed_timeline: {},
    delivery_date: '',
    compliance_matrix: {}
  })

  const [jsonFields, setJsonFields] = useState({
    cost_breakdown: '',
    proposed_timeline: '',
    compliance_matrix: ''
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch proposal details
  const { data: proposal, isLoading, error } = useQuery({
    queryKey: ['proposal', proposalId],
    queryFn: () => ProposalService.getById(proposalId),
    enabled: !!proposalId
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: UpdateProposalData) => 
      ProposalService.update(proposalId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposal', proposalId] })
      queryClient.invalidateQueries({ queryKey: ['proposals'] })
      toast.success('Proposal updated successfully')
      router.push(`/proposals/${proposalId}`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update proposal')
      
      // Handle validation errors
      if (error.response?.data?.validation_errors) {
        setErrors(error.response.data.validation_errors)
      }
    }
  })

  // Initialize form data when proposal loads
  useEffect(() => {
    if (proposal) {
      setFormData({
        title: proposal.title || '',
        executive_summary: proposal.executive_summary || '',
        technical_approach: proposal.technical_approach || '',
        total_cost: proposal.total_cost || undefined,
        currency: proposal.currency || 'USD',
        cost_breakdown: proposal.cost_breakdown || {},
        proposed_timeline: proposal.proposed_timeline || {},
        delivery_date: proposal.delivery_date || '',
        compliance_matrix: proposal.compliance_matrix || {}
      })

      setJsonFields({
        cost_breakdown: JSON.stringify(proposal.cost_breakdown || {}, null, 2),
        proposed_timeline: JSON.stringify(proposal.proposed_timeline || {}, null, 2),
        compliance_matrix: JSON.stringify(proposal.compliance_matrix || {}, null, 2)
      })
    }
  }, [proposal])

  const handleInputChange = (field: keyof UpdateProposalData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const handleJsonFieldChange = (field: string, value: string) => {
    setJsonFields(prev => ({ ...prev, [field]: value }))
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const validateJsonField = (field: string, value: string) => {
    if (!value.trim()) return {}
    
    try {
      return JSON.parse(value)
    } catch (error) {
      throw new Error(`Invalid JSON format in ${field.replace('_', ' ')}`)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    try {
      // Validate and parse JSON fields
      const parsedData = { ...formData }
      
      if (jsonFields.cost_breakdown.trim()) {
        parsedData.cost_breakdown = validateJsonField('cost_breakdown', jsonFields.cost_breakdown)
      }
      
      if (jsonFields.proposed_timeline.trim()) {
        parsedData.proposed_timeline = validateJsonField('proposed_timeline', jsonFields.proposed_timeline)
      }
      
      if (jsonFields.compliance_matrix.trim()) {
        parsedData.compliance_matrix = validateJsonField('compliance_matrix', jsonFields.compliance_matrix)
      }

      // Remove empty fields
      Object.keys(parsedData).forEach(key => {
        const value = parsedData[key as keyof UpdateProposalData]
        if (value === '' || value === undefined || value === null) {
          delete parsedData[key as keyof UpdateProposalData]
        }
      })

      updateMutation.mutate(parsedData)
    } catch (error: any) {
      toast.error(error.message)
    }
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return ''
    return dateString.split('T')[0] // Convert ISO date to YYYY-MM-DD format
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !proposal) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Proposal Not Found</h1>
          <p className="text-gray-600 mb-4">The requested proposal could not be found.</p>
          <Button onClick={() => router.push('/proposals')}>
            Back to Proposals
          </Button>
        </div>
      </div>
    )
  }

  // Check permissions
  const canEdit = user?.is_superuser || proposal.created_by === user?.id
  
  if (!canEdit) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600 mb-4">You don't have permission to edit this proposal.</p>
          <Button onClick={() => router.push(`/proposals/${proposalId}`)}>
            View Proposal
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Edit Proposal</h1>
              <div className="mt-2 flex items-center space-x-4">
                <span className="text-sm text-gray-500">
                  Proposal #{proposal.proposal_number}
                </span>
                <Badge variant="outline">
                  {proposal.rfp_title}
                </Badge>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <Button
                onClick={() => router.push(`/proposals/${proposalId}`)}
                variant="outline"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Proposal
              </Button>
            </div>
          </div>
        </div>

        {/* Edit Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="title">Proposal Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className={errors.title ? 'border-red-500' : ''}
                  placeholder="Enter proposal title"
                />
                {errors.title && (
                  <p className="text-sm text-red-600 mt-1">{errors.title}</p>
                )}
              </div>

              <div>
                <Label htmlFor="executive_summary">Executive Summary</Label>
                <Textarea
                  id="executive_summary"
                  value={formData.executive_summary}
                  onChange={(e) => handleInputChange('executive_summary', e.target.value)}
                  className={errors.executive_summary ? 'border-red-500' : ''}
                  placeholder="Provide a high-level overview of your proposal"
                  rows={4}
                />
                {errors.executive_summary && (
                  <p className="text-sm text-red-600 mt-1">{errors.executive_summary}</p>
                )}
              </div>

              <div>
                <Label htmlFor="technical_approach">Technical Approach</Label>
                <Textarea
                  id="technical_approach"
                  value={formData.technical_approach}
                  onChange={(e) => handleInputChange('technical_approach', e.target.value)}
                  className={errors.technical_approach ? 'border-red-500' : ''}
                  placeholder="Describe your technical solution and methodology"
                  rows={6}
                />
                {errors.technical_approach && (
                  <p className="text-sm text-red-600 mt-1">{errors.technical_approach}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Financial Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5" />
                <span>Financial Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <Label htmlFor="total_cost">Total Cost</Label>
                  <Input
                    id="total_cost"
                    type="number"
                    step="0.01"
                    value={formData.total_cost || ''}
                    onChange={(e) => handleInputChange('total_cost', e.target.value ? parseFloat(e.target.value) : undefined)}
                    className={errors.total_cost ? 'border-red-500' : ''}
                    placeholder="0.00"
                  />
                  {errors.total_cost && (
                    <p className="text-sm text-red-600 mt-1">{errors.total_cost}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="currency">Currency</Label>
                  <select
                    id="currency"
                    value={formData.currency}
                    onChange={(e) => handleInputChange('currency', e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  >
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                    <option value="CAD">CAD ($)</option>
                    <option value="AUD">AUD ($)</option>
                  </select>
                </div>
              </div>

              <div>
                <Label htmlFor="cost_breakdown">Cost Breakdown (JSON Format)</Label>
                <Textarea
                  id="cost_breakdown"
                  value={jsonFields.cost_breakdown}
                  onChange={(e) => handleJsonFieldChange('cost_breakdown', e.target.value)}
                  className={`font-mono text-sm ${errors.cost_breakdown ? 'border-red-500' : ''}`}
                  placeholder='{\n  "development": 50000,\n  "testing": 15000,\n  "deployment": 10000\n}'
                  rows={6}
                />
                {errors.cost_breakdown && (
                  <p className="text-sm text-red-600 mt-1">{errors.cost_breakdown}</p>
                )}
                <p className="text-sm text-gray-500 mt-1">
                  Provide a detailed breakdown of costs in JSON format
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Timeline Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="h-5 w-5" />
                <span>Timeline Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="delivery_date">Delivery Date</Label>
                <Input
                  id="delivery_date"
                  type="date"
                  value={formatDate(formData.delivery_date || '')}
                  onChange={(e) => handleInputChange('delivery_date', e.target.value)}
                  className={errors.delivery_date ? 'border-red-500' : ''}
                />
                {errors.delivery_date && (
                  <p className="text-sm text-red-600 mt-1">{errors.delivery_date}</p>
                )}
              </div>

              <div>
                <Label htmlFor="proposed_timeline">Proposed Timeline (JSON Format)</Label>
                <Textarea
                  id="proposed_timeline"
                  value={jsonFields.proposed_timeline}
                  onChange={(e) => handleJsonFieldChange('proposed_timeline', e.target.value)}
                  className={`font-mono text-sm ${errors.proposed_timeline ? 'border-red-500' : ''}`}
                  placeholder='{\n  "phase1": "Weeks 1-4: Analysis",\n  "phase2": "Weeks 5-8: Development",\n  "phase3": "Weeks 9-10: Testing"\n}'
                  rows={6}
                />
                {errors.proposed_timeline && (
                  <p className="text-sm text-red-600 mt-1">{errors.proposed_timeline}</p>
                )}
                <p className="text-sm text-gray-500 mt-1">
                  Define project phases and milestones in JSON format
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Compliance Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Compliance Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="compliance_matrix">Compliance Matrix (JSON Format)</Label>
                <Textarea
                  id="compliance_matrix"
                  value={jsonFields.compliance_matrix}
                  onChange={(e) => handleJsonFieldChange('compliance_matrix', e.target.value)}
                  className={`font-mono text-sm ${errors.compliance_matrix ? 'border-red-500' : ''}`}
                  placeholder='{\n  "requirement1": "Fully Compliant",\n  "requirement2": "Partially Compliant",\n  "requirement3": "Not Applicable"\n}'
                  rows={6}
                />
                {errors.compliance_matrix && (
                  <p className="text-sm text-red-600 mt-1">{errors.compliance_matrix}</p>
                )}
                <p className="text-sm text-gray-500 mt-1">
                  Map RFP requirements to compliance status in JSON format
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Form Actions */}
          <div className="flex items-center justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push(`/proposals/${proposalId}`)}
            >
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            
            <Button
              type="submit"
              disabled={updateMutation.isPending}
              className="bg-primary-600 hover:bg-primary-700"
            >
              {updateMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}