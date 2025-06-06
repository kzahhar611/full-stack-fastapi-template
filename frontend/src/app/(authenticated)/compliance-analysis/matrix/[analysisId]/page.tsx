"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowLeft, Filter, Download, Search, SortAsc, SortDesc, Eye, AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ComplianceMatrixEntry {
  id: string;
  requirement_id: string;
  proposal_id: string;
  requirement_text: string;
  requirement_type: 'TECHNICAL' | 'FUNCTIONAL' | 'COMMERCIAL' | 'LEGAL' | 'OPERATIONAL';
  vendor_name: string;
  compliance_status: 'COMPLIANT' | 'PARTIAL' | 'NON_COMPLIANT' | 'NOT_ADDRESSED';
  compliance_score: number;
  evidence_text?: string;
  gap_description?: string;
  recommendations?: string;
  keywords_matched?: string[];
}

interface FilterState {
  vendor: string;
  status: string;
  type: string;
  search: string;
}

interface SortState {
  field: 'score' | 'status' | 'vendor' | 'requirement';
  direction: 'asc' | 'desc';
}

const ComplianceMatrixPage = () => {
  const router = useRouter();
  const params = useParams();
  const analysisId = params.analysisId as string;

  const [matrix, setMatrix] = useState<ComplianceMatrixEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [filters, setFilters] = useState<FilterState>({
    vendor: 'all',
    status: 'all',
    type: 'all',
    search: ''
  });
  
  const [sort, setSort] = useState<SortState>({
    field: 'score',
    direction: 'desc'
  });

  const [selectedEntry, setSelectedEntry] = useState<ComplianceMatrixEntry | null>(null);

  useEffect(() => {
    fetchComplianceMatrix();
  }, [analysisId]);

  const fetchComplianceMatrix = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/compliance-analysis/matrix/${analysisId}`);
      if (response.ok) {
        const data = await response.json();
        setMatrix(data);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load compliance matrix');
      }
    } catch (err) {
      console.error('Error fetching compliance matrix:', err);
      setError('Failed to load compliance matrix');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLIANT': return 'bg-green-100 text-green-800 border-green-200';
      case 'PARTIAL': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'NON_COMPLIANT': return 'bg-red-100 text-red-800 border-red-200';
      case 'NOT_ADDRESSED': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLIANT': return <CheckCircle className="h-4 w-4" />;
      case 'PARTIAL': return <AlertTriangle className="h-4 w-4" />;
      case 'NON_COMPLIANT': return <XCircle className="h-4 w-4" />;
      case 'NOT_ADDRESSED': return <Clock className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 font-semibold';
    if (score >= 60) return 'text-yellow-600 font-semibold';
    if (score >= 40) return 'text-orange-600 font-semibold';
    return 'text-red-600 font-semibold';
  };

  const filteredAndSortedMatrix = React.useMemo(() => {
    let filtered = matrix.filter(entry => {
      const matchesVendor = filters.vendor === 'all' || entry.vendor_name === filters.vendor;
      const matchesStatus = filters.status === 'all' || entry.compliance_status === filters.status;
      const matchesType = filters.type === 'all' || entry.requirement_type === filters.type;
      const matchesSearch = filters.search === '' || 
        entry.requirement_text.toLowerCase().includes(filters.search.toLowerCase()) ||
        entry.vendor_name.toLowerCase().includes(filters.search.toLowerCase());
      
      return matchesVendor && matchesStatus && matchesType && matchesSearch;
    });

    // Sort the filtered results
    filtered.sort((a, b) => {
      let aValue: any = a[sort.field];
      let bValue: any = b[sort.field];

      if (sort.field === 'score') {
        aValue = a.compliance_score;
        bValue = b.compliance_score;
      } else if (sort.field === 'status') {
        aValue = a.compliance_status;
        bValue = b.compliance_status;
      } else if (sort.field === 'vendor') {
        aValue = a.vendor_name;
        bValue = b.vendor_name;
      } else if (sort.field === 'requirement') {
        aValue = a.requirement_text;
        bValue = b.requirement_text;
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (sort.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return filtered;
  }, [matrix, filters, sort]);

  const handleSort = (field: SortState['field']) => {
    setSort(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const uniqueVendors = Array.from(new Set(matrix.map(entry => entry.vendor_name)));
  const uniqueTypes = Array.from(new Set(matrix.map(entry => entry.requirement_type)));

  const getSortIcon = (field: SortState['field']) => {
    if (sort.field !== field) return null;
    return sort.direction === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />;
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
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
          <h1 className="text-3xl font-bold text-gray-900">Compliance Matrix</h1>
          <p className="text-gray-600 mt-2">
            Detailed requirement vs vendor proposal compliance analysis
          </p>
        </div>
        <Button 
          variant="outline"
          className="flex items-center gap-2"
          onClick={() => window.open(`/api/v1/documents/generate/analysis/${analysisId}/pdf`, '_blank')}
        >
          <Download className="h-4 w-4" />
          Export Matrix
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search requirements or vendors..."
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Vendor</label>
              <Select value={filters.vendor} onValueChange={(value) => setFilters(prev => ({ ...prev, vendor: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="All vendors" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Vendors</SelectItem>
                  {uniqueVendors.map(vendor => (
                    <SelectItem key={vendor} value={vendor}>{vendor}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Status</label>
              <Select value={filters.status} onValueChange={(value) => setFilters(prev => ({ ...prev, status: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="COMPLIANT">Compliant</SelectItem>
                  <SelectItem value="PARTIAL">Partial</SelectItem>
                  <SelectItem value="NON_COMPLIANT">Non-Compliant</SelectItem>
                  <SelectItem value="NOT_ADDRESSED">Not Addressed</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Type</label>
              <Select value={filters.type} onValueChange={(value) => setFilters(prev => ({ ...prev, type: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {uniqueTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Summary */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>
          Showing {filteredAndSortedMatrix.length} of {matrix.length} compliance assessments
        </span>
        <div className="flex items-center gap-4">
          <span>Sort by:</span>
          <div className="flex gap-2">
            {(['score', 'status', 'vendor', 'requirement'] as const).map(field => (
              <Button
                key={field}
                variant={sort.field === field ? "default" : "outline"}
                size="sm"
                onClick={() => handleSort(field)}
                className="flex items-center gap-1"
              >
                {field.charAt(0).toUpperCase() + field.slice(1)}
                {getSortIcon(field)}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Compliance Matrix Table */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Assessment Matrix</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-medium">Requirement</th>
                  <th className="text-left p-3 font-medium">Type</th>
                  <th className="text-left p-3 font-medium">Vendor</th>
                  <th className="text-left p-3 font-medium">Status</th>
                  <th className="text-left p-3 font-medium">Score</th>
                  <th className="text-left p-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredAndSortedMatrix.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-12 text-gray-500">
                      No compliance assessments match your filters
                    </td>
                  </tr>
                ) : (
                  filteredAndSortedMatrix.map((entry) => (
                    <tr key={entry.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">
                        <div className="max-w-md">
                          <p className="font-medium text-gray-900">
                            {entry.requirement_text.length > 100 
                              ? `${entry.requirement_text.substring(0, 100)}...`
                              : entry.requirement_text
                            }
                          </p>
                        </div>
                      </td>
                      <td className="p-3">
                        <Badge variant="outline">
                          {entry.requirement_type}
                        </Badge>
                      </td>
                      <td className="p-3">
                        <span className="font-medium text-gray-900">
                          {entry.vendor_name}
                        </span>
                      </td>
                      <td className="p-3">
                        <Badge className={`flex items-center gap-1 ${getStatusColor(entry.compliance_status)}`}>
                          {getStatusIcon(entry.compliance_status)}
                          {entry.compliance_status.replace('_', ' ')}
                        </Badge>
                      </td>
                      <td className="p-3">
                        <span className={getScoreColor(entry.compliance_score)}>
                          {Math.round(entry.compliance_score)}%
                        </span>
                      </td>
                      <td className="p-3">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setSelectedEntry(entry)}
                              className="flex items-center gap-2"
                            >
                              <Eye className="h-4 w-4" />
                              Details
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                            <DialogHeader>
                              <DialogTitle>Compliance Assessment Details</DialogTitle>
                            </DialogHeader>
                            {selectedEntry && (
                              <div className="space-y-6">
                                {/* Requirement Details */}
                                <div>
                                  <h4 className="font-medium mb-2">Requirement</h4>
                                  <div className="bg-gray-50 p-4 rounded-lg">
                                    <p className="text-gray-900">{selectedEntry.requirement_text}</p>
                                    <div className="flex items-center gap-4 mt-2">
                                      <Badge variant="outline">{selectedEntry.requirement_type}</Badge>
                                    </div>
                                  </div>
                                </div>

                                {/* Vendor & Assessment */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div>
                                    <h4 className="font-medium mb-2">Vendor</h4>
                                    <p className="text-lg font-semibold text-gray-900">{selectedEntry.vendor_name}</p>
                                  </div>
                                  <div>
                                    <h4 className="font-medium mb-2">Assessment</h4>
                                    <div className="flex items-center gap-3">
                                      <Badge className={`flex items-center gap-1 ${getStatusColor(selectedEntry.compliance_status)}`}>
                                        {getStatusIcon(selectedEntry.compliance_status)}
                                        {selectedEntry.compliance_status.replace('_', ' ')}
                                      </Badge>
                                      <span className={`text-lg ${getScoreColor(selectedEntry.compliance_score)}`}>
                                        {Math.round(selectedEntry.compliance_score)}%
                                      </span>
                                    </div>
                                  </div>
                                </div>

                                <Separator />

                                {/* Evidence */}
                                {selectedEntry.evidence_text && (
                                  <div>
                                    <h4 className="font-medium mb-2">Evidence Found</h4>
                                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                                      <p className="text-gray-900">{selectedEntry.evidence_text}</p>
                                    </div>
                                  </div>
                                )}

                                {/* Gap Analysis */}
                                {selectedEntry.gap_description && (
                                  <div>
                                    <h4 className="font-medium mb-2">Gap Analysis</h4>
                                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                                      <p className="text-gray-900">{selectedEntry.gap_description}</p>
                                    </div>
                                  </div>
                                )}

                                {/* Recommendations */}
                                {selectedEntry.recommendations && (
                                  <div>
                                    <h4 className="font-medium mb-2">Recommendations</h4>
                                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                                      <p className="text-gray-900">{selectedEntry.recommendations}</p>
                                    </div>
                                  </div>
                                )}

                                {/* Keywords Matched */}
                                {selectedEntry.keywords_matched && selectedEntry.keywords_matched.length > 0 && (
                                  <div>
                                    <h4 className="font-medium mb-2">Keywords Matched</h4>
                                    <div className="flex flex-wrap gap-2">
                                      {selectedEntry.keywords_matched.map((keyword, index) => (
                                        <Badge key={index} variant="secondary">
                                          {keyword}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </DialogContent>
                        </Dialog>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ComplianceMatrixPage;