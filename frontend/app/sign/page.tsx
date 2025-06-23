"use client"

import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import { apiClient } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { FileText, Download, CheckCircle } from "lucide-react"

interface Document {
  id: number
  name: string
  document_type: string
  created_at: string
}

interface Summary {
  terms?: string
  responsibilities?: string
  dates?: Record<string, string>
  signatures_required?: Record<string, string>
}

export default function SignPage() {
  const searchParams = useSearchParams()
  const token = searchParams.get("token")
  const docId = searchParams.get("doc")

  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [signing, setSigning] = useState(false)
  const [signed, setSigned] = useState(false)
  const [error, setError] = useState("")
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [summary, setSummary] = useState<Summary | null>(null)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [summaryError, setSummaryError] = useState("")

  useEffect(() => {
    if (token && docId) {
      apiClient.setToken(token)
      fetchDocument()
      fetchPDF()
      fetchSummary()
    } else {
      setError("Invalid signing link")
      setLoading(false)
    }
  }, [token, docId])

  const fetchDocument = async () => {
    try {
      // In a real implementation, you'd have an endpoint to get document details for signers
      // For now, we'll simulate this
      setDocument({
        id: Number.parseInt(docId!),
        name: "Document to Sign",
        document_type: "nda",
        created_at: new Date().toISOString(),
      })
    } catch (err: any) {
      setError("Failed to load document")
    } finally {
      setLoading(false)
    }
  }

  const fetchPDF = async () => {
    try {
      const response = await apiClient.getDocumentPDF(Number(docId))
      const blob = await response.blob()
      setPdfUrl(window.URL.createObjectURL(blob))
    } catch (err) {
      setPdfUrl(null)
    }
  }

  const fetchSummary = async () => {
    setSummaryLoading(true)
    setSummaryError("")
    try {
      const data = await apiClient.getSummary(Number(docId))
      setSummary(data)
    } catch (err: any) {
      setSummary(null)
    } finally {
      setSummaryLoading(false)
    }
  }

  const handleGenerateSummary = async () => {
    setSummaryLoading(true)
    setSummaryError("")
    try {
      await apiClient.generateSummary(Number(docId))
      await fetchSummary()
    } catch (err: any) {
      setSummaryError("Failed to generate summary")
    } finally {
      setSummaryLoading(false)
    }
  }

  const handleSignDocument = async () => {
    if (!document) return

    setSigning(true)
    try {
      await apiClient.signDocument(document.id)
      setSigned(true)
    } catch (err: any) {
      setError("Failed to sign document")
    } finally {
      setSigning(false)
    }
  }

  const handleDownloadSigned = async () => {
    if (!document) return

    try {
      const response = await apiClient.getSignedPDF(document.id)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${document.name}_signed.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error("Failed to download signed document:", error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading document...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardContent className="text-center py-8">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4">
            <h1 className="text-2xl font-bold text-gray-900">Document Signing</h1>
            <p className="text-gray-600">Review and sign your document</p>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {signed ? (
          <Card>
            <CardContent className="text-center py-8">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Document Signed Successfully!</h2>
              <p className="text-gray-600 mb-6">Your document has been signed and the owner has been notified.</p>
              <Button onClick={handleDownloadSigned}>
                <Download className="w-4 h-4 mr-2" />
                Download Signed Document
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                {document?.name}
              </CardTitle>
              <CardDescription>
                Document Type: {document?.document_type.toUpperCase()} • Created:{" "}
                {document && new Date(document.created_at).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">Before Signing</h3>
                <p className="text-blue-800 text-sm">
                  Please review the document carefully before signing. Once signed, this action cannot be undone.
                </p>
              </div>

              {/* Inline PDF Viewer */}
              {pdfUrl ? (
                <div className="my-4 border rounded overflow-hidden" style={{ height: 600 }}>
                  <iframe
                    src={pdfUrl}
                    title="Document PDF"
                    width="100%"
                    height="100%"
                    style={{ border: 0 }}
                  />
                </div>
              ) : (
                <div className="text-gray-500">Unable to load PDF.</div>
              )}

              {/* Summary Section */}
              <div className="my-4">
                <h3 className="font-medium text-gray-900 mb-2">Document Summary</h3>
                {summaryLoading ? (
                  <div className="text-gray-500">Loading summary...</div>
                ) : summary ? (
                  <div className="bg-gray-50 border border-gray-200 rounded p-4 space-y-2">
                    {summary.terms && (
                      <div><strong>Terms:</strong> {summary.terms}</div>
                    )}
                    {summary.responsibilities && (
                      <div><strong>Responsibilities:</strong> {summary.responsibilities}</div>
                    )}
                    {summary.dates && Object.keys(summary.dates).length > 0 && (
                      <div><strong>Dates:</strong> {Object.entries(summary.dates).map(([k, v]) => `${k}: ${v}`).join(", ")}</div>
                    )}
                    {summary.signatures_required && Object.keys(summary.signatures_required).length > 0 && (
                      <div><strong>Signatures Required:</strong> {Object.entries(summary.signatures_required).map(([k, v]) => `${k}: ${v}`).join(", ")}</div>
                    )}
                  </div>
                ) : (
                  <div>
                    <Button onClick={handleGenerateSummary} disabled={summaryLoading}>
                      {summaryLoading ? "Generating..." : "Generate Summary"}
                    </Button>
                    {summaryError && <div className="text-red-500 mt-2">{summaryError}</div>}
                  </div>
                )}
              </div>

              <div className="flex gap-4">
                <Button onClick={handleSignDocument} disabled={signing} className="bg-green-600 hover:bg-green-700">
                  {signing ? "Signing..." : "Sign Document"}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}
