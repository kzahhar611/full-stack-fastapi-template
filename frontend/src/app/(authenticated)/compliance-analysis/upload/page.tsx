"use client";

import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle, AlertCircle, ArrowLeft, Plus } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

const ComplianceAnalysisUploadPage = () => {
  const router = useRouter();
  const [rfpFile, setRfpFile] = useState<UploadedFile | null>(null);
  const [proposalFiles, setProposalFiles] = useState<UploadedFile[]>([]);
  const [analysisName, setAnalysisName] = useState('');
  const [companyContext, setCompanyContext] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const maxProposals = 10;
  const supportedFormats = ['pdf', 'docx', 'doc', 'txt'];

  const validateFile = (file: File): string | null => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (!extension || !supportedFormats.includes(extension)) {
      return `Unsupported file format. Please use: ${supportedFormats.join(', ')}`;
    }
    if (file.size > 50 * 1024 * 1024) { // 50MB limit
      return 'File size must be less than 50MB';
    }
    return null;
  };

  const createUploadedFile = (file: File): UploadedFile => ({
    file,
    id: Math.random().toString(36).substr(2, 9),
    progress: 0,
    status: 'pending'
  });

  // RFP File Upload
  const onRfpDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    const validationError = validateFile(file);
    
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setError(null);
    setRfpFile(createUploadedFile(file));
  }, []);

  const rfpDropzone = useDropzone({
    onDrop: onRfpDrop,
    multiple: false,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt']
    }
  });

  // Proposal Files Upload
  const onProposalDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = [];
    const errors: string[] = [];

    acceptedFiles.forEach(file => {
      if (proposalFiles.length + newFiles.length >= maxProposals) {
        errors.push(`Maximum ${maxProposals} proposal files allowed`);
        return;
      }

      const validationError = validateFile(file);
      if (validationError) {
        errors.push(`${file.name}: ${validationError}`);
        return;
      }

      newFiles.push(createUploadedFile(file));
    });

    if (errors.length > 0) {
      setError(errors.join(', '));
    } else {
      setError(null);
    }

    if (newFiles.length > 0) {
      setProposalFiles(prev => [...prev, ...newFiles]);
    }
  }, [proposalFiles.length]);

  const proposalDropzone = useDropzone({
    onDrop: onProposalDrop,
    multiple: true,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt']
    }
  });

  const removeRfpFile = () => {
    setRfpFile(null);
  };

  const removeProposalFile = (id: string) => {
    setProposalFiles(prev => prev.filter(file => file.id !== id));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    return <FileText className="h-6 w-6 text-blue-600" />;
  };

  const handleSubmit = async () => {
    if (!rfpFile) {
      setError('Please upload an RFP document');
      return;
    }

    if (proposalFiles.length === 0) {
      setError('Please upload at least one vendor proposal');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('rfp_file', rfpFile.file);
      formData.append('analysis_name', analysisName || rfpFile.file.name);
      formData.append('company_context', companyContext);

      proposalFiles.forEach((proposalFile) => {
        formData.append('proposal_files', proposalFile.file);
      });

      const response = await fetch('/api/v1/compliance-analysis/upload', {
        method: 'POST',
        body: formData,
      });

      setUploadProgress(100);

      if (response.ok) {
        const result = await response.json();
        router.push(`/compliance-analysis/results/${result.id}`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Upload failed');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const canSubmit = rfpFile && proposalFiles.length > 0 && !isUploading;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => router.back()}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Upload Documents for Compliance Analysis</h1>
          <p className="text-gray-600 mt-2">
            Upload your RFP document and vendor proposals to start AI-powered compliance assessment
          </p>
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-8">
        {/* Analysis Information */}
        <Card>
          <CardHeader>
            <CardTitle>Analysis Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="analysis-name">Analysis Name (Optional)</Label>
              <Input
                id="analysis-name"
                placeholder="Enter a name for this analysis"
                value={analysisName}
                onChange={(e) => setAnalysisName(e.target.value)}
                className="mt-1"
              />
              <p className="text-sm text-gray-500 mt-1">
                Leave blank to use RFP document name
              </p>
            </div>
            <div>
              <Label htmlFor="company-context">Company Context (Optional)</Label>
              <Textarea
                id="company-context"
                placeholder="Provide context about your company, industry, or specific requirements that should be considered during analysis..."
                value={companyContext}
                onChange={(e) => setCompanyContext(e.target.value)}
                className="mt-1"
                rows={3}
              />
              <p className="text-sm text-gray-500 mt-1">
                This information helps the AI provide more relevant analysis
              </p>
            </div>
          </CardContent>
        </Card>

        {/* RFP Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              RFP Document
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!rfpFile ? (
              <div
                {...rfpDropzone.getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  rfpDropzone.isDragActive 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...rfpDropzone.getInputProps()} />
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Upload RFP Document
                </h3>
                <p className="text-gray-600 mb-4">
                  Drag and drop your RFP document here, or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Supported formats: PDF, DOCX, DOC, TXT (max 50MB)
                </p>
              </div>
            ) : (
              <div className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getFileIcon(rfpFile.file.name)}
                    <div>
                      <p className="font-medium text-gray-900">{rfpFile.file.name}</p>
                      <p className="text-sm text-gray-500">{formatFileSize(rfpFile.file.size)}</p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={removeRfpFile}
                    className="flex items-center gap-2"
                  >
                    <X className="h-4 w-4" />
                    Remove
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Proposal Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Vendor Proposals ({proposalFiles.length}/{maxProposals})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {proposalFiles.length > 0 && (
              <div className="space-y-3">
                {proposalFiles.map((file) => (
                  <div key={file.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getFileIcon(file.file.name)}
                        <div>
                          <p className="font-medium text-gray-900">{file.file.name}</p>
                          <p className="text-sm text-gray-500">{formatFileSize(file.file.size)}</p>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeProposalFile(file.id)}
                        className="flex items-center gap-2"
                      >
                        <X className="h-4 w-4" />
                        Remove
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {proposalFiles.length < maxProposals && (
              <div
                {...proposalDropzone.getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  proposalDropzone.isDragActive 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...proposalDropzone.getInputProps()} />
                <Plus className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Add Vendor Proposals
                </h3>
                <p className="text-gray-600 mb-4">
                  Drag and drop proposal documents here, or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Upload multiple files at once. Supported formats: PDF, DOCX, DOC, TXT (max 50MB each)
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Upload Progress */}
        {isUploading && (
          <Card>
            <CardHeader>
              <CardTitle>Uploading and Processing</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Progress value={uploadProgress} />
              <p className="text-sm text-gray-600">
                {uploadProgress < 100 
                  ? 'Uploading documents and extracting content...'
                  : 'Upload complete. Starting analysis...'
                }
              </p>
            </CardContent>
          </Card>
        )}

        {/* Submit Button */}
        <div className="flex justify-end gap-4">
          <Button 
            variant="outline" 
            onClick={() => router.back()}
            disabled={isUploading}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="flex items-center gap-2"
          >
            {isUploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Processing...
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4" />
                Start Analysis
              </>
            )}
          </Button>
        </div>

        {/* Help Text */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Analysis Process:</strong> After uploading, the AI will extract requirements from your RFP, 
            analyze each vendor proposal for compliance, generate scoring matrices, and provide vendor rankings 
            with gap analysis. This typically takes 1-3 minutes depending on document size and complexity.
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
};

export default ComplianceAnalysisUploadPage;