"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowLeft, FileText, Users, Target, TrendingUp, CheckCircle, AlertTriangle, XCircle, Clock, Download, RefreshCw } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';

interface ComplianceAnalysis {
  id: string;
  rfp_document_name: string;
  analysis_status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  total_requirements: number;
  total_proposals: number;
  processing_progress: number;
  analysis_results?: {
    requirements_extracted: number;
    proposals_analyzed: number;
    top_vendor: string;
    top_score: number;
    average_score: number;
    compliance_overview: {
      total_assessments: number;
      compliant: number;
      partial: number;
      non_compliant: number;
      not_addressed: number;
    };
  };
  processing_time_seconds?: number;
  error_message?: string;
  created_at: string;
  updated_at?: string;
}

interface VendorRanking {
  proposal_id: string;
  vendor_name: string;
  overall_score: number;
  rank_position: number;
  category_scores: {
    technical?: number;
    functional?: number;
    commercial?: number;
    legal?: number;
    operational?: number;
  };
  compliance_distribution: {
    compliant: number;
    partial: number;
    non_compliant: number;
    not_addressed: number;
  };
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

const ComplianceAnalysisResultsPage = () => {
  const router = useRouter();
  const params = useParams();
  const analysisId = params.analysisId as string;

  const [analysis, setAnalysis] = useState<ComplianceAnalysis | null>(null);
  const [rankings, setRankings] = useState<VendorRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    fetchAnalysisResults();
    
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [analysisId]);

  useEffect(() => {
    // Set up polling for processing analyses
    if (analysis && (analysis.analysis_status === 'PROCESSING' || analysis.analysis_status === 'PENDING')) {
      const interval = setInterval(() => {
        fetchAnalysisResults(false);
      }, 3000); // Poll every 3 seconds
      
      setPollingInterval(interval);
    } else if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }

    // Fetch rankings if analysis is complete
    if (analysis && analysis.analysis_status === 'COMPLETED') {
      fetchVendorRankings();
    }
  }, [analysis?.analysis_status]);

  const fetchAnalysisResults = async (setLoadingState = true) => {
    try {
      if (setLoadingState) setLoading(true);
      
      const response = await fetch(`/api/v1/compliance-analysis/results/${analysisId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load analysis results');
      }
    } catch (err) {
      console.error('Error fetching analysis results:', err);
      setError('Failed to load analysis results');
    } finally {
      if (setLoadingState) setLoading(false);
    }
  };

  const fetchVendorRankings = async () => {
    try {
      const response = await fetch(`/api/v1/compliance-analysis/rankings/${analysisId}`);
      if (response.ok) {
        const data = await response.json();
        setRankings(data);
      }
    } catch (err) {
      console.error('Error fetching vendor rankings:', err);
    }
  };

  const handleRestartAnalysis = async () => {
    try {
      const response = await fetch(`/api/v1/compliance-analysis/analyze/${analysisId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        fetchAnalysisResults();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to restart analysis');
      }
    } catch (err) {
      setError('Failed to restart analysis');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'text-green-600 bg-green-50 border-green-200';
      case 'PROCESSING': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'PENDING': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'FAILED': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED': return <CheckCircle className="h-4 w-4" />;
      case 'PROCESSING': return <Clock className="h-4 w-4" />;
      case 'PENDING': return <AlertTriangle className="h-4 w-4" />;
      case 'FAILED': return <XCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getComplianceColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    if (percentage >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>Analysis not found</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => router.push('/compliance-analysis')}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Analyses
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">{analysis.rfp_document_name}</h1>
          <p className="text-gray-600 mt-2">
            Compliance Analysis Results • Created {formatDate(analysis.created_at)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge 
            variant="secondary" 
            className={`flex items-center gap-2 px-3 py-1 border ${getStatusColor(analysis.analysis_status)}`}
          >
            {getStatusIcon(analysis.analysis_status)}
            {analysis.analysis_status}
          </Badge>
        </div>
      </div>

      {/* Processing Status */}
      {(analysis.analysis_status === 'PROCESSING' || analysis.analysis_status === 'PENDING') && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Analysis in Progress
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Progress value={analysis.processing_progress} />
            <div className="flex justify-between text-sm text-gray-600">
              <span>{Math.round(analysis.processing_progress)}% complete</span>
              <span>
                {analysis.analysis_status === 'PROCESSING' 
                  ? 'Processing documents and generating compliance matrix...'
                  : 'Analysis queued for processing...'
                }
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Status */}
      {analysis.analysis_status === 'FAILED' && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>
              Analysis failed: {analysis.error_message || 'Unknown error occurred'}
            </span>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRestartAnalysis}
              className="ml-4"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Results Overview */}
      {analysis.analysis_status === 'COMPLETED' && analysis.analysis_results && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Requirements</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analysis.analysis_results.requirements_extracted}</div>
                <p className="text-xs text-muted-foreground">
                  Extracted from RFP
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Proposals</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analysis.analysis_results.proposals_analyzed}</div>
                <p className="text-xs text-muted-foreground">
                  Vendor submissions
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Top Score</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getComplianceColor(analysis.analysis_results.top_score)}`}>
                  {Math.round(analysis.analysis_results.top_score)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  {analysis.analysis_results.top_vendor}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Score</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getComplianceColor(analysis.analysis_results.average_score)}`}>
                  {Math.round(analysis.analysis_results.average_score)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Across all vendors
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Compliance Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Compliance Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {analysis.analysis_results.compliance_overview.compliant}
                  </div>
                  <p className="text-sm text-gray-600">Compliant</p>
                  <p className="text-xs text-gray-500">80-100% match</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">
                    {analysis.analysis_results.compliance_overview.partial}
                  </div>
                  <p className="text-sm text-gray-600">Partial</p>
                  <p className="text-xs text-gray-500">40-79% match</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {analysis.analysis_results.compliance_overview.non_compliant}
                  </div>
                  <p className="text-sm text-gray-600">Non-compliant</p>
                  <p className="text-xs text-gray-500">1-39% match</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-600">
                    {analysis.analysis_results.compliance_overview.not_addressed}
                  </div>
                  <p className="text-sm text-gray-600">Not Addressed</p>
                  <p className="text-xs text-gray-500">0% match</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Top Vendors */}
          {rankings.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Top Vendors</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {rankings.slice(0, 3).map((vendor, index) => (
                    <div key={vendor.proposal_id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          index === 0 ? 'bg-yellow-100 text-yellow-800' :
                          index === 1 ? 'bg-gray-100 text-gray-800' :
                          'bg-orange-100 text-orange-800'
                        }`}>
                          {vendor.rank_position}
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{vendor.vendor_name}</h4>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span>{vendor.compliance_distribution.compliant} compliant</span>
                            <span>{vendor.compliance_distribution.partial} partial</span>
                            {vendor.compliance_distribution.non_compliant > 0 && (
                              <span>{vendor.compliance_distribution.non_compliant} non-compliant</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${getComplianceColor(vendor.overall_score)}`}>
                          {Math.round(vendor.overall_score)}%
                        </div>
                        <p className="text-sm text-gray-600">Overall Score</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Navigation Tabs */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Button
                  variant="outline"
                  className="flex flex-col items-center gap-2 h-24"
                  onClick={() => router.push(`/compliance-analysis/matrix/${analysisId}`)}
                >
                  <Target className="h-6 w-6" />
                  <span>Compliance Matrix</span>
                </Button>
                <Button
                  variant="outline"
                  className="flex flex-col items-center gap-2 h-24"
                  onClick={() => router.push(`/compliance-analysis/rankings/${analysisId}`)}
                >
                  <TrendingUp className="h-6 w-6" />
                  <span>Vendor Rankings</span>
                </Button>
                <Button
                  variant="outline"
                  className="flex flex-col items-center gap-2 h-24"
                  onClick={() => router.push(`/compliance-analysis/gaps/${analysisId}`)}
                >
                  <AlertTriangle className="h-6 w-6" />
                  <span>Gap Analysis</span>
                </Button>
                <Button
                  variant="outline"
                  className="flex flex-col items-center gap-2 h-24"
                  onClick={() => window.open(`/api/v1/documents/generate/analysis/${analysisId}/pdf`, '_blank')}
                >
                  <Download className="h-6 w-6" />
                  <span>Export Report</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Processing Information */}
          <Card>
            <CardHeader>
              <CardTitle>Analysis Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2">Processing Details</h4>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>Processing time: {analysis.processing_time_seconds ? `${Math.round(analysis.processing_time_seconds)} seconds` : 'N/A'}</p>
                    <p>Total assessments: {analysis.analysis_results.compliance_overview.total_assessments}</p>
                    <p>Analysis ID: {analysis.id}</p>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Document Information</h4>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>RFP: {analysis.rfp_document_name}</p>
                    <p>Requirements extracted: {analysis.analysis_results.requirements_extracted}</p>
                    <p>Proposals analyzed: {analysis.analysis_results.proposals_analyzed}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default ComplianceAnalysisResultsPage;