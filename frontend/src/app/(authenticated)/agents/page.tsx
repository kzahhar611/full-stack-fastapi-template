"use client"

import { useState } from "react"
import { 
  Plus, 
  Search, 
  Bot, 
  Settings, 
  Play, 
  Pause, 
  MoreHorizontal,
  Edit,
  Copy,
  Trash2,
  Activity,
  Zap,
  Brain,
  MessageSquare,
  FileText,
  Database
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"

// Mock data for AI Agents
const agents = [
  {
    id: "1",
    name: "RFP Analyzer Pro",
    description: "Comprehensive RFP analysis with risk assessment and compliance checking",
    type: "analyzer",
    status: "active",
    llm: "GPT-4 Turbo",
    lastRun: "2 minutes ago",
    totalRuns: 1247,
    successRate: 94.2,
    avgProcessingTime: "12.3s",
    icon: FileText,
    color: "bg-blue-500"
  },
  {
    id: "2",
    name: "Proposal Generator",
    description: "AI-powered proposal generation based on RFP requirements and company templates",
    type: "generator",
    status: "active", 
    llm: "Claude 3 Opus",
    lastRun: "15 minutes ago",
    totalRuns: 892,
    successRate: 96.8,
    avgProcessingTime: "18.7s",
    icon: Bot,
    color: "bg-purple-500"
  },
  {
    id: "3",
    name: "Compliance Checker",
    description: "Automated compliance verification against industry standards and regulations",
    type: "validator",
    status: "active",
    llm: "GPT-4",
    lastRun: "1 hour ago", 
    totalRuns: 2156,
    successRate: 99.1,
    avgProcessingTime: "8.4s",
    icon: Database,
    color: "bg-green-500"
  },
  {
    id: "4",
    name: "Contract Negotiator Assistant",
    description: "Intelligent contract analysis and negotiation point identification",
    type: "assistant",
    status: "paused",
    llm: "Gemini Pro",
    lastRun: "2 days ago",
    totalRuns: 543,
    successRate: 91.7,
    avgProcessingTime: "25.1s",
    icon: MessageSquare,
    color: "bg-orange-500"
  },
  {
    id: "5",
    name: "Market Intelligence Bot",
    description: "Real-time market research and competitive analysis for proposal pricing",
    type: "researcher",
    status: "active",
    llm: "Custom LLM",
    lastRun: "30 minutes ago",
    totalRuns: 1789,
    successRate: 88.3,
    avgProcessingTime: "45.2s",
    icon: Brain,
    color: "bg-pink-500"
  },
  {
    id: "6",
    name: "Document Summarizer",
    description: "Intelligent summarization of large documents and technical specifications",
    type: "processor",
    status: "active",
    llm: "Llama 2 70B",
    lastRun: "5 minutes ago",
    totalRuns: 3421,
    successRate: 97.5,
    avgProcessingTime: "6.8s",
    icon: Activity,
    color: "bg-teal-500"
  }
]

const agentTypes = [
  { label: "All Types", value: "all" },
  { label: "Analyzer", value: "analyzer" },
  { label: "Generator", value: "generator" },
  { label: "Validator", value: "validator" },
  { label: "Assistant", value: "assistant" },
  { label: "Researcher", value: "researcher" },
  { label: "Processor", value: "processor" }
]

export default function AgentsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedType, setSelectedType] = useState("all")

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = selectedType === "all" || agent.type === selectedType
    return matchesSearch && matchesType
  })

  const getStatusBadge = (status: string) => {
    const variants = {
      active: { variant: "default" as const, text: "Active", color: "bg-green-100 text-green-800" },
      paused: { variant: "secondary" as const, text: "Paused", color: "bg-yellow-100 text-yellow-800" },
      stopped: { variant: "outline" as const, text: "Stopped", color: "bg-red-100 text-red-800" }
    }
    
    const config = variants[status as keyof typeof variants] || variants.active
    return <Badge className={config.color}>{config.text}</Badge>
  }

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 95) return "text-green-600"
    if (rate >= 90) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Agents</h1>
          <p className="text-muted-foreground">
            Manage and configure your intelligent AI agents for RFP processing
          </p>
        </div>
        <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
          <Plus className="mr-2 h-4 w-4" />
          Create New Agent
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agents.length}</div>
            <p className="text-xs text-muted-foreground">
              {agents.filter(a => a.status === 'active').length} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Runs</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(agents.reduce((sum, agent) => sum + agent.totalRuns, 0) / 1000).toFixed(1)}K
            </div>
            <p className="text-xs text-muted-foreground">
              Last 30 days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Success Rate</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(agents.reduce((sum, agent) => sum + agent.successRate, 0) / agents.length).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Across all agents
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Processing</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">15.2s</div>
            <p className="text-xs text-muted-foreground">
              Average response time
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <div className="flex items-center justify-between space-x-4">
        <div className="flex items-center space-x-2 flex-1">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search agents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <Settings className="mr-2 h-4 w-4" />
                Type: {agentTypes.find(t => t.value === selectedType)?.label}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {agentTypes.map((type) => (
                <DropdownMenuItem
                  key={type.value}
                  onClick={() => setSelectedType(type.value)}
                >
                  {type.label}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <Button variant="outline">
          <Play className="mr-2 h-4 w-4" />
          Run All Active
        </Button>
      </div>

      {/* Agents Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredAgents.map((agent) => {
          const Icon = agent.icon
          return (
            <Card key={agent.id} className="group hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`h-10 w-10 rounded-lg ${agent.color} flex items-center justify-center`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{agent.name}</CardTitle>
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(agent.status)}
                        <Badge variant="outline" className="text-xs">
                          {agent.llm}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>
                        <Play className="mr-2 h-4 w-4" />
                        Run Agent
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Edit className="mr-2 h-4 w-4" />
                        Edit Configuration
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Copy className="mr-2 h-4 w-4" />
                        Duplicate
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <Pause className="mr-2 h-4 w-4" />
                        Pause Agent
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                
                <CardDescription className="mt-2">
                  {agent.description}
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-4">
                  {/* Performance Metrics */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">Total Runs</div>
                      <div className="font-semibold">{agent.totalRuns.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Success Rate</div>
                      <div className={`font-semibold ${getSuccessRateColor(agent.successRate)}`}>
                        {agent.successRate}%
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Avg Time</div>
                      <div className="font-semibold">{agent.avgProcessingTime}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Last Run</div>
                      <div className="font-semibold">{agent.lastRun}</div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2 pt-2">
                    <Button size="sm" className="flex-1">
                      <Play className="mr-2 h-3 w-3" />
                      Run
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <Settings className="mr-2 h-3 w-3" />
                      Configure
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Create Agent CTA */}
      <Card className="border-dashed border-2">
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Bot className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">Create Your First Custom Agent</h3>
          <p className="text-muted-foreground text-center mb-4 max-w-md">
            Build powerful AI agents tailored to your specific RFP processing needs. 
            Configure prompts, select LLMs, and define workflows.
          </p>
          <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
            <Plus className="mr-2 h-4 w-4" />
            Create Custom Agent
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}