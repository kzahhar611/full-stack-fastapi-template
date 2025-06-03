import api, { createFormData } from './api'
import { 
  Proposal, 
  ProposalListItem, 
  CreateProposalData, 
  UpdateProposalData, 
  ProposalDocument, 
  ProposalEvaluationRequest, 
  ProposalEvaluationResponse,
  ProposalStatus,
  ProposalFilters 
} from '@/types/proposal'

export const proposalService = {
  async getProposals(params: ProposalFilters & { skip?: number; limit?: number } = {}): Promise<ProposalListItem[]> {
    const response = await api.get<ProposalListItem[]>('/proposals/', { params })
    return response.data
  },

  async getProposal(id: number): Promise<Proposal> {
    const response = await api.get<Proposal>(`/proposals/${id}`)
    return response.data
  },

  async createProposal(data: CreateProposalData): Promise<Proposal> {
    const response = await api.post<Proposal>('/proposals/', data)
    return response.data
  },

  async updateProposal(id: number, data: UpdateProposalData): Promise<Proposal> {
    const response = await api.put<Proposal>(`/proposals/${id}`, data)
    return response.data
  },

  async updateProposalStatus(id: number, status: ProposalStatus): Promise<Proposal> {
    const response = await api.put<Proposal>(`/proposals/${id}/status`, { status })
    return response.data
  },

  async deleteProposal(id: number): Promise<void> {
    await api.delete(`/proposals/${id}`)
  },

  async evaluateProposal(id: number, request: ProposalEvaluationRequest): Promise<ProposalEvaluationResponse> {
    const response = await api.post<ProposalEvaluationResponse>(`/proposals/${id}/evaluate`, request)
    return response.data
  },

  async getProposalDocuments(id: number): Promise<ProposalDocument[]> {
    const response = await api.get<ProposalDocument[]>(`/proposals/${id}/documents`)
    return response.data
  },

  async uploadProposalDocument(
    id: number, 
    file: File, 
    documentType?: string
  ): Promise<ProposalDocument> {
    const formData = createFormData({ file, document_type: documentType })
    const response = await api.post<ProposalDocument>(`/proposals/${id}/documents`, formData)
    return response.data
  },

  async deleteProposalDocument(proposalId: number, documentId: number): Promise<void> {
    await api.delete(`/proposals/${proposalId}/documents/${documentId}`)
  }
}