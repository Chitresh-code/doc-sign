"use client"

import { useEffect, useState } from "react"
import { useAuth } from "@/contexts/auth-context"
import { apiClient } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Plus, FileText, Download, Send } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

interface Document {
  id: number
  name: string
  document_type: string
  signer_username: string
  created_at: string
  signed?: boolean
  signed_at?: string | null
}

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    if (!user) {
      router.push("/login")
      return
    }
    fetchDocuments()
  }, [user])

  const fetchDocuments = async () => {
    try {
      const data = await apiClient.getDocuments()
      setDocuments(data)
    } catch (error) {
      console.error("Failed to fetch documents:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (id: number, name: string) => {
    try {
      const response = await apiClient.getDocumentPDF(id)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${name}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error("Failed to download document:", error)
    }
  }

  const handleViewPDF = async (id: number) => {
    try {
      const response = await apiClient.getDocumentPDF(id)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      window.open(url, '_blank')
    } catch (error) {
      console.error("Failed to view document:", error)
    }
  }

  const handleViewSignedPDF = async (id: number, name: string) => {
    try {
      const response = await apiClient.getSignedPDF(id)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      window.open(url, '_blank')
    } catch (error) {
      console.error("Failed to view signed document:", error)
    }
  }

  const handleSendToSigner = async (id: number) => {
    try {
      await apiClient.sendDocumentToSigner(id)
      alert("Document sent to signer successfully!")
    } catch (error) {
      console.error("Failed to send document:", error)
      alert("Failed to send document to signer")
    }
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Document Dashboard</h1>
              <p className="text-gray-600">Welcome back, {user.first_name}!</p>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/create-document">
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Document
                </Button>
              </Link>
              <Button variant="outline" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Your Documents</h2>

          {loading ? (
            <div className="text-center py-8">Loading documents...</div>
          ) : documents.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
                <p className="text-gray-600 mb-4">Create your first document to get started</p>
                <Link href="/create-document">
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Document
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {documents.map((doc) => (
                <Card key={doc.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{doc.name}</CardTitle>
                        <CardDescription>Created {new Date(doc.created_at).toLocaleDateString()}</CardDescription>
                      </div>
                      <Badge variant="secondary">{doc.document_type.toUpperCase()}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">Signer: {doc.signer_username}</p>
                      <div className="flex items-center gap-2 mt-2">
                        {doc.signed ? (
                          <span className="text-green-600 font-semibold text-xs">Signed{doc.signed_at ? ` on ${new Date(doc.signed_at).toLocaleDateString()}` : ''}</span>
                        ) : (
                          <span className="text-gray-400 font-semibold text-xs">Not Signed</span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => handleDownload(doc.id, doc.name)}>
                          <Download className="w-4 h-4 mr-1" />
                          Download
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleViewPDF(doc.id)}>
                          <FileText className="w-4 h-4 mr-1" />
                          View
                        </Button>
                        {doc.signed && (
                          <Button size="sm" variant="outline" onClick={() => handleViewSignedPDF(doc.id, doc.name)}>
                            <FileText className="w-4 h-4 mr-1 text-green-600" />
                            View Signed
                          </Button>
                        )}
                        <Button size="sm" variant="outline" onClick={() => handleSendToSigner(doc.id)}>
                          <Send className="w-4 h-4 mr-1" />
                          Send
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
