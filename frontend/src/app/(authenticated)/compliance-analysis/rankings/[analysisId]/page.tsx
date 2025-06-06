"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowLeft, Trophy, TrendingUp, Target, AlertTriangle, CheckCircle, Download, Users, Award } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';

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

const VendorRankingsPage = () => {
  const router = useRouter();
  const params = useParams();
  const analysisId = params.analysisId as string;

  const [rankings, setRankings] = useState<VendorRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVendors, setSelectedVendors] = useState<string[]>([]);

  useEffect(() => {
    fetchVendorRankings();
  }, [analysisId]);

  const fetchVendorRankings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/compliance-analysis/rankings/${analysisId}`);
      if (response.ok) {
        const data = await response.json();
        setRankings(data);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load vendor rankings');
      }
    } catch (err) {
      console.error('Error fetching vendor rankings:', err);
      setError('Failed to load vendor rankings');
    } finally {
      setLoading(false);
    }
  };

  const getRankBadgeColor = (position: number) => {
    switch (position) {
      case 1: return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 2: return 'bg-gray-100 text-gray-800 border-gray-300';
      case 3: return 'bg-orange-100 text-orange-800 border-orange-300';
      default: return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  const getRankIcon = (position: number) => {
    switch (position) {
      case 1: return <Trophy className="h-4 w-4 text-yellow-600" />;
      case 2: return <Award className="h-4 w-4 text-gray-600" />;
      case 3: return <Award className="h-4 w-4 text-orange-600" />;
      default: return <Target className="h-4 w-4 text-blue-600" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const categoryLabels = {
    technical: 'Technical',
    functional: 'Functional',
    commercial: 'Commercial',
    legal: 'Legal',
    operational: 'Operational'
  };

  const toggleVendorComparison = (vendorId: string) => {
    setSelectedVendors(prev => 
      prev.includes(vendorId) 
        ? prev.filter(id => id !== vendorId)
        : [...prev, vendorId].slice(0, 3) // Max 3 vendors for comparison
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
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
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const comparisonVendors = rankings.filter(vendor => 
    selectedVendors.includes(vendor.proposal_id)
  );

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => router.push(`/compliance-analysis/results/${analysisId}`)}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Results
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">Vendor Rankings</h1>
          <p className="text-gray-600 mt-2">
            Comprehensive vendor comparison and performance analysis
          </p>
        </div>
        <Button 
          variant="outline"
          className="flex items-center gap-2"
          onClick={() => window.open(`/api/v1/documents/generate/analysis/${analysisId}/pdf`, '_blank')}
        >
          <Download className="h-4 w-4" />
          Export Rankings
        </Button>
      </div>

      <Tabs defaultValue="rankings" className="space-y-6">
        <TabsList>
          <TabsTrigger value="rankings">Rankings</TabsTrigger>
          <TabsTrigger value="comparison">Comparison</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="rankings" className="space-y-6">
          {/* Top 3 Winners */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5 text-yellow-600" />
                Top Performers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {rankings.slice(0, 3).map((vendor) => (
                  <div
                    key={vendor.proposal_id}
                    className={`p-6 rounded-lg border-2 ${
                      vendor.rank_position === 1 
                        ? 'border-yellow-300 bg-yellow-50' 
                        : vendor.rank_position === 2
                        ? 'border-gray-300 bg-gray-50'
                        : 'border-orange-300 bg-orange-50'
                    }`}
                  >
                    <div className="text-center space-y-4">
                      <div className="flex justify-center">
                        {getRankIcon(vendor.rank_position)}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{vendor.vendor_name}</h3>
                        <p className="text-sm text-gray-600">Rank #{vendor.rank_position}</p>
                      </div>
                      <div className="text-center">
                        <div className={`text-3xl font-bold ${getScoreColor(vendor.overall_score)}`}>
                          {Math.round(vendor.overall_score)}%
                        </div>
                        <p className="text-sm text-gray-600">Overall Score</p>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="text-center">
                          <div className="text-green-600 font-semibold">{vendor.compliance_distribution.compliant}</div>
                          <div className="text-gray-600">Compliant</div>
                        </div>
                        <div className="text-center">
                          <div className="text-yellow-600 font-semibold">{vendor.compliance_distribution.partial}</div>
                          <div className="text-gray-600">Partial</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Detailed Rankings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Complete Rankings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {rankings.map((vendor) => (
                  <div
                    key={vendor.proposal_id}
                    className="p-6 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <Badge className={`flex items-center gap-1 ${getRankBadgeColor(vendor.rank_position)}`}>
                          {getRankIcon(vendor.rank_position)}
                          #{vendor.rank_position}
                        </Badge>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{vendor.vendor_name}</h3>
                          <p className="text-sm text-gray-600">
                            {vendor.compliance_distribution.compliant} compliant • {' '}
                            {vendor.compliance_distribution.partial} partial • {' '}
                            {vendor.compliance_distribution.non_compliant + vendor.compliance_distribution.not_addressed} gaps
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${getScoreColor(vendor.overall_score)}`}>
                          {Math.round(vendor.overall_score)}%
                        </div>
                        <p className="text-sm text-gray-600">Overall Score</p>
                      </div>
                    </div>

                    {/* Category Scores */}
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
                      {Object.entries(vendor.category_scores).map(([category, score]) => (
                        score !== undefined && score !== null && (
                          <div key={category} className="text-center">
                            <div className={`text-lg font-semibold ${getScoreColor(score)}`}>
                              {Math.round(score)}%
                            </div>
                            <div className="text-xs text-gray-600 mb-2">
                              {categoryLabels[category as keyof typeof categoryLabels]}
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${getScoreBarColor(score)}`}
                                style={{ width: `${score}%` }}
                              />
                            </div>
                          </div>
                        )
                      ))}
                    </div>

                    {/* Strengths and Weaknesses */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                          Strengths
                        </h4>
                        <ul className="space-y-1">
                          {vendor.strengths.slice(0, 3).map((strength, index) => (
                            <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                              <span className="text-green-500 mt-1">•</span>
                              {strength}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-yellow-600" />
                          Areas for Improvement
                        </h4>
                        <ul className="space-y-1">
                          {vendor.weaknesses.slice(0, 3).map((weakness, index) => (
                            <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                              <span className="text-yellow-500 mt-1">•</span>
                              {weakness}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Comparison Checkbox */}
                    <div className="mt-4 pt-4 border-t">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedVendors.includes(vendor.proposal_id)}
                          onChange={() => toggleVendorComparison(vendor.proposal_id)}
                          disabled={!selectedVendors.includes(vendor.proposal_id) && selectedVendors.length >= 3}
                          className="rounded"
                        />
                        <span className="text-sm text-gray-600">
                          Add to comparison {selectedVendors.length >= 3 && !selectedVendors.includes(vendor.proposal_id) && '(max 3)'}
                        </span>
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comparison" className="space-y-6">
          {comparisonVendors.length === 0 ? (
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Vendors Selected</h3>
                  <p className="text-gray-600 mb-4">
                    Select vendors from the Rankings tab to compare their performance side-by-side.
                  </p>
                  <Button onClick={() => document.querySelector('[value="rankings"]')?.click()}>
                    Go to Rankings
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Vendor Comparison ({comparisonVendors.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3 font-medium">Metric</th>
                        {comparisonVendors.map(vendor => (
                          <th key={vendor.proposal_id} className="text-center p-3 font-medium">
                            <div>
                              <div className="font-semibold">{vendor.vendor_name}</div>
                              <Badge className={`mt-1 ${getRankBadgeColor(vendor.rank_position)}`}>
                                #{vendor.rank_position}
                              </Badge>
                            </div>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b">
                        <td className="p-3 font-medium">Overall Score</td>
                        {comparisonVendors.map(vendor => (
                          <td key={vendor.proposal_id} className="text-center p-3">
                            <span className={`text-lg font-bold ${getScoreColor(vendor.overall_score)}`}>
                              {Math.round(vendor.overall_score)}%
                            </span>
                          </td>
                        ))}
                      </tr>
                      {Object.entries(categoryLabels).map(([key, label]) => (
                        <tr key={key} className="border-b">
                          <td className="p-3 font-medium">{label}</td>
                          {comparisonVendors.map(vendor => {
                            const score = vendor.category_scores[key as keyof typeof vendor.category_scores];
                            return (
                              <td key={vendor.proposal_id} className="text-center p-3">
                                {score !== undefined && score !== null ? (
                                  <span className={`font-semibold ${getScoreColor(score)}`}>
                                    {Math.round(score)}%
                                  </span>
                                ) : (
                                  <span className="text-gray-400">N/A</span>
                                )}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                      <tr className="border-b">
                        <td className="p-3 font-medium">Compliant</td>
                        {comparisonVendors.map(vendor => (
                          <td key={vendor.proposal_id} className="text-center p-3">
                            <span className="text-green-600 font-semibold">
                              {vendor.compliance_distribution.compliant}
                            </span>
                          </td>
                        ))}
                      </tr>
                      <tr className="border-b">
                        <td className="p-3 font-medium">Partial</td>
                        {comparisonVendors.map(vendor => (
                          <td key={vendor.proposal_id} className="text-center p-3">
                            <span className="text-yellow-600 font-semibold">
                              {vendor.compliance_distribution.partial}
                            </span>
                          </td>
                        ))}
                      </tr>
                      <tr className="border-b">
                        <td className="p-3 font-medium">Gaps</td>
                        {comparisonVendors.map(vendor => (
                          <td key={vendor.proposal_id} className="text-center p-3">
                            <span className="text-red-600 font-semibold">
                              {vendor.compliance_distribution.non_compliant + vendor.compliance_distribution.not_addressed}
                            </span>
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Insights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Overall Market Analysis */}
              <div>
                <h4 className="font-medium mb-3">Market Analysis</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {rankings.length > 0 ? Math.round(rankings.reduce((sum, vendor) => sum + vendor.overall_score, 0) / rankings.length) : 0}%
                    </div>
                    <div className="text-sm text-gray-600">Average Score</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {rankings.length > 0 ? Math.round(Math.max(...rankings.map(v => v.overall_score))) : 0}%
                    </div>
                    <div className="text-sm text-gray-600">Highest Score</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {rankings.length > 0 ? Math.round(Math.max(...rankings.map(v => v.overall_score)) - Math.min(...rankings.map(v => v.overall_score))) : 0}%
                    </div>
                    <div className="text-sm text-gray-600">Score Range</div>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Common Patterns */}
              <div>
                <h4 className="font-medium mb-3">Common Patterns</h4>
                <div className="space-y-4">
                  <div>
                    <h5 className="text-sm font-medium text-gray-900 mb-2">Most Common Strengths</h5>
                    <div className="flex flex-wrap gap-2">
                      {/* This would be calculated from actual data */}
                      <Badge variant="outline">Strong technical capabilities</Badge>
                      <Badge variant="outline">Good functional coverage</Badge>
                      <Badge variant="outline">Competitive commercial terms</Badge>
                    </div>
                  </div>
                  <div>
                    <h5 className="text-sm font-medium text-gray-900 mb-2">Common Improvement Areas</h5>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="outline">Legal compliance gaps</Badge>
                      <Badge variant="outline">Operational details needed</Badge>
                      <Badge variant="outline">Security requirements unclear</Badge>
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Recommendations */}
              <div>
                <h4 className="font-medium mb-3">Overall Recommendations</h4>
                <div className="space-y-3">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h5 className="font-medium text-blue-900 mb-2">Vendor Selection</h5>
                    <p className="text-sm text-blue-800">
                      Consider the top 3 performers for detailed negotiations. Focus on addressing identified gaps through clarification requests.
                    </p>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h5 className="font-medium text-yellow-900 mb-2">Due Diligence</h5>
                    <p className="text-sm text-yellow-800">
                      Request additional documentation for areas marked as "partial" or "not addressed" before making final decisions.
                    </p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h5 className="font-medium text-green-900 mb-2">Negotiation Focus</h5>
                    <p className="text-sm text-green-800">
                      Use the compliance analysis results to negotiate specific improvements and guarantees in final contracts.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default VendorRankingsPage;