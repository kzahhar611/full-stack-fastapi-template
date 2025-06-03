'use client'

import React, { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Button from '@/components/common/Button'
import FileUpload from '@/components/common/FileUpload'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import Select from '@/components/common/Select'
import { rfpService } from '@/services/rfp'
import { RFPDocument } from '@/types/rfp'
import { 
  ArrowLeftIcon,
  DocumentIcon,
  TrashIcon,
  CloudArrowDownIcon,
  EyeIcon
} from '@heroicons/react/24/outline'

const DocumentsPage: React.FC = () => {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const rfpId = parseInt(params.id as string)

  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [documentType, setDocumentType] = useState('')

  // Fetch RFP documents
  const { data: documents, isLoading } = useQuery(
    ['rfp-documents', rfpId],
    () => rfpService.getRFPDocuments(rfpId),
    {
      enabled: !!rfpId,
    }
  )

  // Upload mutation
  const uploadMutation = useMutation(
    ({ file, type }: { file: File; type?: string }) => 
      rfpService.uploadRFPDocument(rfpId, file, type),
    {
      onSuccess: () => {
        toast.success('Document uploaded successfully!')
        queryClient.invalidateQueries(['rfp-documents', rfpId])
        setSelectedFiles([])
        setDocumentType('')
      },
      onError: (error: any) => {
        console.error('Upload failed:', error)
        toast.error('Failed to upload document')
      }
    }
  )

  // Delete mutation
  const deleteMutation = useMutation(
    (documentId: number) => rfpService.deleteRFPDocument(rfpId, documentId),
    {
      onSuccess: () => {
        toast.success('Document deleted successfully!')
        queryClient.invalidateQueries(['rfp-documents', rfpId])
      },
      onError: () => {
        toast.error('Failed to delete document')
      }
    }
  )

  const documentTypeOptions = [
    { value: '', label: 'Select document type (optional)' },
    { value: 'requirements', label: 'Requirements' },
    { value: 'specifications', label: 'Technical Specifications' },
    { value: 'drawings', label: 'Drawings/Blueprints' },
    { value: 'references', label: 'Reference Documents' },
    { value: 'terms', label: 'Terms & Conditions' },
    { value: 'proposal_template', label: 'Proposal Template' },
    { value: 'other', label: 'Other' },
  ]

  const handleFileSelect = (file: File) => {
    setSelectedFiles(prev => [...prev, file])
  }

  const handleFileRemove = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select at least one file')
      return
    }

    setUploading(true)
    
    try {
      for (const file of selectedFiles) {
        await uploadMutation.mutateAsync({ 
          file, 
          type: documentType || undefined 
        })
      }
    } catch (error) {
      // Error handling is done in the mutation
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = (documentId: number, fileName: string) => {
    if (confirm(`Are you sure you want to delete "${fileName}"?`)) {
      deleteMutation.mutate(documentId)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    switch (extension) {
      case 'pdf':
        return '📄'
      case 'doc':
      case 'docx':
        return '📝'
      case 'xls':
      case 'xlsx':
        return '📊'
      case 'ppt':
      case 'pptx':
        return '📺'
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return '🖼️'
      default:
        return '📎'
    }
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={() => router.back()}
              leftIcon={<ArrowLeftIcon className="h-5 w-5" />}
            >
              Back to RFP
            </Button>
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Document Management</h1>
              <p className="mt-1 text-sm text-gray-600">
                Upload and manage documents for this RFP.
              </p>
            </div>
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Documents</h2>
          
          <div className="space-y-4">
            <Select
              label="Document Type"
              options={documentTypeOptions}
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              helpText="Categorize your document for better organization"
            />

            <FileUpload
              onFileSelect={handleFileSelect}
              onFileRemove={handleFileRemove}
              selectedFiles={selectedFiles}
              multiple={true}
            />

            {selectedFiles.length > 0 && (
              <div className="flex justify-end">
                <Button
                  onClick={handleUpload}
                  loading={uploading}
                  leftIcon={<CloudArrowDownIcon className="h-5 w-5" />}
                >
                  Upload {selectedFiles.length} File{selectedFiles.length !== 1 ? 's' : ''}
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Documents List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              Uploaded Documents ({documents?.length || 0})
            </h2>
          </div>

          {documents && documents.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {documents.map((document) => (
                <div key={document.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <span className="text-3xl">{getFileIcon(document.filename)}</span>
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">
                          {document.original_filename}
                        </h3>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                          <span>{formatFileSize(document.file_size)}</span>
                          <span>{document.content_type}</span>
                          {document.document_type && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {document.document_type}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-400 mt-1">
                          Uploaded {new Date(document.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${document.processing_status === 'uploaded' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                        }`}>
                        {document.processing_status}
                      </span>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          // In a real app, this would download the file
                          toast.info('Download functionality would be implemented here')
                        }}
                        leftIcon={<CloudArrowDownIcon className="h-4 w-4" />}
                      >
                        Download
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(document.id, document.original_filename)}
                        loading={deleteMutation.isLoading}
                        leftIcon={<TrashIcon className="h-4 w-4" />}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
              <p className="mt-1 text-sm text-gray-500">
                Upload your first document to get started.
              </p>
            </div>
          )}
        </div>

        {/* Upload Tips */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Upload Tips</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Supported formats: PDF, DOC, DOCX, TXT, XLS, XLSX, PPT, PPTX, JPG, PNG, GIF</li>
            <li>• Maximum file size: 10MB per file</li>
            <li>• You can upload multiple files at once</li>
            <li>• Categorizing documents helps with organization</li>
            <li>• Documents are automatically scanned for security</li>
          </ul>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default DocumentsPage