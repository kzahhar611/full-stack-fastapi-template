"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useDropzone } from "react-dropzone"
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle,
  X,
  ArrowLeft,
  Bot,
  Zap,
  Target,
  Brain
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface UploadedFile {
  file: File
  id: string
  status: 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  extractedText?: string
  error?: string
}

export default function UploadAnalyzePage() {
  const router = useRouter()
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    companyName: "",
    industry: "",
    companySize: "",
    coreCapabilities: "",
    strategicGoals: ""
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'uploading' as const,
      progress: 0
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])

    // Simulate file upload and processing
    newFiles.forEach(uploadFile => {
      simulateFileProcessing(uploadFile.id)
    })
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'application/rtf': ['.rtf']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024 // 10MB
  })

  const simulateFileProcessing = (fileId: string) => {
    // Simulate upload progress
    let progress = 0
    const uploadInterval = setInterval(() => {
      progress += 10
      setUploadedFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, progress } : f
      ))
      
      if (progress >= 100) {
        clearInterval(uploadInterval)
        // Simulate text extraction
        setTimeout(() => {
          setUploadedFiles(prev => prev.map(f => 
            f.id === fileId ? { 
              ...f, 
              status: 'processing',
              extractedText: "Sample extracted text from document..." 
            } : f
          ))
          
          // Complete processing
          setTimeout(() => {
            setUploadedFiles(prev => prev.map(f => 
              f.id === fileId ? { ...f, status: 'completed' } : f
            ))
          }, 1500)
        }, 1000)
      }
    }, 200)
  }

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const startAnalysis = async () => {
    if (uploadedFiles.length === 0 || uploadedFiles.some(f => f.status !== 'completed')) {
      return
    }

    setIsAnalyzing(true)
    setAnalysisProgress(0)

    // Simulate analysis progress
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          setTimeout(() => {
            router.push('/rfp-analysis/results/analysis_demo_20250103_120000')
          }, 1000)
          return 100
        }
        return prev + 5
      })
    }, 300)
  }

  const canStartAnalysis = uploadedFiles.length > 0 && 
    uploadedFiles.every(f => f.status === 'completed') &&
    formData.title.trim() !== ""

  const getFileStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return <FileText className="h-4 w-4 text-blue-600" />
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Upload & Analyze RFP</h1>
          <p className="text-muted-foreground">
            Upload your RFP document for AI-powered strategic analysis
          </p>
        </div>
      </div>

      {/* Analysis Process Steps */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bot className="h-5 w-5 text-blue-600" />
            <span>AI Analysis Process</span>
          </CardTitle>
          <CardDescription>
            Our AI will analyze your RFP through multiple strategic dimensions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="text-center p-4 border rounded-lg">
              <FileText className="h-8 w-8 mx-auto mb-2 text-blue-600" />
              <h4 className="font-semibold text-sm">Document Extraction</h4>
              <p className="text-xs text-muted-foreground mt-1">
                Extract and parse RFP content
              </p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Brain className="h-8 w-8 mx-auto mb-2 text-purple-600" />
              <h4 className="font-semibold text-sm">Strategic Analysis</h4>
              <p className="text-xs text-muted-foreground mt-1">
                Assess strategic alignment
              </p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Target className="h-8 w-8 mx-auto mb-2 text-green-600" />
              <h4 className="font-semibold text-sm">Risk Assessment</h4>
              <p className="text-xs text-muted-foreground mt-1">
                Identify and evaluate risks
              </p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Zap className="h-8 w-8 mx-auto mb-2 text-yellow-600" />
              <h4 className="font-semibold text-sm">Go/No-Go Decision</h4>
              <p className="text-xs text-muted-foreground mt-1">
                Generate recommendation
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* File Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle>1. Upload RFP Document</CardTitle>
            <CardDescription>
              Supported formats: PDF, DOCX, DOC, TXT, RTF (max 10MB)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Drop Zone */}
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              {isDragActive ? (
                <p className="text-blue-600">Drop the RFP document here...</p>
              ) : (
                <div>
                  <p className="text-gray-600 mb-2">
                    Drag & drop your RFP document here, or click to select
                  </p>
                  <Button variant="outline" type="button">
                    Choose File
                  </Button>
                </div>
              )}
            </div>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-semibold">Uploaded Files</h4>
                {uploadedFiles.map((uploadFile) => (
                  <div key={uploadFile.id} className="flex items-center space-x-3 p-3 border rounded-lg">
                    {getFileStatusIcon(uploadFile.status)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium truncate">
                          {uploadFile.file.name}
                        </p>
                        <Button
                          variant="ghost" 
                          size="sm"
                          onClick={() => removeFile(uploadFile.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      {uploadFile.status !== 'completed' && (
                        <Progress value={uploadFile.progress} className="mt-2" />
                      )}
                      {uploadFile.error && (
                        <p className="text-xs text-red-600 mt-1">{uploadFile.error}</p>
                      )}
                    </div>
                    <Badge variant={
                      uploadFile.status === 'completed' ? 'default' : 
                      uploadFile.status === 'error' ? 'destructive' : 'secondary'
                    }>
                      {uploadFile.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* RFP Information */}
        <Card>
          <CardHeader>
            <CardTitle>2. RFP Information</CardTitle>
            <CardDescription>
              Provide basic information about the RFP
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">RFP Title *</Label>
              <Input
                id="title"
                placeholder="Enter RFP title"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Brief description of the RFP"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Company Context */}
      <Card>
        <CardHeader>
          <CardTitle>3. Company Context (Optional)</CardTitle>
          <CardDescription>
            Provide your company information for more accurate strategic analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="companyName">Company Name</Label>
              <Input
                id="companyName"
                placeholder="Your company name"
                value={formData.companyName}
                onChange={(e) => setFormData(prev => ({ ...prev, companyName: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="industry">Industry</Label>
              <Select value={formData.industry} onValueChange={(value) => setFormData(prev => ({ ...prev, industry: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select industry" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technology">Technology</SelectItem>
                  <SelectItem value="consulting">Consulting</SelectItem>
                  <SelectItem value="manufacturing">Manufacturing</SelectItem>
                  <SelectItem value="healthcare">Healthcare</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="companySize">Company Size</Label>
              <Select value={formData.companySize} onValueChange={(value) => setFormData(prev => ({ ...prev, companySize: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select size" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="startup">Startup (1-10)</SelectItem>
                  <SelectItem value="small">Small (11-50)</SelectItem>
                  <SelectItem value="medium">Medium (51-200)</SelectItem>
                  <SelectItem value="large">Large (201-1000)</SelectItem>
                  <SelectItem value="enterprise">Enterprise (1000+)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2 md:col-span-2 lg:col-span-3">
              <Label htmlFor="coreCapabilities">Core Capabilities</Label>
              <Textarea
                id="coreCapabilities"
                placeholder="List your key capabilities and expertise areas"
                value={formData.coreCapabilities}
                onChange={(e) => setFormData(prev => ({ ...prev, coreCapabilities: e.target.value }))}
                rows={2}
              />
            </div>

            <div className="space-y-2 md:col-span-2 lg:col-span-3">
              <Label htmlFor="strategicGoals">Strategic Goals</Label>
              <Textarea
                id="strategicGoals"
                placeholder="Describe your strategic objectives and goals"
                value={formData.strategicGoals}
                onChange={(e) => setFormData(prev => ({ ...prev, strategicGoals: e.target.value }))}
                rows={2}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Progress */}
      {isAnalyzing && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bot className="h-5 w-5 text-blue-600 animate-pulse" />
              <span>Analyzing RFP...</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Progress value={analysisProgress} className="w-full" />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Progress: {analysisProgress}%</span>
                <span>Estimated time: {Math.max(0, Math.round((100 - analysisProgress) * 0.5))}s</span>
              </div>
              <div className="grid gap-2 md:grid-cols-4 text-sm">
                <div className={`p-2 rounded ${analysisProgress > 25 ? 'bg-green-100 text-green-800' : 'bg-gray-100'}`}>
                  ✓ Document processed
                </div>
                <div className={`p-2 rounded ${analysisProgress > 50 ? 'bg-green-100 text-green-800' : 'bg-gray-100'}`}>
                  {analysisProgress > 50 ? '✓' : '⏳'} Strategic analysis
                </div>
                <div className={`p-2 rounded ${analysisProgress > 75 ? 'bg-green-100 text-green-800' : 'bg-gray-100'}`}>
                  {analysisProgress > 75 ? '✓' : '⏳'} Risk assessment
                </div>
                <div className={`p-2 rounded ${analysisProgress >= 100 ? 'bg-green-100 text-green-800' : 'bg-gray-100'}`}>
                  {analysisProgress >= 100 ? '✓' : '⏳'} Decision generation
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => router.back()}>
          Cancel
        </Button>
        <Button 
          onClick={startAnalysis}
          disabled={!canStartAnalysis || isAnalyzing}
          className="min-w-32"
        >
          {isAnalyzing ? (
            <>
              <Bot className="h-4 w-4 mr-2 animate-pulse" />
              Analyzing...
            </>
          ) : (
            <>
              <Zap className="h-4 w-4 mr-2" />
              Start Analysis
            </>
          )}
        </Button>
      </div>

      {/* Requirements Alert */}
      {!canStartAnalysis && uploadedFiles.length > 0 && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Please ensure all files are processed and provide an RFP title before starting analysis.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}