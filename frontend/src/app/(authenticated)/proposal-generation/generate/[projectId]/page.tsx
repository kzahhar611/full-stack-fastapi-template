'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { 
  ArrowLeft,
  Zap, 
  FileText,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  Eye,
  Edit,
  Download,
  BarChart3,
  Target,
  Star
} from 'lucide-react'
import Link from 'next/link'
import { useParams } from 'next/navigation'

interface GeneratedSection {
  id: number
  uuid: string
  section_title: string
  content_type: string
  section_order: number
  generated_content: string
  word_count: number
  estimated_reading_time: number
  generation_status: string
  ai_confidence_score: number
  content_quality_score: number
  relevance_score: number
  completeness_score: number
  human_reviewed: boolean
  human_approved: boolean
  created_at: string
  updated_at: string
}

interface Project {
  id: number
  name: string
  client_name: string
  status: string
  progress_percentage: number
  total_requirements: number
  completed_sections: number
}

const contentTypes = [
  { value: 'executive_summary', label: 'Executive Summary', description: 'High-level project overview and value proposition', order: 1 },
  { value: 'technical_approach', label: 'Technical Approach', description: 'Detailed technical solution and methodology', order: 2 },
  { value: 'methodology', label: 'Methodology', description: 'Project execution methodology and processes', order: 3 },
  { value: 'team_qualifications', label: 'Team Qualifications', description: 'Team expertise and relevant experience', order: 4 },
  { value: 'project_timeline', label: 'Project Timeline', description: 'Detailed project schedule and milestones', order: 5 },
  { value: 'risk_management', label: 'Risk Management', description: 'Risk identification and mitigation strategies', order: 6 },
  { value: 'quality_assurance', label: 'Quality Assurance', description: 'Quality control processes and standards', order: 7 },
  { value: 'deliverables', label: 'Deliverables', description: 'Project deliverables and acceptance criteria', order: 8 }
]

export default function ContentGeneration() {
  const params = useParams()
  const projectId = parseInt(params.projectId as string)
  
  const [project, setProject] = useState<Project | null>(null)
  const [generatedSections, setGeneratedSections] = useState<GeneratedSection[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedContentType, setSelectedContentType] = useState('')
  const [previewSection, setPreviewSection] = useState<GeneratedSection | null>(null)
  const [editingSection, setEditingSection] = useState<GeneratedSection | null>(null)
  const [editContent, setEditContent] = useState('')

  useEffect(() => {
    fetchProjectData()
    fetchGeneratedSections()
  }, [projectId])

  const fetchProjectData = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/proposal-generation/projects/${projectId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setProject(data)
      }
    } catch (err) {
      setError('Failed to load project data')
    }
  }

  const fetchGeneratedSections = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/proposal-generation/projects/${projectId}/generated-sections`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setGeneratedSections(data.sections || [])
      }
    } catch (err) {
      setError('Failed to load generated sections')
    } finally {
      setLoading(false)
    }
  }

  const generateContent = async () => {
    if (!selectedContentType) {
      setError('Please select a content type')
      return
    }

    try {
      setGenerating(true)
      setError('')
      
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.append('content_type', selectedContentType)
      
      const response = await fetch(`/api/v1/proposal-generation/projects/${projectId}/generate-content`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })
      
      if (response.ok) {
        setSuccess('Content generation started successfully!')
        setSelectedContentType('')
        
        // Refresh sections after a delay
        setTimeout(() => {
          fetchGeneratedSections()
          fetchProjectData()
          setSuccess('')
        }, 3000)
      } else {
        throw new Error('Failed to start content generation')
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate content')
    } finally {
      setGenerating(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors = {
      completed: 'bg-green-100 text-green-800',
      in_progress: 'bg-blue-100 text-blue-800',
      pending: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
      needs_review: 'bg-orange-100 text-orange-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getQualityColor = (score: number) => {
    if (score >= 85) return 'text-green-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getContentTypeInfo = (contentType: string) => {
    return contentTypes.find(ct => ct.value === contentType) || { label: contentType, description: '', order: 99 }
  }

  const getGeneratedContentTypes = () => {
    return new Set(generatedSections.map(s => s.content_type))
  }

  const getAvailableContentTypes = () => {
    const generated = getGeneratedContentTypes()
    return contentTypes.filter(ct => !generated.has(ct.value))
  }

  const startEdit = (section: GeneratedSection) => {
    setEditingSection(section)
    setEditContent(section.generated_content)
  }

  const saveEdit = async () => {
    // In a real implementation, this would call an API to update the section
    if (editingSection) {
      const updatedSections = generatedSections.map(s => 
        s.id === editingSection.id 
          ? { ...s, generated_content: editContent, updated_at: new Date().toISOString() }
          : s
      )
      setGeneratedSections(updatedSections)
      setEditingSection(null)
      setEditContent('')
      setSuccess('Section updated successfully!')
      setTimeout(() => setSuccess(''), 2000)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const sortedSections = [...generatedSections].sort((a, b) => {
    const aInfo = getContentTypeInfo(a.content_type)
    const bInfo = getContentTypeInfo(b.content_type)
    return aInfo.order - bInfo.order
  })

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href={`/proposal-generation/requirements/${projectId}`}>
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Requirements
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Content Generation</h1>
            {project && (
              <p className="text-gray-600 mt-1">
                {project.name} • {project.client_name}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Project Progress */}
      {project && (
        <Card>
          <CardHeader>
            <CardTitle>Project Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{generatedSections.length}</div>
                <div className="text-sm text-gray-600">Sections Generated</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{project.progress_percentage}%</div>
                <div className="text-sm text-gray-600">Complete</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {generatedSections.reduce((acc, s) => acc + s.word_count, 0)}
                </div>
                <div className="text-sm text-gray-600">Total Words</div>
              </div>
            </div>
            <Progress value={project.progress_percentage} className="h-2" />
          </CardContent>
        </Card>
      )}

      {/* Content Generation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="w-5 h-5 mr-2" />
            Generate New Content
          </CardTitle>
          <CardDescription>
            Select a content type to generate AI-powered proposal sections
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <Select value={selectedContentType} onValueChange={setSelectedContentType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select content type to generate" />
                </SelectTrigger>
                <SelectContent>
                  {getAvailableContentTypes().map((contentType) => (
                    <SelectItem key={contentType.value} value={contentType.value}>
                      <div>
                        <div className="font-medium">{contentType.label}</div>
                        <div className="text-sm text-gray-500">{contentType.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button 
              onClick={generateContent} 
              disabled={generating || !selectedContentType}
              className="w-full"
            >
              {generating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Generate Content
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Generated Sections */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Generated Sections</h2>
          {generatedSections.length > 0 && (
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export Proposal
            </Button>
          )}
        </div>

        {generatedSections.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Content Generated Yet</h3>
              <p className="text-gray-600 mb-4">
                Start by generating your first proposal section using the form above.
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {contentTypes.slice(0, 3).map((ct) => (
                  <Button
                    key={ct.value}
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedContentType(ct.value)
                      generateContent()
                    }}
                  >
                    Generate {ct.label}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {sortedSections.map((section) => {
              const contentTypeInfo = getContentTypeInfo(section.content_type)
              return (
                <Card key={section.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center space-x-2">
                          <span>{contentTypeInfo.label}</span>
                          <Badge className={getStatusColor(section.generation_status)}>
                            {section.generation_status.replace('_', ' ')}
                          </Badge>
                        </CardTitle>
                        <CardDescription className="mt-1">
                          {section.word_count} words • {section.estimated_reading_time} min read • 
                          Created {new Date(section.created_at).toLocaleDateString()}
                        </CardDescription>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setPreviewSection(section)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => startEdit(section)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {/* Quality Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="text-center">
                        <div className={`text-lg font-bold ${getQualityColor(section.ai_confidence_score)}`}>
                          {section.ai_confidence_score}%
                        </div>
                        <div className="text-xs text-gray-600">AI Confidence</div>
                      </div>
                      <div className="text-center">
                        <div className={`text-lg font-bold ${getQualityColor(section.content_quality_score)}`}>
                          {section.content_quality_score}%
                        </div>
                        <div className="text-xs text-gray-600">Quality</div>
                      </div>
                      <div className="text-center">
                        <div className={`text-lg font-bold ${getQualityColor(section.relevance_score)}`}>
                          {section.relevance_score}%
                        </div>
                        <div className="text-xs text-gray-600">Relevance</div>
                      </div>
                      <div className="text-center">
                        <div className={`text-lg font-bold ${getQualityColor(section.completeness_score)}`}>
                          {section.completeness_score}%
                        </div>
                        <div className="text-xs text-gray-600">Completeness</div>
                      </div>
                    </div>

                    {/* Content Preview */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-gray-700">
                        {section.generated_content.length > 300
                          ? `${section.generated_content.substring(0, 300)}...`
                          : section.generated_content
                        }
                      </p>
                    </div>

                    {/* Status Indicators */}
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center space-x-4">
                        {section.human_reviewed && (
                          <div className="flex items-center text-sm text-blue-600">
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Reviewed
                          </div>
                        )}
                        {section.human_approved && (
                          <div className="flex items-center text-sm text-green-600">
                            <Star className="w-4 h-4 mr-1" />
                            Approved
                          </div>
                        )}
                      </div>
                      <div className="text-sm text-gray-500">
                        Last updated {new Date(section.updated_at).toLocaleDateString()}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>

      {/* Preview Modal */}
      {previewSection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">{getContentTypeInfo(previewSection.content_type).label}</h3>
                <Button variant="outline" onClick={() => setPreviewSection(null)}>
                  Close
                </Button>
              </div>
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap text-gray-800">
                  {previewSection.generated_content}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editingSection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-[80vh] w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">Edit {getContentTypeInfo(editingSection.content_type).label}</h3>
                <div className="flex space-x-2">
                  <Button onClick={saveEdit}>Save Changes</Button>
                  <Button variant="outline" onClick={() => setEditingSection(null)}>
                    Cancel
                  </Button>
                </div>
              </div>
              <Textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="min-h-[400px] font-mono text-sm"
                placeholder="Edit section content..."
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}