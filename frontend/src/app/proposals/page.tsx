'use client'

import React from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Button from '@/components/common/Button'
import { 
  PlusIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

const ProposalsPage: React.FC = () => {
  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="sm:flex sm:items-center">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">Proposals</h1>
            <p className="mt-2 text-sm text-gray-700">
              Manage proposal responses to RFPs and track submission status.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
            <Button
              leftIcon={<PlusIcon className="h-5 w-5" />}
              disabled
            >
              Create Proposal
            </Button>
          </div>
        </div>

        {/* Coming Soon Message */}
        <div className="mt-8 text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Proposal Management Coming Soon</h3>
          <p className="mt-1 text-sm text-gray-500">
            This feature will be available in Phase 4 of the development process.
          </p>
          <p className="mt-2 text-xs text-gray-400">
            Features planned: Proposal creation, submission tracking, evaluation, and AI-powered analysis.
          </p>
        </div>

        {/* Feature Preview */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-4">Planned Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-blue-800">Proposal Creation</h4>
              <ul className="mt-2 text-sm text-blue-700 space-y-1">
                <li>• Response to RFP requirements</li>
                <li>• Technical approach documentation</li>
                <li>• Cost breakdown and timeline</li>
                <li>• Document attachments</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-blue-800">Management & Tracking</h4>
              <ul className="mt-2 text-sm text-blue-700 space-y-1">
                <li>• Submission status tracking</li>
                <li>• Evaluation scoring</li>
                <li>• AI-powered analysis</li>
                <li>• Compliance verification</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default ProposalsPage