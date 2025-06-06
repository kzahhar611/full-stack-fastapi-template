'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { 
  Upload, 
  FileText, 
  Calendar, 
  DollarSign, 
  Building, 
  User,
  CheckCircle,
  AlertCircle,
  Loader2,
  ArrowLeft,
  ArrowRight
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface ProjectFormData {
  name: string
  description: string
  client_name: string
  opportunity_value: string
  submission_deadline: string
}

export default function CreateProposalProject() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    client_name: '',
    opportunity_value: '',
    submission_deadline: ''
  })
  const [rfpFile, setRfpFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleInputChange = (field: keyof ProjectFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError('')
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      const allowedTypes = ['.pdf', '.docx', '.doc', '.txt']
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
      
      if (!allowedTypes.includes(fileExt)) {
        setError(`File type ${fileExt} not supported. Please use: ${allowedTypes.join(', ')}`)
        return
      }
      
      // Validate file size (50MB)
      if (file.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB')
        return
      }
      
      setRfpFile(file)
      setError('')
    }
  }

  const validateStep1 = () => {
    if (!formData.name.trim()) {
      setError('Project name is required')
      return false
    }
    if (!formData.client_name.trim()) {
      setError('Client name is required')
      return false
    }
    return true
  }

  const validateStep2 = () => {
    if (!rfpFile) {
      setError('RFP document is required')
      return false
    }
    return true
  }

  const handleNextStep = () => {
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2)
    } else if (currentStep === 2 && validateStep2()) {
      setCurrentStep(3)
    }
  }

  const handlePreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const createProject = async () => {
    setLoading(true)
    setError('')
    
    try {
      // Create project
      const projectFormData = new FormData()
      projectFormData.append('name', formData.name)
      projectFormData.append('description', formData.description)
      projectFormData.append('client_name', formData.client_name)
      projectFormData.append('opportunity_value', formData.opportunity_value)
      if (formData.submission_deadline) {
        projectFormData.append('submission_deadline', formData.submission_deadline)
      }

      const token = localStorage.getItem('token')
      const projectResponse = await fetch('/api/v1/proposal-generation/projects', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: projectFormData
      })

      if (!projectResponse.ok) {
        throw new Error('Failed to create project')
      }

      const projectData = await projectResponse.json()
      const projectId = projectData.id

      // Upload RFP if provided
      if (rfpFile) {
        const rfpFormData = new FormData()
        rfpFormData.append('file', rfpFile)

        setUploadProgress(25)
        
        const uploadResponse = await fetch(`/api/v1/proposal-generation/projects/${projectId}/upload-rfp`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: rfpFormData
        })

        setUploadProgress(75)

        if (!uploadResponse.ok) {
          throw new Error('Failed to upload RFP')
        }

        setUploadProgress(100)
      }

      setSuccess(`Project "${formData.name}" created successfully! Analysis is starting...`)
      
      // Redirect to project details after 2 seconds
      setTimeout(() => {
        router.push(`/proposal-generation/projects/${projectId}`)
      }, 2000)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    } finally {
      setLoading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const progressPercentage = (currentStep / 3) * 100

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create Proposal Project</h1>
          <p className="text-gray-600 mt-1">AI-powered technical proposal generation</p>
        </div>
        <Link href="/proposal-generation">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Progress Bar */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium">Step {currentStep} of 3</span>
            <span className="text-sm text-gray-500">{Math.round(progressPercentage)}% complete</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span className={currentStep >= 1 ? 'text-blue-600 font-medium' : ''}>Project Details</span>
            <span className={currentStep >= 2 ? 'text-blue-600 font-medium' : ''}>RFP Upload</span>
            <span className={currentStep >= 3 ? 'text-blue-600 font-medium' : ''}>Review & Create</span>
          </div>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Success Alert */}
      {success && (
        <Alert className="mb-6 border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Step 1: Project Details */}
      {currentStep === 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2" />
              Project Details
            </CardTitle>
            <CardDescription>
              Basic information about your proposal project
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">Project Name *</Label>
                <Input
                  id="name"
                  placeholder="e.g., Software Development Proposal"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="client_name">Client Name *</Label>
                <Input
                  id="client_name"
                  placeholder="e.g., ABC Corporation"
                  value={formData.client_name}
                  onChange={(e) => handleInputChange('client_name', e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="opportunity_value">Opportunity Value</Label>
                <Input
                  id="opportunity_value"
                  placeholder="e.g., $250,000"
                  value={formData.opportunity_value}
                  onChange={(e) => handleInputChange('opportunity_value', e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="submission_deadline">Submission Deadline</Label>
                <Input
                  id="submission_deadline"
                  type="datetime-local"
                  value={formData.submission_deadline}
                  onChange={(e) => handleInputChange('submission_deadline', e.target.value)}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">Project Description</Label>
              <Textarea
                id="description"
                placeholder="Describe the project scope, objectives, and key requirements..."
                rows={4}
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
              />
            </div>

            <div className="flex justify-end">
              <Button onClick={handleNextStep}>
                Next Step
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: RFP Upload */}
      {currentStep === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Upload className="w-5 h-5 mr-2" />
              RFP Document Upload
            </CardTitle>
            <CardDescription>
              Upload the RFP document for AI analysis and requirement extraction
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {!rfpFile ? (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Upload RFP Document
                </h3>
                <p className="text-gray-600 mb-4">
                  Select a PDF, Word document, or text file containing the RFP
                </p>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="rfp-upload"
                />
                <Label htmlFor="rfp-upload">
                  <Button asChild>
                    <span>Choose File</span>
                  </Button>
                </Label>
                <p className="text-xs text-gray-500 mt-2">
                  Supported formats: PDF, DOCX, DOC, TXT (max 50MB)
                </p>
              </div>
            ) : (
              <div className="border border-green-200 bg-green-50 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-8 h-8 text-green-600" />
                    <div>
                      <h4 className="font-medium text-green-900">{rfpFile.name}</h4>
                      <p className="text-sm text-green-700">
                        {formatFileSize(rfpFile.size)} • Ready for analysis
                      </p>
                    </div>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setRfpFile(null)}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">What happens next?</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• AI will extract requirements from your RFP document</li>
                <li>• Requirements will be categorized by type and priority</li>
                <li>• Appropriate content templates will be recommended</li>
                <li>• You can then generate proposal sections automatically</li>
              </ul>
            </div>

            <div className="flex justify-between">
              <Button variant="outline" onClick={handlePreviousStep}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>
              <Button onClick={handleNextStep}>
                Next Step
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Review & Create */}
      {currentStep === 3 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CheckCircle className="w-5 h-5 mr-2" />
              Review & Create Project
            </CardTitle>
            <CardDescription>
              Review your project details and create the proposal project
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Project Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Project Information</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Name:</span>
                    <span className="ml-2 font-medium">{formData.name}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Client:</span>
                    <span className="ml-2 font-medium">{formData.client_name}</span>
                  </div>
                  {formData.opportunity_value && (
                    <div>
                      <span className="text-gray-600">Value:</span>
                      <span className="ml-2 font-medium">{formData.opportunity_value}</span>
                    </div>
                  )}
                  {formData.submission_deadline && (
                    <div>
                      <span className="text-gray-600">Deadline:</span>
                      <span className="ml-2 font-medium">
                        {new Date(formData.submission_deadline).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">RFP Document</h4>
                {rfpFile && (
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-blue-600" />
                    <div>
                      <div className="font-medium text-sm">{rfpFile.name}</div>
                      <div className="text-xs text-gray-600">{formatFileSize(rfpFile.size)}</div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {formData.description && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                  {formData.description}
                </p>
              </div>
            )}

            {/* Upload Progress */}
            {loading && uploadProgress > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-blue-900">Creating project...</span>
                  <span className="text-sm text-blue-700">{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="h-2" />
              </div>
            )}

            <div className="flex justify-between">
              <Button variant="outline" onClick={handlePreviousStep} disabled={loading}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>
              <Button onClick={createProject} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating Project...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Create Project
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}