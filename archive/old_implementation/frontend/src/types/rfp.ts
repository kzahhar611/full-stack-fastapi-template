export enum RFPStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  UNDER_REVIEW = 'under_review',
  CLOSED = 'closed',
  AWARDED = 'awarded',
  CANCELLED = 'cancelled'
}

export enum RFPType {
  REQUEST_FOR_PROPOSAL = 'rfp',
  REQUEST_FOR_QUOTATION = 'rfq',
  INVITATION_TO_BID = 'itb',
  REQUEST_FOR_INFORMATION = 'rfi'
}

export interface RFP {
  id: number
  title: string
  rfp_number: string
  description?: string
  rfp_type: RFPType
  status: RFPStatus
  estimated_budget?: number
  currency: string
  submission_deadline?: string
  evaluation_period?: number
  project_start_date?: string
  project_end_date?: string
  technical_requirements?: Record<string, any>
  evaluation_criteria?: Record<string, any>
  compliance_requirements?: Record<string, any>
  organization?: string
  contact_person?: string
  contact_email?: string
  contact_phone?: string
  issue_date?: string
  award_date?: string
  complexity_score?: number
  risk_assessment?: Record<string, any>
  go_no_go_recommendation?: string
  ai_analysis_summary?: string
  key_insights?: Record<string, any>
  created_by: number
  created_at: string
  updated_at: string
}

export interface RFPListItem {
  id: number
  title: string
  rfp_number: string
  status: RFPStatus
  rfp_type: RFPType
  estimated_budget?: number
  currency: string
  submission_deadline?: string
  organization?: string
  created_at: string
}

export interface CreateRFPData {
  title: string
  description?: string
  rfp_type: RFPType
  estimated_budget?: number
  currency?: string
  submission_deadline?: string
  evaluation_period?: number
  project_start_date?: string
  project_end_date?: string
  technical_requirements?: Record<string, any>
  evaluation_criteria?: Record<string, any>
  compliance_requirements?: Record<string, any>
  organization?: string
  contact_person?: string
  contact_email?: string
  contact_phone?: string
}

export interface UpdateRFPData extends Partial<CreateRFPData> {}

export interface RFPDocument {
  id: number
  filename: string
  original_filename: string
  file_size: number
  content_type: string
  document_type?: string
  processing_status: string
  created_at: string
}

export interface RFPAnalysisRequest {
  analyze_complexity?: boolean
  analyze_risks?: boolean
  generate_recommendations?: boolean
  custom_criteria?: Record<string, any>
}

export interface RFPAnalysisResponse {
  complexity_score?: number
  risk_assessment?: Record<string, any>
  go_no_go_recommendation?: string
  analysis_summary: string
  key_insights: Record<string, any>
  confidence_score?: number
  processing_time: number
}

export interface RFPFilters {
  status?: RFPStatus
  search?: string
  my_rfps?: boolean
  order_by?: string
  order_direction?: 'asc' | 'desc'
}