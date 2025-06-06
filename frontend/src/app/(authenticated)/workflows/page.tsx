"use client"

import { useState, useCallback } from 'react'
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Node,
  Edge,
  Connection,
  BackgroundVariant,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { 
  Plus, 
  Save, 
  Play, 
  Square, 
  Download, 
  Upload,
  Zap,
  FileText,
  Bot,
  Database,
  Settings
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// Initial nodes for the workflow
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'input',
    position: { x: 250, y: 25 },
    data: { 
      label: 'RFP Document Input',
      type: 'input',
      description: 'Upload or connect RFP document source'
    },
    style: {
      background: '#3b82f6',
      color: 'white',
      border: '1px solid #1e40af',
      borderRadius: '8px',
    },
  },
  {
    id: '2',
    position: { x: 100, y: 125 },
    data: { 
      label: 'Document Parser',
      type: 'processor',
      description: 'Extract text and structure from documents'
    },
    style: {
      background: '#8b5cf6',
      color: 'white',
      border: '1px solid #7c3aed',
      borderRadius: '8px',
    },
  },
  {
    id: '3',
    position: { x: 400, y: 125 },
    data: { 
      label: 'AI Analyzer',
      type: 'ai',
      description: 'GPT-4 powered RFP analysis'
    },
    style: {
      background: '#10b981',
      color: 'white', 
      border: '1px solid #059669',
      borderRadius: '8px',
    },
  },
  {
    id: '4',
    position: { x: 250, y: 225 },
    data: { 
      label: 'Compliance Checker',
      type: 'validator',
      description: 'Validate against compliance requirements'
    },
    style: {
      background: '#f59e0b',
      color: 'white',
      border: '1px solid #d97706',
      borderRadius: '8px',
    },
  },
  {
    id: '5',
    position: { x: 100, y: 325 },
    data: { 
      label: 'Risk Assessment',
      type: 'analyzer',
      description: 'Identify potential risks and issues'
    },
    style: {
      background: '#ef4444',
      color: 'white',
      border: '1px solid #dc2626',
      borderRadius: '8px',
    },
  },
  {
    id: '6',
    position: { x: 400, y: 325 },
    data: { 
      label: 'Proposal Generator',
      type: 'generator',
      description: 'Generate proposal draft based on analysis'
    },
    style: {
      background: '#6366f1',
      color: 'white',
      border: '1px solid #4f46e5',
      borderRadius: '8px',
    },
  },
  {
    id: '7',
    type: 'output',
    position: { x: 250, y: 425 },
    data: { 
      label: 'Final Report',
      type: 'output',
      description: 'Compiled analysis and proposal output'
    },
    style: {
      background: '#1f2937',
      color: 'white',
      border: '1px solid #374151',
      borderRadius: '8px',
    },
  },
]

// Initial edges connecting the nodes
const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', type: 'smoothstep' },
  { id: 'e1-3', source: '1', target: '3', type: 'smoothstep' },
  { id: 'e2-4', source: '2', target: '4', type: 'smoothstep' },
  { id: 'e3-4', source: '3', target: '4', type: 'smoothstep' },
  { id: 'e4-5', source: '4', target: '5', type: 'smoothstep' },
  { id: 'e4-6', source: '4', target: '6', type: 'smoothstep' },
  { id: 'e5-7', source: '5', target: '7', type: 'smoothstep' },
  { id: 'e6-7', source: '6', target: '7', type: 'smoothstep' },
]

// Workflow templates
const workflowTemplates = [
  {
    id: 'rfp-analysis',
    name: 'RFP Analysis Workflow',
    description: 'Complete RFP analysis with compliance checking and risk assessment',
    nodes: 7,
    category: 'Analysis',
    badge: 'Popular'
  },
  {
    id: 'proposal-generation',
    name: 'Proposal Generator',
    description: 'AI-powered proposal generation with quality assurance',
    nodes: 5,
    category: 'Generation',
    badge: 'New'
  },
  {
    id: 'compliance-audit',
    name: 'Compliance Audit',
    description: 'Comprehensive compliance checking across multiple standards',
    nodes: 6,
    category: 'Validation',
    badge: null
  },
  {
    id: 'market-research',
    name: 'Market Intelligence',
    description: 'Automated market research and competitive analysis',
    nodes: 8,
    category: 'Research',
    badge: 'Beta'
  }
]

export default function WorkflowsPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [isRunning, setIsRunning] = useState(false)
  const [showTemplates, setShowTemplates] = useState(false)

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const handleRunWorkflow = () => {
    setIsRunning(true)
    // Simulate workflow execution
    setTimeout(() => {
      setIsRunning(false)
    }, 3000)
  }

  const handleSaveWorkflow = () => {
    const workflow = {
      nodes,
      edges,
      name: 'Custom RFP Workflow',
      createdAt: new Date().toISOString()
    }
    console.log('Saving workflow:', workflow)
    // Here you would save to your backend
  }

  return (
    <div className="h-full flex flex-col space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Designer</h1>
          <p className="text-muted-foreground">
            Design and execute AI-powered workflows for RFP processing
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => setShowTemplates(!showTemplates)}>
            <FileText className="mr-2 h-4 w-4" />
            Templates
          </Button>
          <Button variant="outline" onClick={handleSaveWorkflow}>
            <Save className="mr-2 h-4 w-4" />
            Save
          </Button>
          <Button 
            onClick={handleRunWorkflow}
            disabled={isRunning}
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
          >
            {isRunning ? (
              <>
                <Square className="mr-2 h-4 w-4" />
                Running...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Run Workflow
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Templates Panel */}
      {showTemplates && (
        <Card>
          <CardHeader>
            <CardTitle>Workflow Templates</CardTitle>
            <CardDescription>
              Start with pre-built templates or create your own from scratch
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {workflowTemplates.map((template) => (
                <Card key={template.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm">{template.name}</CardTitle>
                      {template.badge && (
                        <Badge variant={template.badge === 'Popular' ? 'default' : 'secondary'}>
                          {template.badge}
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="text-xs">
                      {template.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{template.nodes} nodes</span>
                      <span>{template.category}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Workflow Canvas */}
      <Card className="flex-1 min-h-[600px]">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">RFP Analysis Workflow</CardTitle>
            <div className="flex items-center space-x-2">
              <Badge variant="outline">
                <Zap className="mr-1 h-3 w-3" />
                {nodes.length} nodes
              </Badge>
              <Badge variant="outline">
                <Settings className="mr-1 h-3 w-3" />
                {edges.length} connections
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0 h-full">
          <div className="h-[500px] bg-gray-50 dark:bg-gray-900 rounded-lg overflow-hidden">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              fitView
              attributionPosition="bottom-left"
              className="bg-teal-50 dark:bg-gray-900"
            >
              <Controls className="bg-white dark:bg-gray-800 border rounded-lg" />
              <MiniMap 
                className="bg-white dark:bg-gray-800 border rounded-lg"
                nodeColor={(node) => {
                  switch (node.data.type) {
                    case 'input': return '#3b82f6'
                    case 'processor': return '#8b5cf6'
                    case 'ai': return '#10b981'
                    case 'validator': return '#f59e0b'
                    case 'analyzer': return '#ef4444'
                    case 'generator': return '#6366f1'
                    case 'output': return '#1f2937'
                    default: return '#6b7280'
                  }
                }}
              />
              <Background 
                variant={BackgroundVariant.Dots} 
                gap={20}
                size={1}
                className="bg-white dark:bg-gray-900"
              />
            </ReactFlow>
          </div>
        </CardContent>
      </Card>

      {/* Node Palette */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Node Palette</CardTitle>
          <CardDescription>
            Drag and drop components to build your workflow
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[
              { type: 'input', label: 'Input', icon: FileText, color: 'bg-blue-500' },
              { type: 'processor', label: 'Processor', icon: Settings, color: 'bg-purple-500' },
              { type: 'ai', label: 'AI Agent', icon: Bot, color: 'bg-green-500' },
              { type: 'validator', label: 'Validator', icon: Database, color: 'bg-yellow-500' },
              { type: 'analyzer', label: 'Analyzer', icon: Zap, color: 'bg-red-500' },
              { type: 'output', label: 'Output', icon: Download, color: 'bg-gray-700' },
            ].map((nodeType) => {
              const Icon = nodeType.icon
              return (
                <div
                  key={nodeType.type}
                  className="flex flex-col items-center p-3 border rounded-lg cursor-move hover:shadow-md transition-shadow"
                  draggable
                  onDragStart={(event) => {
                    event.dataTransfer.setData('application/reactflow', nodeType.type)
                    event.dataTransfer.effectAllowed = 'move'
                  }}
                >
                  <div className={`h-8 w-8 rounded ${nodeType.color} flex items-center justify-center mb-2`}>
                    <Icon className="h-4 w-4 text-white" />
                  </div>
                  <span className="text-xs font-medium">{nodeType.label}</span>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Execution Status */}
      {isRunning && (
        <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
          <CardContent className="flex items-center justify-between p-4">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="font-medium">Executing workflow...</span>
              <Badge variant="outline">Step 3/7</Badge>
            </div>
            <Button variant="outline" size="sm" onClick={() => setIsRunning(false)}>
              <Square className="mr-2 h-3 w-3" />
              Stop
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}