const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor() {
    this.baseURL = API_BASE_URL
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("access_token")
    }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token")
    }
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: "Network error" }))
      throw new Error(error.error || error.message || "Request failed")
    }

    return response.json()
  }

  // Auth endpoints
  async register(userData: {
    username: string
    email: string
    first_name: string
    last_name: string
    password: string
    confirm_password: string
    role: string
  }) {
    return this.request("/users/v1/register/", {
      method: "POST",
      body: JSON.stringify(userData),
    })
  }

  async login(credentials: { username: string; password: string }) {
    const response = await this.request("/users/v1/login/", {
      method: "POST",
      body: JSON.stringify(credentials),
    })
    if (response.access) {
      this.setToken(response.access)
    }
    return response
  }

  async getProfile() {
    return this.request("/users/v1/profile/")
  }

  // Document endpoints
  async generateDocument(documentData: {
    template_type: string
    prompt: string
    metadata: Record<string, any>
    signer_username: string
    signer_email: string
    signer_first_name: string
    signer_last_name: string
    name?: string
  }) {
    return this.request("/documents/v1/generate/", {
      method: "POST",
      body: JSON.stringify(documentData),
    })
  }

  async getDocuments() {
    return this.request("/documents/v1/list/")
  }

  async getDocumentPDF(id: number) {
    const url = `${this.baseURL}/documents/v1/view/${id}/`
    const headers: HeadersInit = {}

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    return fetch(url, { headers })
  }

  async sendDocumentToSigner(id: number) {
    return this.request(`/documents/v1/send/${id}/`, {
      method: "POST",
    })
  }

  // Signature endpoints
  async signDocument(id: number) {
    return this.request(`/signature/v1/sign/${id}/`, {
      method: "POST",
    })
  }

  async getSignedPDF(id: number) {
    const url = `${this.baseURL}/signature/v1/view/${id}/`
    const headers: HeadersInit = {}

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    return fetch(url, { headers })
  }

  // Summary endpoints
  async generateSummary(id: number) {
    return this.request(`/summary/v1/generate/${id}/`, {
      method: "POST",
    })
  }

  async getSummary(id: number) {
    return this.request(`/summary/v1/view/${id}/`)
  }

  async getSignedStatus(id: number) {
    return this.request(`/signature/v1/status/${id}/`)
  }
}

export const apiClient = new ApiClient()
