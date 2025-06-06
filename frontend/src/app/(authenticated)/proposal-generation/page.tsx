'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  FileText, 
  Plus, 
  Zap, 
  Target, 
  BarChart3, 
  Clock,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Database
} from 'lucide-react'
import Link from 'next/link'

// Module 3 Phase 3.1 Foundation Dashboard
export default function ProposalGenerationDashboard() {
  const [phaseStatus, setPhaseStatus] = useState<any>(null)
  const [statistics, setStatistics] = useState<any>(null)
  const [contentTypes, setContentTypes] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Fetch phase status
      const phaseResponse = await fetch('/api/v1/proposal-generation/phase-status')
      const phaseData = await phaseResponse.json()
      setPhaseStatus(phaseData)

      // Fetch statistics
      const statsResponse = await fetch('/api/v1/proposal-generation/statistics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStatistics(statsData)
      }

      // Fetch content types
      const typesResponse = await fetch('/api/v1/proposal-generation/content-types')
      const typesData = await typesResponse.json()
      setContentTypes(typesData.content_types || [])

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Proposal Generation</h1>
          <p className="text-gray-600 mt-1">AI-Powered Technical Proposal Generation System</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" size="sm">
            <FileText className="w-4 h-4 mr-2" />
            Templates
          </Button>
          <Button size="sm">
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </Button>
        </div>
      </div>

      {/* Phase Status Banner */}
      {phaseStatus && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Zap className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-blue-900">
                    Module 3: {phaseStatus.current_phase}
                  </CardTitle>
                  <CardDescription className="text-blue-700">
                    {phaseStatus.phase_description}
                  </CardDescription>
                </div>
              </div>
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                {phaseStatus.estimated_completion?.phase_3_1} Complete
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Completed Tasks */}
              <div>
                <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Completed Tasks
                </h4>
                <div className="space-y-2">
                  {phaseStatus.completed_tasks?.map((task: string, index: number) => (
                    <div key={index} className="flex items-center text-sm text-blue-800">
                      <span>{task}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Next Phase Tasks */}
              <div>
                <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  Next Phase Tasks
                </h4>
                <div className="space-y-2">
                  {phaseStatus.next_phase_tasks?.map((task: string, index: number) => (
                    <div key={index} className="flex items-center text-sm text-blue-700">
                      <span>{task}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-4">
              <div className="flex justify-between text-sm text-blue-700 mb-2">
                <span>Overall Module 3 Progress</span>
                <span>{phaseStatus.estimated_completion?.overall_module_3}</span>
              </div>
              <Progress value={25} className="h-2" />
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="content-types">Content Types</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="infrastructure">Infrastructure</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Projects</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics?.total_projects || 0}</div>
                <p className="text-xs text-muted-foreground">
                  Phase 3.1 Foundation
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Templates</CardTitle>
                <Lightbulb className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics?.total_templates || 0}</div>
                <p className="text-xs text-muted-foreground">
                  Ready to use
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Database Tables</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics?.database_tables_created || 0}</div>
                <p className="text-xs text-muted-foreground">
                  Schema created
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">API Endpoints</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics?.api_endpoints_implemented || 0}</div>
                <p className="text-xs text-muted-foreground">
                  Foundation ready
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Available actions for Phase 3.1 Foundation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
                  <Plus className="w-6 h-6" />
                  <span>Create Project</span>
                  <span className="text-xs text-muted-foreground">Phase 3.2</span>
                </Button>
                
                <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
                  <FileText className="w-6 h-6" />
                  <span>Browse Templates</span>
                  <span className="text-xs text-green-600">Available</span>
                </Button>
                
                <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
                  <BarChart3 className="w-6 h-6" />
                  <span>View Statistics</span>
                  <span className="text-xs text-green-600">Available</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Content Types Tab */}
        <TabsContent value="content-types" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Supported Content Types</CardTitle>
              <CardDescription>
                Types of proposal content that can be generated
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {contentTypes.map((type, index) => (
                  <Card key={index} className="border border-gray-200">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">{type.label}</CardTitle>
                        <Badge variant="outline" className="text-xs">
                          {type.typical_word_count}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <p className="text-sm text-gray-600">{type.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Content Templates</CardTitle>
              <CardDescription>
                Pre-built templates for proposal generation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Template Management
                </h3>
                <p className="text-gray-600 mb-4">
                  Template browsing and management will be implemented in Phase 3.2
                </p>
                <div className="flex justify-center gap-3">
                  <Button variant="outline" disabled>
                    <FileText className="w-4 h-4 mr-2" />
                    Browse Templates
                  </Button>
                  <Button variant="outline" disabled>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Template
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Infrastructure Tab */}
        <TabsContent value="infrastructure" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Database Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  Database Infrastructure
                </CardTitle>
              </CardHeader>
              <CardContent>
                {phaseStatus?.database_status && (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm">Tables Created</span>
                      <Badge variant="outline">{phaseStatus.database_status.tables_created}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Sample Templates</span>
                      <Badge variant="outline">{phaseStatus.database_status.sample_templates}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Indexes Created</span>
                      <Badge variant="outline">{phaseStatus.database_status.indexes_created}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Status</span>
                      <Badge className="bg-green-100 text-green-800">
                        {phaseStatus.database_status.status}
                      </Badge>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Development Roadmap */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  Development Roadmap
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <div>
                      <div className="font-medium text-sm">Phase 3.1 - Foundation</div>
                      <div className="text-xs text-gray-600">Database & API structure</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <div>
                      <div className="font-medium text-sm">Phase 3.2 - Core AI Engine</div>
                      <div className="text-xs text-gray-600">RFP analysis & content generation</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                    <div>
                      <div className="font-medium text-sm">Phase 3.3 - Content Management</div>
                      <div className="text-xs text-gray-600">Template system & editing tools</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                    <div>
                      <div className="font-medium text-sm">Phase 3.4 - Proposal Assembly</div>
                      <div className="text-xs text-gray-600">Document generation & export</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}