import api, { createFormData } from './api'
import { 
  RFP, 
  RFPListItem, 
  CreateRFPData, 
  UpdateRFPData, 
  RFPDocument, 
  RFPAnalysisRequest, 
  RFPAnalysisResponse,
  RFPStatus,
  RFPFilters 
} from '@/types/rfp'

export const rfpService = {
  async getRFPs(params: RFPFilters & { skip?: number; limit?: number } = {}): Promise<RFPListItem[]> {
    const response = await api.get<RFPListItem[]>('/rfps/', { params })
    return response.data
  },

  async getRFP(id: number): Promise<RFP> {
    const response = await api.get<RFP>(`/rfps/${id}`)
    return response.data
  },

  async createRFP(data: CreateRFPData): Promise<RFP> {
    const response = await api.post<RFP>('/rfps/', data)
    return response.data
  },

  async updateRFP(id: number, data: UpdateRFPData): Promise<RFP> {
    const response = await api.put<RFP>(`/rfps/${id}`, data)
    return response.data
  },

  async updateRFPStatus(id: number, status: RFPStatus): Promise<RFP> {
    const response = await api.put<RFP>(`/rfps/${id}/status`, { status })
    return response.data
  },

  async deleteRFP(id: number): Promise<void> {
    await api.delete(`/rfps/${id}`)
  },

  async analyzeRFP(id: number, request: RFPAnalysisRequest): Promise<RFPAnalysisResponse> {
    const response = await api.post<RFPAnalysisResponse>(`/rfps/${id}/analyze`, request)
    return response.data
  },

  async getRFPDocuments(id: number): Promise<RFPDocument[]> {
    const response = await api.get<RFPDocument[]>(`/rfps/${id}/documents`)
    return response.data
  },

  async uploadRFPDocument(
    rfpId: number, 
    file: File, 
    documentType?: string
  ): Promise<RFPDocument> {
    const formData = createFormData({
      file,
      document_type: documentType
    })

    const response = await api.post<RFPDocument>(
      `/rfps/${rfpId}/documents`, 
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  },

  async deleteRFPDocument(rfpId: number, documentId: number): Promise<void> {
    await api.delete(`/rfps/${rfpId}/documents/${documentId}`)
  }
}