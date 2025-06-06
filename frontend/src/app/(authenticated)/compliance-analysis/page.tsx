"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, FileText, Users, TrendingUp, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ComplianceAnalysis {
  id: string;
  rfp_document_name: string;
  analysis_status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  total_requirements: number;
  total_proposals: number;
  processing_progress: number;
  analysis_results?: any;
  created_at: string;
  updated_at?: string;
}

interface ComplianceStatistics {
  total_analyses: number;
  completed_analyses: number;
  processing_analyses: number;
  failed_analyses: number;
  total_requirements_analyzed: number;
  total_proposals_analyzed: number;
  recent_analyses: any[];
}

const ComplianceAnalysisPage = () => {
  const router = useRouter();
  const [analyses, setAnalyses] = useState<ComplianceAnalysis[]>([]);
  const [statistics, setStatistics] = useState<ComplianceStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalyses();
    fetchStatistics();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const response = await fetch('/api/v1/compliance-analysis/statistics');
      if (response.ok) {
        const data = await response.json();
        setAnalyses(data.recent_analyses || []);
      }
    } catch (err) {
      console.error('Error fetching analyses:', err);
      setError('Failed to load analyses');
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch('/api/v1/compliance-analysis/statistics');
      if (response.ok) {
        const data = await response.json();
        setStatistics(data);
      }
    } catch (err) {
      console.error('Error fetching statistics:', err);
      setError('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'text-green-600 bg-green-50';
      case 'PROCESSING': return 'text-blue-600 bg-blue-50';
      case 'PENDING': return 'text-yellow-600 bg-yellow-50';
      case 'FAILED': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED': return <CheckCircle className="h-4 w-4" />;
      case 'PROCESSING': return <Clock className="h-4 w-4" />;
      case 'PENDING': return <AlertCircle className="h-4 w-4" />;
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

  const handleViewAnalysis = (analysisId: string) => {
    router.push(`/compliance-analysis/results/${analysisId}`);
  };

  const handleNewAnalysis = () => {
    router.push('/compliance-analysis/upload');
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Compliance Analysis</h1>
          <p className="text-gray-600 mt-2">
            Analyze vendor proposals against RFP requirements with AI-powered compliance assessment
          </p>
        </div>
        <Button onClick={handleNewAnalysis} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Analysis
        </Button>
      </div>

      {/* Module 2 Badge */}
      <Alert>
        <FileText className="h-4 w-4" />
        <AlertDescription>
          <strong>Module 2: Proposal Compliance & Vendor Assessment</strong> - AI-powered compliance matrix generation with automated vendor scoring and gap analysis.
        </AlertDescription>
      </Alert>

      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_analyses}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.completed_analyses} completed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Requirements Analyzed</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_requirements_analyzed}</div>
              <p className="text-xs text-muted-foreground">
                Across all analyses
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Proposals Evaluated</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_proposals_analyzed}</div>
              <p className="text-xs text-muted-foreground">
                Vendor submissions
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics.total_analyses > 0 
                  ? Math.round((statistics.completed_analyses / statistics.total_analyses) * 100)
                  : 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                Analysis completion rate
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="analyses">All Analyses</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Recent Analyses */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Analyses</CardTitle>
            </CardHeader>
            <CardContent>
              {analyses.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No analyses yet</h3>
                  <p className="text-gray-600 mb-4">
                    Get started by uploading an RFP and vendor proposals for compliance analysis.
                  </p>
                  <Button onClick={handleNewAnalysis}>
                    Create Your First Analysis
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {analyses.slice(0, 5).map((analysis) => (
                    <div
                      key={analysis.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleViewAnalysis(analysis.id)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-medium text-gray-900">
                            {analysis.rfp_document_name}
                          </h4>
                          <Badge 
                            variant="secondary" 
                            className={`flex items-center gap-1 ${getStatusColor(analysis.analysis_status)}`}
                          >
                            {getStatusIcon(analysis.analysis_status)}
                            {analysis.analysis_status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span>{analysis.total_requirements} requirements</span>
                          <span>{analysis.total_proposals} proposals</span>
                          <span>Created {formatDate(analysis.created_at)}</span>
                        </div>
                        {analysis.analysis_status === 'PROCESSING' && (
                          <div className="mt-2">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${analysis.processing_progress}%` }}
                              ></div>
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              {Math.round(analysis.processing_progress)}% complete
                            </p>
                          </div>
                        )}
                      </div>
                      <Button variant="outline" size="sm">
                        View Results
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button 
                  variant="outline" 
                  className="flex flex-col items-center gap-2 h-24"
                  onClick={handleNewAnalysis}
                >
                  <Plus className="h-6 w-6" />
                  New Analysis
                </Button>
                <Button 
                  variant="outline" 
                  className="flex flex-col items-center gap-2 h-24"
                  onClick={() => router.push('/compliance-analysis')}
                >
                  <FileText className="h-6 w-6" />
                  View All Analyses
                </Button>
                <Button 
                  variant="outline" 
                  className="flex flex-col items-center gap-2 h-24"
                  onClick={() => router.push('/help/compliance-analysis')}
                >
                  <AlertCircle className="h-6 w-6" />
                  Help & Guides
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analyses" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>All Compliance Analyses</CardTitle>
            </CardHeader>
            <CardContent>
              {analyses.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No analyses found</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {analyses.map((analysis) => (
                    <div
                      key={analysis.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleViewAnalysis(analysis.id)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-medium text-gray-900">
                            {analysis.rfp_document_name}
                          </h4>
                          <Badge 
                            variant="secondary" 
                            className={`flex items-center gap-1 ${getStatusColor(analysis.analysis_status)}`}
                          >
                            {getStatusIcon(analysis.analysis_status)}
                            {analysis.analysis_status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span>{analysis.total_requirements} requirements</span>
                          <span>{analysis.total_proposals} proposals</span>
                          <span>Created {formatDate(analysis.created_at)}</span>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Compliance Trends</h4>
                  <p className="text-sm text-gray-600">
                    Track compliance scores and vendor performance across analyses to identify trends and improve RFP requirements.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Vendor Insights</h4>
                  <p className="text-sm text-gray-600">
                    Analyze vendor strengths and weaknesses across different requirement categories to make better selection decisions.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Requirement Quality</h4>
                  <p className="text-sm text-gray-600">
                    Identify which requirements are consistently well-addressed and which may need clarification or revision.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Gap Analysis</h4>
                  <p className="text-sm text-gray-600">
                    Discover common gaps across vendors to understand market capabilities and adjust expectations.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ComplianceAnalysisPage;