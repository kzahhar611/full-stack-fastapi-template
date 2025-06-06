'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { 
  ArrowLeft,
  FileText, 
  Target,
  Zap,
  BarChart3,
  CheckCircle,
  AlertCircle,
  Clock,
  Filter,
  Search,
  Loader2,
  Lightbulb
} from 'lucide-react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'

interface Requirement {
  id: number
  uuid: string
  requirement_text: string
  requirement_type: string
  section_title?: string
  page_number?: number
  priority_level: string
  complexity_score: number
  word_count_estimate: number
  assigned_content_type?: string
  response_status: string
  estimated_effort_hours: number
  extraction_confidence: number
  keywords: string[]
  clarity_score: number
  measurability_score: number
  created_at: string
}

interface Project {
  id: number
  name: string
  client_name: string
  status: string
  progress_percentage: number
  total_requirements: number
  completed_sections: number
  ai_analysis_completed: boolean
  requirements_extracted: boolean
}

export default function RequirementsManagement() {
  const params = useParams()
  const router = useRouter()
  const projectId = parseInt(params.projectId as string)
  
  const [project, setProject] = useState<Project | null>(null)
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [filteredRequirements, setFilteredRequirements] = useState<Requirement[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterPriority, setFilterPriority] = useState('all')
  const [generating, setGenerating] = useState(false)
  const [generationStatus, setGenerationStatus] = useState('')

  useEffect(() => {
    fetchProjectAndRequirements()
  }, [projectId])

  useEffect(() => {
    filterRequirements()
  }, [requirements, searchTerm, filterType, filterPriority])

  const fetchProjectAndRequirements = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      
      // Fetch project details
      const projectResponse = await fetch(`/api/v1/proposal-generation/projects/${projectId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (projectResponse.ok) {
        const projectData = await projectResponse.json()
        setProject(projectData)
      }
      
      // Fetch requirements
      const requirementsResponse = await fetch(`/api/v1/proposal-generation/projects/${projectId}/requirements`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (requirementsResponse.ok) {
        const requirementsData = await requirementsResponse.json()
        setRequirements(requirementsData.requirements || [])
      } else {
        setError('Failed to load requirements')
      }
      
    } catch (err) {
      setError('Failed to load project data')
    } finally {
      setLoading(false)
    }
  }

  const filterRequirements = () => {
    let filtered = [...requirements]
    
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(req => 
        req.requirement_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
        req.section_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        req.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }
    
    // Type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(req => req.requirement_type === filterType)
    }
    
    // Priority filter
    if (filterPriority !== 'all') {
      filtered = filtered.filter(req => req.priority_level.toLowerCase() === filterPriority)
    }
    
    setFilteredRequirements(filtered)
  }

  const generateContent = async (contentType: string, requirementIds: number[] = []) => {
    try {
      setGenerating(true)
      setGenerationStatus(`Generating ${contentType.replace('_', ' ')} content...`)
      
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.append('content_type', contentType)
      if (requirementIds.length > 0) {
        formData.append('requirement_ids', requirementIds.join(','))
      }
      
      const response = await fetch(`/api/v1/proposal-generation/projects/${projectId}/generate-content`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })
      
      if (response.ok) {
        setGenerationStatus('Content generation started successfully!')
        setTimeout(() => {
          setGenerationStatus('')
          // Refresh project data
          fetchProjectAndRequirements()
        }, 2000)
      } else {
        throw new Error('Failed to start content generation')
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate content')
      setGenerationStatus('')
    } finally {
      setGenerating(false)
    }
  }

  const getRequirementTypeColor = (type: string) => {
    const colors = {
      technical: 'bg-blue-100 text-blue-800',
      functional: 'bg-green-100 text-green-800',
      commercial: 'bg-purple-100 text-purple-800',
      compliance: 'bg-orange-100 text-orange-800',
      management: 'bg-cyan-100 text-cyan-800',
      delivery: 'bg-pink-100 text-pink-800'
    }
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getPriorityColor = (priority: string) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[priority?.toLowerCase() as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600'
    if (confidence >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const requirementsByType = filteredRequirements.reduce((acc, req) => {
    const type = req.requirement_type
    if (!acc[type]) acc[type] = []
    acc[type].push(req)
    return acc
  }, {} as Record<string, Requirement[]>)

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/proposal-generation">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Requirements Management</h1>
            {project && (
              <p className="text-gray-600 mt-1">
                {project.name} • {project.client_name}
              </p>
            )}
          </div>
        </div>
        <Button onClick={() => router.push(`/proposal-generation/generate/${projectId}`)}>
          <Zap className="w-4 h-4 mr-2" />
          Generate Content
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Generation Status */}
      {generationStatus && (
        <Alert className="border-blue-200 bg-blue-50">
          <CheckCircle className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">{generationStatus}</AlertDescription>
        </Alert>
      )}

      {/* Project Status */}
      {project && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Project Status</span>
              <Badge variant={project.status === 'completed' ? 'default' : 'secondary'}>
                {project.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{project.total_requirements}</div>
                <div className="text-sm text-gray-600">Requirements</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{project.completed_sections}</div>
                <div className="text-sm text-gray-600">Sections Generated</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{project.progress_percentage}%</div>
                <div className="text-sm text-gray-600">Progress</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center space-x-2">
                  {project.ai_analysis_completed ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : (
                    <Clock className="w-6 h-6 text-yellow-600" />
                  )}
                  <span className="text-sm font-medium">
                    {project.ai_analysis_completed ? 'Analysis Complete' : 'Analyzing...'}
                  </span>
                </div>
              </div>
            </div>
            <div className="mt-4">
              <Progress value={project.progress_percentage} className="h-2" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filter Requirements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="search"
                  placeholder="Search requirements..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="type">Type</Label>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="technical">Technical</SelectItem>
                  <SelectItem value="functional">Functional</SelectItem>
                  <SelectItem value="commercial">Commercial</SelectItem>
                  <SelectItem value="compliance">Compliance</SelectItem>
                  <SelectItem value="management">Management</SelectItem>
                  <SelectItem value="delivery">Delivery</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <Select value={filterPriority} onValueChange={setFilterPriority}>
                <SelectTrigger>
                  <SelectValue placeholder="All priorities" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priorities</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>&nbsp;</Label>
              <Button variant="outline" onClick={filterRequirements} className="w-full">
                <Filter className="w-4 h-4 mr-2" />
                Apply Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Requirements Display */}
      <Tabs defaultValue="by-type" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="by-type">By Type</TabsTrigger>
          <TabsTrigger value="list">All Requirements</TabsTrigger>
        </TabsList>

        {/* By Type View */}
        <TabsContent value="by-type" className="space-y-6">
          {Object.keys(requirementsByType).length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Requirements Found</h3>
                <p className="text-gray-600">
                  No requirements match your current filters or the project analysis is still in progress.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(requirementsByType).map(([type, reqs]) => (
                <Card key={type}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="capitalize">{type.replace('_', ' ')} Requirements</span>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{reqs.length}</Badge>
                        <Button 
                          size="sm" 
                          onClick={() => generateContent(`${type}_approach`, reqs.map(r => r.id))}
                          disabled={generating}
                        >
                          {generating ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <Lightbulb className="w-3 h-3" />
                          )}
                        </Button>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {reqs.slice(0, 3).map((req) => (
                        <div key={req.id} className="border border-gray-200 rounded-lg p-3">
                          <div className="flex items-start justify-between mb-2">
                            <Badge className={getRequirementTypeColor(req.requirement_type)}>
                              {req.requirement_type}
                            </Badge>
                            <div className="flex items-center space-x-2">
                              <Badge className={getPriorityColor(req.priority_level)}>
                                {req.priority_level}
                              </Badge>
                              <span className={`text-xs font-medium ${getConfidenceColor(req.extraction_confidence)}`}>
                                {req.extraction_confidence}%
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">
                            {req.requirement_text.length > 150 
                              ? `${req.requirement_text.substring(0, 150)}...`
                              : req.requirement_text
                            }
                          </p>
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>{req.section_title}</span>
                            <span>{req.word_count_estimate} words est.</span>
                          </div>
                        </div>
                      ))}
                      {reqs.length > 3 && (
                        <div className="text-center">
                          <Button variant="link" size="sm">
                            View {reqs.length - 3} more requirements
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* List View */}
        <TabsContent value="list" className="space-y-4">
          {filteredRequirements.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Requirements Found</h3>
                <p className="text-gray-600">
                  Try adjusting your filters or wait for the RFP analysis to complete.
                </p>
              </CardContent>
            </Card>
          ) : (
            filteredRequirements.map((req) => (
              <Card key={req.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Badge className={getRequirementTypeColor(req.requirement_type)}>
                        {req.requirement_type}
                      </Badge>
                      <Badge className={getPriorityColor(req.priority_level)}>
                        {req.priority_level}
                      </Badge>
                      <span className="text-sm text-gray-500">
                        Complexity: {req.complexity_score}/10
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`text-sm font-medium ${getConfidenceColor(req.extraction_confidence)}`}>
                        {req.extraction_confidence}% confidence
                      </span>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => generateContent('technical_approach', [req.id])}
                        disabled={generating}
                      >
                        Generate Content
                      </Button>
                    </div>
                  </div>
                  <p className="text-gray-800 mb-3">{req.requirement_text}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{req.section_title} {req.page_number && `(Page ${req.page_number})`}</span>
                    <span>{req.word_count_estimate} words • {req.estimated_effort_hours}h estimated</span>
                  </div>
                  {req.keywords.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {req.keywords.slice(0, 5).map((keyword, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}