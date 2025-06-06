"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { 
  Upload, 
  FileText, 
  BarChart3, 
  AlertTriangle, 
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Plus,
  Search,
  Filter,
  RefreshCw
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"

// Mock data for RFP analyses
const mockAnalyses = [
  {
    id: "1",
    rfpTitle: "Enterprise Software Development Platform",
    analysisId: "analysis_1_20250103_120000",
    status: "completed",
    decision: "go",
    confidenceScore: 0.85,
    winProbability: 0.78,
    riskScore: 4.2,
    strategicScore: 0.82,
    createdAt: "2025-01-03T12:00:00Z",
    analysisDuration: 45
  },
  {
    id: "2", 
    rfpTitle: "Cloud Infrastructure Migration",
    analysisId: "analysis_2_20250103_140000",
    status: "completed",
    decision: "conditional",
    confidenceScore: 0.71,
    winProbability: 0.65,
    riskScore: 6.8,
    strategicScore: 0.75,
    createdAt: "2025-01-03T14:00:00Z",
    analysisDuration: 52
  },
  {
    id: "3",
    rfpTitle: "Digital Marketing & Brand Strategy",
    analysisId: "analysis_3_20250103_160000", 
    status: "in_progress",
    decision: null,
    confidenceScore: null,
    winProbability: null,
    riskScore: null,
    strategicScore: null,
    createdAt: "2025-01-03T16:00:00Z",
    analysisDuration: null
  },
  {
    id: "4",
    rfpTitle: "Legacy System Modernization",
    analysisId: "analysis_4_20250103_180000",
    status: "completed",
    decision: "no_go",
    confidenceScore: 0.92,
    winProbability: 0.25,
    riskScore: 8.5,
    strategicScore: 0.45,
    createdAt: "2025-01-03T18:00:00Z", 
    analysisDuration: 38
  }
]

// Mock statistics
const mockStats = {
  totalAnalyses: 28,
  goDecisions: 12,
  noGoDecisions: 8,
  conditionalDecisions: 6,
  needsReviewDecisions: 2,
  averageWinProbability: 0.68,
  averageRiskScore: 5.2,
  topRiskFactors: [
    "Timeline constraints",
    "Technical complexity", 
    "Resource availability",
    "Budget limitations",
    "Client requirements clarity"
  ]
}

export default function RFPAnalysisPage() {
  const router = useRouter()
  const [selectedTab, setSelectedTab] = useState("overview")
  const [searchTerm, setSearchTerm] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [analyses, setAnalyses] = useState(mockAnalyses)
  const [stats, setStats] = useState(mockStats)

  const getDecisionBadge = (decision: string | null) => {
    if (!decision) return <Badge variant="outline">Analyzing</Badge>
    
    switch (decision) {
      case "go":
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-200">Go</Badge>
      case "no_go":
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-200">No Go</Badge>
      case "conditional":
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200">Conditional</Badge>
      case "needs_review":
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-200">Needs Review</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "in_progress":
        return <Clock className="h-4 w-4 text-yellow-600" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getRiskColor = (score: number | null) => {
    if (!score) return "text-gray-400"
    if (score <= 3) return "text-green-600"
    if (score <= 6) return "text-yellow-600"
    if (score <= 8) return "text-orange-600"
    return "text-red-600"
  }

  const filteredAnalyses = analyses.filter(analysis =>
    analysis.rfpTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
    analysis.analysisId.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">RFP Analysis & Decision Support</h1>
          <p className="text-muted-foreground">
            AI-powered strategic analysis for Go/No-Go decisions
          </p>
        </div>
        <div className="flex space-x-3">
          <Button 
            variant="outline"
            onClick={() => router.push("/rfp-analysis/upload")}
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload & Analyze
          </Button>
          <Button 
            onClick={() => router.push("/rfp-analysis/new")}
          >
            <Plus className="h-4 w-4 mr-2" />
            New Analysis
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAnalyses}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Go Decisions</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.goDecisions}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((stats.goDecisions / stats.totalAnalyses) * 100)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Win Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(stats.averageWinProbability * 100)}%</div>
            <Progress value={stats.averageWinProbability * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Risk Score</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getRiskColor(stats.averageRiskScore)}`}>
              {stats.averageRiskScore.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground">
              Out of 10.0 scale
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="analyses">All Analyses</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="risk-factors">Risk Factors</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Decision Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Decision Distribution</CardTitle>
              <CardDescription>
                Breakdown of Go/No-Go decisions over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{stats.goDecisions}</div>
                  <div className="text-sm text-muted-foreground">Go Decisions</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{stats.noGoDecisions}</div>
                  <div className="text-sm text-muted-foreground">No-Go Decisions</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">{stats.conditionalDecisions}</div>
                  <div className="text-sm text-muted-foreground">Conditional</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{stats.needsReviewDecisions}</div>
                  <div className="text-sm text-muted-foreground">Needs Review</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Analyses */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Analyses</CardTitle>
              <CardDescription>
                Latest RFP analyses and their outcomes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analyses.slice(0, 3).map((analysis) => (
                  <div key={analysis.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(analysis.status)}
                      <div>
                        <div className="font-medium">{analysis.rfpTitle}</div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(analysis.createdAt).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      {getDecisionBadge(analysis.decision)}
                      {analysis.winProbability && (
                        <div className="text-sm">
                          Win: {Math.round(analysis.winProbability * 100)}%
                        </div>
                      )}
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analyses" className="space-y-6">
          {/* Search and Filters */}
          <div className="flex items-center space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search analyses..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem>All Statuses</DropdownMenuItem>
                <DropdownMenuItem>Completed</DropdownMenuItem>
                <DropdownMenuItem>In Progress</DropdownMenuItem>
                <DropdownMenuItem>Failed</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button variant="outline" size="icon">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>

          {/* Analyses Table */}
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>RFP Title</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Decision</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Win Rate</TableHead>
                    <TableHead>Risk Score</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAnalyses.map((analysis) => (
                    <TableRow key={analysis.id}>
                      <TableCell className="font-medium">
                        <div>
                          <div>{analysis.rfpTitle}</div>
                          <div className="text-xs text-muted-foreground">
                            {analysis.analysisId}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(analysis.status)}
                          <span className="capitalize">{analysis.status.replace("_", " ")}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {getDecisionBadge(analysis.decision)}
                      </TableCell>
                      <TableCell>
                        {analysis.confidenceScore ? (
                          <div className="flex items-center space-x-2">
                            <span>{Math.round(analysis.confidenceScore * 100)}%</span>
                            <Progress value={analysis.confidenceScore * 100} className="w-16" />
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {analysis.winProbability ? (
                          `${Math.round(analysis.winProbability * 100)}%`
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {analysis.riskScore ? (
                          <span className={getRiskColor(analysis.riskScore)}>
                            {analysis.riskScore.toFixed(1)}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {new Date(analysis.createdAt).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          {/* Performance Insights */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Win Rate Trends</CardTitle>
                <CardDescription>
                  Success probability analysis over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center border-2 border-dashed rounded-lg">
                  <div className="text-center text-muted-foreground">
                    <BarChart3 className="h-12 w-12 mx-auto mb-2" />
                    <p>Win rate trends chart will be displayed here</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Risk vs. Reward</CardTitle>
                <CardDescription>
                  Risk score vs win probability analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center border-2 border-dashed rounded-lg">
                  <div className="text-center text-muted-foreground">
                    <TrendingUp className="h-12 w-12 mx-auto mb-2" />
                    <p>Risk vs reward scatter plot will be displayed here</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Strategic Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Strategic Insights</CardTitle>
              <CardDescription>
                Key patterns and recommendations from analysis data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                  <h4 className="font-semibold text-blue-900">High Success Rate in Tech Sector</h4>
                  <p className="text-blue-800">
                    Your organization shows 85% win rate for technology-focused RFPs, 
                    significantly above the 68% average.
                  </p>
                </div>
                <div className="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                  <h4 className="font-semibold text-yellow-900">Timeline Risk Pattern</h4>
                  <p className="text-yellow-800">
                    Analyses show 70% of high-risk assessments are driven by tight timelines. 
                    Consider timeline as a key decision factor.
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                  <h4 className="font-semibold text-green-900">Competitive Advantage</h4>
                  <p className="text-green-800">
                    Your team's AI/ML expertise is consistently identified as a key differentiator 
                    in 92% of Go decisions.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risk-factors" className="space-y-6">
          {/* Top Risk Factors */}
          <Card>
            <CardHeader>
              <CardTitle>Top Risk Factors</CardTitle>
              <CardDescription>
                Most common risks identified across all analyses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.topRiskFactors.map((factor, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-semibold text-red-600">{index + 1}</span>
                      </div>
                      <span className="font-medium">{factor}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Progress value={(5 - index) * 20} className="w-24" />
                      <span className="text-sm text-muted-foreground">
                        {Math.round((5 - index) * 20)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Risk Mitigation Strategies */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Mitigation Strategies</CardTitle>
              <CardDescription>
                Recommended strategies based on historical analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-3">
                  <h4 className="font-semibold">Timeline Constraints</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>• Add 20% buffer to initial estimates</li>
                    <li>• Use phased delivery approach</li>
                    <li>• Early stakeholder alignment</li>
                  </ul>
                </div>
                <div className="space-y-3">
                  <h4 className="font-semibold">Technical Complexity</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>• Proof of concept development</li>
                    <li>• Expert technical review</li>
                    <li>• Technology risk assessment</li>
                  </ul>
                </div>
                <div className="space-y-3">
                  <h4 className="font-semibold">Resource Availability</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>• Resource forecasting model</li>
                    <li>• Cross-training programs</li>
                    <li>• Partner capacity planning</li>
                  </ul>
                </div>
                <div className="space-y-3">
                  <h4 className="font-semibold">Budget Limitations</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>• Value-based pricing strategy</li>
                    <li>• Flexible engagement models</li>
                    <li>• Cost optimization analysis</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}