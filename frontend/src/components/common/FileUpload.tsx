import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import Button from './Button'
import { 
  CloudArrowUpIcon,
  DocumentIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  onFileRemove?: (index: number) => void
  selectedFiles?: File[]
  accept?: string
  maxSize?: number
  multiple?: boolean
  disabled?: boolean
  className?: string
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  selectedFiles = [],
  accept = '.pdf,.doc,.docx,.txt,.xlsx,.xls,.ppt,.pptx,.jpg,.jpeg,.png,.gif',
  maxSize = 10 * 1024 * 1024, // 10MB
  multiple = true,
  disabled = false,
  className = ''
}) => {
  const [dragActive, setDragActive] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      onFileSelect(file)
    })
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/gif': ['.gif'],
    },
    maxSize,
    multiple,
    disabled
  })

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

  return (
    <div className={className}>
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-primary-400 bg-primary-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        
        <div className="mt-4">
          <p className="text-sm text-gray-600">
            {isDragActive ? (
              'Drop the files here...'
            ) : (
              <>
                <span className="font-medium text-primary-600">Click to upload</span> or drag and drop
              </>
            )}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            PDF, DOC, DOCX, TXT, XLS, XLSX, PPT, PPTX, JPG, PNG, GIF up to {formatFileSize(maxSize)}
          </p>
        </div>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            Selected Files ({selectedFiles.length})
          </h4>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getFileIcon(file.name)}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                
                {onFileRemove && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onFileRemove(index)}
                    leftIcon={<XMarkIcon className="h-4 w-4" />}
                  >
                    Remove
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUpload