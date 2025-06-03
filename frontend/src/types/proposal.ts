export type ProposalStatus = 
  | 'draft' 
  | 'in_progress' 
  | 'under_review' 
  | 'submitted' 
  | 'accepted' 
  | 'rejected' 
  | 'withdrawn'

export interface ProposalDocument {
  id: number
  filename: string
  original_filename: string
  file_size: number
  content_type: string
  document_type?: string
  processing_status: string
  created_at: string
}

export interface ProposalListItem {
  id: number
  rfp_id: number
  title: string
  proposal_number: string
  status: ProposalStatus
  total_cost?: number
  currency: string
  delivery_date?: string
  compliance_score?: number
  created_at: string
  updated_at: string
  submitted_at?: string
  rfp_title?: string
  rfp_number?: string
  rfp_organization?: string
}

export interface Proposal {
  id: number
  rfp_id: number
  title: string
  proposal_number: string
  status: ProposalStatus
  executive_summary?: string
  technical_approach?: string
  total_cost?: number
  currency: string
  cost_breakdown?: Record<string, any>
  proposed_timeline?: Record<string, any>
  delivery_date?: string
  compliance_matrix?: Record<string, any>
  compliance_score?: number
  evaluation_results?: Record<string, any>
  strengths?: string[]
  weaknesses?: string[]
  risk_factors?: string[]
  recommendation?: string
  created_by: number
  submitted_at?: string
  created_at: string
  updated_at: string
  rfp_title?: string
  rfp_number?: string
  rfp_organization?: string
  documents: ProposalDocument[]
}

export interface CreateProposalData {
  rfp_id: number
  title: string
  executive_summary?: string
  technical_approach?: string
  total_cost?: number
  currency?: string
  cost_breakdown?: Record<string, any>
  proposed_timeline?: Record<string, any>
  delivery_date?: string
  compliance_matrix?: Record<string, any>
}

export interface UpdateProposalData {
  title?: string
  executive_summary?: string
  technical_approach?: string
  total_cost?: number
  currency?: string
  cost_breakdown?: Record<string, any>
  proposed_timeline?: Record<string, any>
  delivery_date?: string
  compliance_matrix?: Record<string, any>
}

export interface ProposalEvaluationRequest {
  evaluate_technical: boolean
  evaluate_financial: boolean
  evaluate_compliance: boolean
  custom_criteria?: Record<string, number>
}

export interface ProposalEvaluationResponse {
  proposal_id: number
  overall_score: number
  technical_score?: number
  financial_score?: number
  compliance_score?: number
  strengths: string[]
  weaknesses: string[]
  risk_factors: string[]
  recommendation: string
  evaluation_summary: string
  created_at: string
}

export interface ProposalFilters {
  search?: string
  status?: ProposalStatus
  rfp_id?: number
  my_proposals?: boolean
  min_cost?: number
  max_cost?: number
  order_by?: string
  order_direction?: string
}