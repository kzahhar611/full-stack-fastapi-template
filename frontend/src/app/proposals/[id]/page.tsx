'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ProposalService } from '@/services/proposal'
import { useAuth } from '@/contexts/AuthContext'
import type { Proposal, ProposalStatus } from '@/types/proposal'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Eye, 
  Edit, 
  Download, 
  Upload, 
  X, 
  Clock, 
  DollarSign, 
  CheckCircle, 
  AlertCircle,
  FileText,
  Calendar,
  Building,
  User,
  TrendingUp
} from 'lucide-react'
import { toast } from 'react-hot-toast'

const getStatusColor = (status: ProposalStatus) => {
  switch (status) {
    case 'draft': return 'bg-gray-100 text-gray-800'
    case 'in_progress': return 'bg-blue-100 text-blue-800'
    case 'under_review': return 'bg-yellow-100 text-yellow-800'
    case 'submitted': return 'bg-green-100 text-green-800'
    case 'accepted': return 'bg-emerald-100 text-emerald-800'
    case 'rejected': return 'bg-red-100 text-red-800'
    case 'withdrawn': return 'bg-gray-100 text-gray-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getStatusIcon = (status: ProposalStatus) => {
  switch (status) {
    case 'draft': return <Edit className="h-4 w-4" />
    case 'in_progress': return <Clock className="h-4 w-4" />
    case 'under_review': return <Eye className="h-4 w-4" />
    case 'submitted': return <CheckCircle className="h-4 w-4" />
    case 'accepted': return <CheckCircle className="h-4 w-4" />
    case 'rejected': return <X className="h-4 w-4" />
    case 'withdrawn': return <X className="h-4 w-4" />
    default: return <AlertCircle className="h-4 w-4" />
  }
}

export default function ProposalDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const proposalId = parseInt(params.id as string)

  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)

  // Fetch proposal details
  const { data: proposal, isLoading, error } = useQuery({
    queryKey: ['proposal', proposalId],
    queryFn: () => ProposalService.getById(proposalId),
    enabled: !!proposalId
  })

  // Status update mutation
  const statusMutation = useMutation({
    mutationFn: ({ status }: { status: ProposalStatus }) => 
      ProposalService.updateStatus(proposalId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposal', proposalId] })
      toast.success('Proposal status updated successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update status')
    }
  })

  // Document upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => ProposalService.uploadDocument(proposalId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposal', proposalId] })
      toast.success('Document uploaded successfully')
      setUploadFile(null)
      setUploadDialogOpen(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload document')
    }
  })

  // Document delete mutation
  const deleteMutation = useMutation({
    mutationFn: (documentId: number) => 
      ProposalService.deleteDocument(proposalId, documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposal', proposalId] })
      toast.success('Document deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete document')
    }
  })

  // Evaluation mutation
  const evaluationMutation = useMutation({
    mutationFn: () => ProposalService.evaluate(proposalId, {
      evaluate_technical: true,
      evaluate_financial: true,
      evaluate_compliance: true
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposal', proposalId] })
      toast.success('Proposal evaluation completed')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to evaluate proposal')
    }
  })

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

  const canEdit = user?.is_superuser || proposal.created_by === user?.id
  const canChangeStatus = canEdit && ['draft', 'in_progress'].includes(proposal.status)

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD'
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const handleFileUpload = () => {
    if (uploadFile) {
      uploadMutation.mutate(uploadFile)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{proposal.title}</h1>
              <div className="mt-2 flex items-center space-x-4">
                <span className="text-sm text-gray-500">
                  Proposal #{proposal.proposal_number}
                </span>
                <Badge className={`${getStatusColor(proposal.status)} inline-flex items-center space-x-1`}>
                  {getStatusIcon(proposal.status)}
                  <span className="capitalize">{proposal.status.replace('_', ' ')}</span>
                </Badge>
                {proposal.compliance_score && (
                  <Badge variant="outline" className="inline-flex items-center space-x-1">
                    <TrendingUp className="h-3 w-3" />
                    <span>{proposal.compliance_score}% Compliance</span>
                  </Badge>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {canChangeStatus && (
                <select
                  value={proposal.status}
                  onChange={(e) => statusMutation.mutate({ status: e.target.value as ProposalStatus })}
                  className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  disabled={statusMutation.isPending}
                >
                  <option value="draft">Draft</option>
                  <option value="in_progress">In Progress</option>
                  <option value="submitted">Submitted</option>
                </select>
              )}

              {canEdit && (
                <Button
                  onClick={() => router.push(`/proposals/${proposalId}/edit`)}
                  variant="outline"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              )}

              {(user?.is_superuser || proposal.status === 'submitted') && (
                <Button
                  onClick={() => evaluationMutation.mutate()}
                  disabled={evaluationMutation.isPending}
                  variant="outline"
                >
                  <TrendingUp className="h-4 w-4 mr-2" />
                  {evaluationMutation.isPending ? 'Evaluating...' : 'Evaluate'}
                </Button>
              )}

              <Button
                onClick={() => router.push('/proposals')}
                variant="outline"
              >
                Back to Proposals
              </Button>
            </div>
          </div>
        </div>

        {/* RFP Information */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Building className="h-5 w-5" />
              <span>Related RFP</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">RFP Title</label>
                <p className="mt-1 text-sm text-gray-900">{proposal.rfp_title}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">RFP Number</label>
                <p className="mt-1 text-sm text-gray-900">{proposal.rfp_number}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Organization</label>
                <p className="mt-1 text-sm text-gray-900">{proposal.rfp_organization}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          {proposal.total_cost && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center">
                  <div className="p-2 rounded-md bg-green-100">
                    <DollarSign className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Cost</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(proposal.total_cost, proposal.currency)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {proposal.delivery_date && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center">
                  <div className="p-2 rounded-md bg-blue-100">
                    <Calendar className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Delivery Date</p>
                    <p className="text-lg font-bold text-gray-900">
                      {formatDate(proposal.delivery_date)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 rounded-md bg-purple-100">
                  <User className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Created</p>
                  <p className="text-lg font-bold text-gray-900">
                    {formatDate(proposal.created_at)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 rounded-md bg-orange-100">
                  <FileText className="h-6 w-6 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Documents</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {proposal.documents?.length || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="details" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="evaluation">Evaluation</TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
          </TabsList>

          {/* Details Tab */}
          <TabsContent value="details" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Executive Summary */}
              {proposal.executive_summary && (
                <Card>
                  <CardHeader>
                    <CardTitle>Executive Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {proposal.executive_summary}
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Technical Approach */}
              {proposal.technical_approach && (
                <Card>
                  <CardHeader>
                    <CardTitle>Technical Approach</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {proposal.technical_approach}
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Cost Breakdown */}
              {proposal.cost_breakdown && (
                <Card>
                  <CardHeader>
                    <CardTitle>Cost Breakdown</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-sm text-gray-700 bg-gray-50 p-4 rounded-md overflow-auto">
                      {JSON.stringify(proposal.cost_breakdown, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
              )}

              {/* Compliance Matrix */}
              {proposal.compliance_matrix && (
                <Card>
                  <CardHeader>
                    <CardTitle>Compliance Matrix</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-sm text-gray-700 bg-gray-50 p-4 rounded-md overflow-auto">
                      {JSON.stringify(proposal.compliance_matrix, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Proposal Documents</CardTitle>
                  {canEdit && (
                    <Button 
                      onClick={() => setUploadDialogOpen(true)}
                      size="sm"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Document
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {proposal.documents && proposal.documents.length > 0 ? (
                  <div className="space-y-3">
                    {proposal.documents.map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-gray-500" />
                          <div>
                            <p className="font-medium text-gray-900">{doc.original_filename}</p>
                            <p className="text-sm text-gray-500">
                              {(doc.file_size / 1024 / 1024).toFixed(2)} MB • {doc.content_type}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => {
                              const downloadUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/proposals/${proposalId}/documents/${doc.id}/download`
                              const token = localStorage.getItem('access_token')
                              
                              // Create a temporary anchor element to download the file
                              const link = document.createElement('a')
                              link.href = downloadUrl
                              link.setAttribute('download', doc.original_filename)
                              
                              // Add authorization header if token exists
                              if (token) {
                                fetch(downloadUrl, {
                                  headers: {
                                    'Authorization': `Bearer ${token}`
                                  }
                                })
                                .then(response => response.blob())
                                .then(blob => {
                                  const url = window.URL.createObjectURL(blob)
                                  link.href = url
                                  document.body.appendChild(link)
                                  link.click()
                                  document.body.removeChild(link)
                                  window.URL.revokeObjectURL(url)
                                })
                                .catch(() => {
                                  toast.error('Failed to download file')
                                })
                              } else {
                                toast.error('Authentication required')
                              }
                            }}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </Button>
                          {canEdit && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => deleteMutation.mutate(doc.id)}
                              disabled={deleteMutation.isPending}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No documents uploaded yet.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Evaluation Tab */}
          <TabsContent value="evaluation" className="space-y-6">
            {proposal.evaluation_results || proposal.strengths || proposal.weaknesses ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Strengths */}
                {proposal.strengths && proposal.strengths.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-green-700">Strengths</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {proposal.strengths.map((strength, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Weaknesses */}
                {proposal.weaknesses && proposal.weaknesses.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-red-700">Areas for Improvement</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {proposal.weaknesses.map((weakness, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{weakness}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Risk Factors */}
                {proposal.risk_factors && proposal.risk_factors.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-yellow-700">Risk Factors</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {proposal.risk_factors.map((risk, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{risk}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Recommendation */}
                {proposal.recommendation && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Recommendation</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 whitespace-pre-wrap">
                        {proposal.recommendation}
                      </p>
                    </CardContent>
                  </Card>
                )}

                {/* Evaluation Results */}
                {proposal.evaluation_results && (
                  <Card className="lg:col-span-2">
                    <CardHeader>
                      <CardTitle>Detailed Evaluation Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <pre className="text-sm text-gray-700 bg-gray-50 p-4 rounded-md overflow-auto">
                        {JSON.stringify(proposal.evaluation_results, null, 2)}
                      </pre>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">No evaluation results available yet.</p>
                  {(user?.is_superuser || proposal.status === 'submitted') && (
                    <Button
                      onClick={() => evaluationMutation.mutate()}
                      disabled={evaluationMutation.isPending}
                    >
                      <TrendingUp className="h-4 w-4 mr-2" />
                      {evaluationMutation.isPending ? 'Evaluating...' : 'Run Evaluation'}
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Timeline Tab */}
          <TabsContent value="timeline" className="space-y-6">
            {proposal.proposed_timeline ? (
              <Card>
                <CardHeader>
                  <CardTitle>Proposed Timeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-sm text-gray-700 bg-gray-50 p-4 rounded-md overflow-auto">
                    {JSON.stringify(proposal.proposed_timeline, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No timeline information available.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        {/* Upload Dialog */}
        {uploadDialogOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Upload Document</CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setUploadDialogOpen(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select File
                  </label>
                  <input
                    type="file"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => setUploadDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleFileUpload}
                    disabled={!uploadFile || uploadMutation.isPending}
                  >
                    {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}