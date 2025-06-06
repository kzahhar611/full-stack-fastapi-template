"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { 
  ArrowLeft,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Eye,
  TrendingUp,
  TrendingDown,
  Target,
  Users,
  Calendar,
  DollarSign,
  Zap,
  Shield,
  Brain,
  Download,
  Share,
  Edit,
  MessageSquare
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"

// Mock analysis data
const mockAnalysisData = {
  id: "analysis_demo_20250103_120000",
  rfpTitle: "Enterprise Software Development Platform",
  status: "completed",
  createdAt: "2025-01-03T12:00:00Z",
  analysisDuration: 45,
  
  decision: {
    type: "go",
    confidenceScore: 0.85,
    primaryJustification: "Strong strategic alignment with our core capabilities and high win probability based on technical expertise match.",
    detailedReasoning: [
      "Excellent alignment with our AI/ML and cloud development expertise",
      "Client's requirements match 92% of our proven capabilities",
      "Competitive landscape favors our unique positioning in enterprise AI",
      "Strong relationship potential with strategic client in target market",
      "Financial projections exceed our profitability thresholds"
    ],
    riskFactors: [
      "Aggressive timeline requires careful resource planning",
      "Integration complexity with legacy systems",
      "Potential scope creep in AI/ML requirements"
    ],
    successFactors: [
      "Proven track record in similar enterprise AI implementations",
      "Strong technical team with relevant expertise",
      "Existing partnerships with required technology vendors",
      "Clear understanding of client's business objectives"
    ],
    conditions: [
      "Secure commitment for phased delivery approach",
      "Establish clear scope boundaries for AI components",
      "Confirm resource availability for Q2-Q3 timeline"
    ],
    estimatedWinProbability: 0.78
  },
  
  riskAssessment: {
    overallRiskLevel: "medium",
    riskScore: 5.2,
    technicalRisks: [
      {
        description: "Integration with legacy ERP systems",
        probability: "medium",
        impact: "high",
        mitigationStrategy: "Develop integration layer with fallback options"
      },
      {
        description: "AI model accuracy requirements",
        probability: "low",
        impact: "medium", 
        mitigationStrategy: "Implement robust testing and validation framework"
      }
    ],
    commercialRisks: [
      {
        description: "Fixed-price contract with scope uncertainties",
        probability: "medium",
        impact: "high",
        mitigationStrategy: "Negotiate change management provisions"
      }
    ],
    operationalRisks: [
      {
        description: "Resource availability during peak period",
        probability: "high",
        impact: "medium",
        mitigationStrategy: "Cross-train team members and identify backup resources"
      }
    ],
    legalRisks: [
      {
        description: "Data privacy compliance requirements",
        probability: "low",
        impact: "high",
        mitigationStrategy: "Engage legal counsel early and implement GDPR framework"
      }
    ]
  },
  
  projectInsights: {
    complexity: "high",
    estimatedDurationMonths: 8,
    estimatedCostRange: { min: 450000, max: 650000 },
    technologyStack: ["React", "Node.js", "Python", "TensorFlow", "AWS", "PostgreSQL"],
    requiredTeamSize: 12,
    keySuccessFactors: [
      "Strong project management and communication",
      "Agile development methodology",
      "Continuous client engagement",
      "Robust testing and quality assurance"
    ],
    competitiveAdvantages: [
      "Unique AI/ML expertise in enterprise applications",
      "Proven track record with similar Fortune 500 clients",
      "Strong partnership ecosystem",
      "Agile delivery methodology"
    ],
    potentialChallenges: [
      "Complex integration requirements",
      "Tight timeline for comprehensive testing",
      "Managing stakeholder expectations across multiple departments"
    ]
  },
  
  kpiDashboard: {
    strategicScore: 0.82,
    riskScore: 5.2,
    complexityScore: 0.75,
    winProbability: 0.78,
    financialAttractiveness: 0.85,
    resourceRequirements: {
      teamSize: 12,
      durationMonths: 8,
      technologyComplexity: "high"
    },
    keyMetrics: {
      alignmentScore: 0.88,
      competitivePosition: 0.79,
      deliveryConfidence: 0.73
    }
  }
}

export default function AnalysisResultsPage() {
  const router = useRouter()
  const params = useParams()
  const [selectedTab, setSelectedTab] = useState("overview")
  const [isLoading, setIsLoading] = useState(true)
  const [showDecisionDialog, setShowDecisionDialog] = useState(false)
  const [newDecision, setNewDecision] = useState("")
  const [decisionReason, setDecisionReason] = useState("")
  const [analysisData, setAnalysisData] = useState(mockAnalysisData)
  const [isDownloading, setIsDownloading] = useState(false)

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setIsLoading(false), 1000)
  }, [])

  const downloadAnalysis = async (format: 'pdf' | 'html' | 'pptx') => {
    try {
      setIsDownloading(true)
      
      // In a real implementation, this would call the API
      const analysisId = params.analysisId as string
      const response = await fetch(`/api/v1/documents/generate/analysis/${analysisId}/${format}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })

      if (!response.ok) {
        throw new Error('Download failed')
      }

      // Get filename from response headers
      const contentDisposition = response.headers.get('content-disposition')
      const filename = contentDisposition?.match(/filename="(.+)"/)?.[1] || 
                     `analysis_${analysisId}.${format}`

      // Create blob and download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      
      // Cleanup
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)
      
    } catch (error) {
      console.error('Download error:', error)
      // In a real app, show toast notification
      alert('Download failed. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case "go":
        return <CheckCircle className="h-6 w-6 text-green-600" />
      case "no_go":
        return <XCircle className="h-6 w-6 text-red-600" />
      case "conditional":
        return <AlertTriangle className="h-6 w-6 text-yellow-600" />
      default:
        return <Eye className="h-6 w-6 text-blue-600" />
    }
  }

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case "go":
        return "text-green-600 bg-green-50 border-green-200"
      case "no_go":
        return "text-red-600 bg-red-50 border-red-200"
      case "conditional":
        return "text-yellow-600 bg-yellow-50 border-yellow-200"
      default:
        return "text-blue-600 bg-blue-50 border-blue-200"
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case "low":
        return "text-green-600"
      case "medium":
        return "text-yellow-600"
      case "high":
        return "text-orange-600"
      case "critical":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <Brain className="h-12 w-12 mx-auto mb-4 text-blue-600 animate-pulse" />
          <p className="text-lg font-medium">Loading analysis results...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Analysis Results</h1>
            <p className="text-muted-foreground">
              {analysisData.rfpTitle} • Completed {new Date(analysisData.createdAt).toLocaleDateString()}
            </p>
          </div>
        </div>
        <div className="flex space-x-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => downloadAnalysis('pdf')}>
                <FileText className="h-4 w-4 mr-2" />
                Download PDF
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => downloadAnalysis('html')}>
                <FileText className="h-4 w-4 mr-2" />
                Download HTML
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => downloadAnalysis('pptx')}>
                <FileText className="h-4 w-4 mr-2" />
                Download PowerPoint
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button variant="outline" size="sm">
            <Share className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Dialog open={showDecisionDialog} onOpenChange={setShowDecisionDialog}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Edit className="h-4 w-4 mr-2" />
                Update Decision
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Update Analysis Decision</DialogTitle>
                <DialogDescription>
                  Override the AI recommendation with your own decision
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>New Decision</Label>
                  <Select value={newDecision} onValueChange={setNewDecision}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select decision" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="go">Go</SelectItem>
                      <SelectItem value="no_go">No Go</SelectItem>
                      <SelectItem value="conditional">Conditional</SelectItem>
                      <SelectItem value="needs_review">Needs Review</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Reason for Change</Label>
                  <Textarea
                    placeholder="Explain why you're changing the decision..."
                    value={decisionReason}
                    onChange={(e) => setDecisionReason(e.target.value)}
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowDecisionDialog(false)}>
                    Cancel
                  </Button>
                  <Button onClick={() => setShowDecisionDialog(false)}>
                    Update Decision
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Decision Summary Card */}
      <Card className={`border-2 ${getDecisionColor(analysisData.decision.type)}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {getDecisionIcon(analysisData.decision.type)}
              <div>
                <h2 className="text-2xl font-bold capitalize">
                  {analysisData.decision.type.replace('_', ' ')} Recommendation
                </h2>
                <p className="text-lg font-medium">
                  Confidence: {Math.round(analysisData.decision.confidenceScore * 100)}%
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Win Probability</div>
              <div className="text-3xl font-bold">
                {Math.round(analysisData.decision.estimatedWinProbability * 100)}%
              </div>
            </div>
          </div>
          <Separator className="my-4" />
          <p className="text-lg">{analysisData.decision.primaryJustification}</p>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Strategic Alignment</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(analysisData.kpiDashboard.strategicScore * 100)}%
            </div>
            <Progress value={analysisData.kpiDashboard.strategicScore * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Score</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getRiskColor(analysisData.riskAssessment.overallRiskLevel)}`}>
              {analysisData.riskAssessment.riskScore.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground">
              {analysisData.riskAssessment.overallRiskLevel.toUpperCase()} risk
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Project Value</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(analysisData.projectInsights.estimatedCostRange.min)} - {formatCurrency(analysisData.projectInsights.estimatedCostRange.max)}
            </div>
            <p className="text-xs text-muted-foreground">
              Estimated project value
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Timeline</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analysisData.projectInsights.estimatedDurationMonths} months
            </div>
            <p className="text-xs text-muted-foreground">
              Team of {analysisData.projectInsights.requiredTeamSize} people
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analysis Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="reasoning">Reasoning</TabsTrigger>
          <TabsTrigger value="risks">Risk Analysis</TabsTrigger>
          <TabsTrigger value="insights">Project Insights</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Success Factors */}
            <Card>
              <CardHeader>
                <CardTitle className="text-green-600">Success Factors</CardTitle>
                <CardDescription>
                  Key factors supporting this opportunity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {analysisData.decision.successFactors.map((factor, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{factor}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Risk Factors */}
            <Card>
              <CardHeader>
                <CardTitle className="text-yellow-600">Risk Factors</CardTitle>
                <CardDescription>
                  Areas requiring attention and mitigation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {analysisData.decision.riskFactors.map((risk, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{risk}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Conditions (if conditional decision) */}
          {analysisData.decision.type === "conditional" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-blue-600">Conditions for Proceeding</CardTitle>
                <CardDescription>
                  Requirements that must be met before moving forward
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {analysisData.decision.conditions.map((condition, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{condition}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Technology Stack */}
          <Card>
            <CardHeader>
              <CardTitle>Required Technology Stack</CardTitle>
              <CardDescription>
                Technologies identified for this project
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {analysisData.projectInsights.technologyStack.map((tech, index) => (
                  <Badge key={index} variant="secondary">{tech}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reasoning" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Detailed Reasoning</CardTitle>
              <CardDescription>
                AI analysis breakdown supporting the recommendation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="space-y-4">
                {analysisData.decision.detailedReasoning.map((reason, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-sm font-semibold text-blue-600 mt-0.5 flex-shrink-0">
                      {index + 1}
                    </div>
                    <span>{reason}</span>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Competitive Advantages</CardTitle>
              <CardDescription>
                Your organization's strengths for this opportunity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {analysisData.projectInsights.competitiveAdvantages.map((advantage, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <TrendingUp className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{advantage}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risks" className="space-y-6">
          {/* Risk Categories */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-red-600">Technical Risks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisData.riskAssessment.technicalRisks.map((risk, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-sm">{risk.description}</h4>
                        <div className="flex space-x-2">
                          <Badge variant="outline" className="text-xs">
                            {risk.probability} prob
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {risk.impact} impact
                          </Badge>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        <strong>Mitigation:</strong> {risk.mitigationStrategy}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-orange-600">Commercial Risks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisData.riskAssessment.commercialRisks.map((risk, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-sm">{risk.description}</h4>
                        <div className="flex space-x-2">
                          <Badge variant="outline" className="text-xs">
                            {risk.probability} prob
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {risk.impact} impact
                          </Badge>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        <strong>Mitigation:</strong> {risk.mitigationStrategy}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-yellow-600">Operational Risks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisData.riskAssessment.operationalRisks.map((risk, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-sm">{risk.description}</h4>
                        <div className="flex space-x-2">
                          <Badge variant="outline" className="text-xs">
                            {risk.probability} prob
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {risk.impact} impact
                          </Badge>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        <strong>Mitigation:</strong> {risk.mitigationStrategy}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-purple-600">Legal Risks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisData.riskAssessment.legalRisks.map((risk, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-sm">{risk.description}</h4>
                        <div className="flex space-x-2">
                          <Badge variant="outline" className="text-xs">
                            {risk.probability} prob
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {risk.impact} impact
                          </Badge>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        <strong>Mitigation:</strong> {risk.mitigationStrategy}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Project Characteristics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Complexity:</span>
                  <Badge variant={
                    analysisData.projectInsights.complexity === 'high' ? 'destructive' :
                    analysisData.projectInsights.complexity === 'medium' ? 'default' : 'secondary'
                  }>
                    {analysisData.projectInsights.complexity.toUpperCase()}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Duration:</span>
                  <span className="font-medium">{analysisData.projectInsights.estimatedDurationMonths} months</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Team Size:</span>
                  <span className="font-medium">{analysisData.projectInsights.requiredTeamSize} people</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Budget Range:</span>
                  <span className="font-medium">
                    {formatCurrency(analysisData.projectInsights.estimatedCostRange.min)} - {formatCurrency(analysisData.projectInsights.estimatedCostRange.max)}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Key Success Factors</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {analysisData.projectInsights.keySuccessFactors.map((factor, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <Target className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{factor}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Potential Challenges</CardTitle>
              <CardDescription>
                Areas that may require special attention
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {analysisData.projectInsights.potentialChallenges.map((challenge, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <AlertTriangle className="h-5 w-5 text-orange-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{challenge}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Next Steps</CardTitle>
                <CardDescription>
                  Recommended actions based on this analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisData.decision.type === "go" && (
                    <>
                      <Alert>
                        <CheckCircle className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Proceed with proposal development.</strong> This opportunity aligns well with your strategic objectives and capabilities.
                        </AlertDescription>
                      </Alert>
                      <div className="space-y-3">
                        <h4 className="font-semibold">Immediate Actions:</h4>
                        <ul className="space-y-2 text-sm">
                          <li>• Assemble core proposal team within 48 hours</li>
                          <li>• Schedule stakeholder alignment meeting</li>
                          <li>• Begin technical architecture planning</li>
                          <li>• Confirm resource availability for projected timeline</li>
                          <li>• Initiate preliminary client engagement</li>
                        </ul>
                      </div>
                    </>
                  )}
                  
                  {analysisData.decision.type === "conditional" && (
                    <>
                      <Alert>
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Proceed with caution.</strong> Address the specified conditions before committing resources.
                        </AlertDescription>
                      </Alert>
                      <div className="space-y-3">
                        <h4 className="font-semibold">Required Actions:</h4>
                        <ul className="space-y-2 text-sm">
                          {analysisData.decision.conditions.map((condition, index) => (
                            <li key={index}>• {condition}</li>
                          ))}
                        </ul>
                      </div>
                    </>
                  )}

                  {analysisData.decision.type === "no_go" && (
                    <>
                      <Alert className="border-red-200 bg-red-50">
                        <XCircle className="h-4 w-4 text-red-600" />
                        <AlertDescription>
                          <strong>Do not proceed.</strong> The risks and challenges outweigh the potential benefits.
                        </AlertDescription>
                      </Alert>
                      <div className="space-y-3">
                        <h4 className="font-semibold">Alternative Actions:</h4>
                        <ul className="space-y-2 text-sm">
                          <li>• Document lessons learned for future opportunities</li>
                          <li>• Consider if client relationship has other potential</li>
                          <li>• Focus resources on higher-probability opportunities</li>
                          <li>• Use analysis insights to improve capability gaps</li>
                        </ul>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Long-term Strategic Considerations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Market Positioning</h4>
                    <p className="text-sm text-muted-foreground">
                      This opportunity could establish stronger presence in the enterprise AI market and create reference value for future proposals.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Capability Development</h4>
                    <p className="text-sm text-muted-foreground">
                      Success would enhance your team's expertise in enterprise integrations and strengthen vendor partnerships.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Financial Impact</h4>
                    <p className="text-sm text-muted-foreground">
                      Project contributes significantly to Q2-Q3 revenue targets and provides good profit margins within risk tolerance.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Analysis Metadata */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Analysis Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4 text-sm">
            <div>
              <span className="text-muted-foreground">Analysis ID:</span>
              <p className="font-mono">{analysisData.id}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Completed:</span>
              <p>{new Date(analysisData.createdAt).toLocaleString()}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Duration:</span>
              <p>{analysisData.analysisDuration} seconds</p>
            </div>
            <div>
              <span className="text-muted-foreground">Status:</span>
              <Badge variant="default">{analysisData.status}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}