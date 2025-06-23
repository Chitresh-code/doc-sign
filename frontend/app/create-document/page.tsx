"use client"

import type React from "react"

import { useState, useMemo } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { apiClient } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

// Mapping of document types to their required metadata fields
const DOCUMENT_FIELDS: Record<string, { label: string; name: string; type?: string; placeholder?: string }[]> = {
  nda: [
    { label: "Start Date", name: "start_date", type: "date" },
    { label: "End Date", name: "end_date", type: "date" },
    { label: "Recipient Name", name: "recipient_name", placeholder: "e.g., John Doe" },
  ],
  offer: [
    { label: "Start Date", name: "start_date", type: "date" },
    { label: "Recipient Name", name: "recipient_name", placeholder: "e.g., John Doe" },
    { label: "Role", name: "role", placeholder: "e.g., Software Engineer" },
    { label: "Salary", name: "salary", type: "number", placeholder: "e.g., 50000" },
  ],
  invoice: [
    { label: "Recipient Name", name: "recipient_name", placeholder: "e.g., John Doe" },
    { label: "Due Date", name: "due_date", type: "date" },
    { label: "Item", name: "item", placeholder: "e.g., Consulting" },
    { label: "Description", name: "description", placeholder: "e.g., Consulting services for May" },
    { label: "Amount", name: "amount", type: "number", placeholder: "e.g., 10000" },
  ],
}

export default function CreateDocumentPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [formData, setFormData] = useState({
    name: "",
    template_type: "",
    prompt: "",
    signer_username: "",
    signer_email: "",
    signer_first_name: "",
    signer_last_name: "",
    metadata: {},
  })

  // Memoize the fields to render based on selected template_type
  const dynamicFields = useMemo(() => {
    return DOCUMENT_FIELDS[formData.template_type] || []
  }, [formData.template_type])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      await apiClient.generateDocument(formData)
      router.push("/dashboard")
    } catch (err: any) {
      setError(err.message || "Failed to create document")
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleMetadataChange = (key: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      metadata: { ...prev.metadata, [key]: value },
    }))
  }

  if (!user) {
    router.push("/login")
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center py-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 ml-4">Create New Document</h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Document Details</CardTitle>
            <CardDescription>Fill in the information below to generate your document</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Document Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => handleChange("name", e.target.value)}
                      placeholder="e.g., NDA for John Doe"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="template_type">Document Type</Label>
                    <Select
                      value={formData.template_type}
                      onValueChange={(value) => handleChange("template_type", value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select document type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="nda">Non-Disclosure Agreement</SelectItem>
                        <SelectItem value="offer">Job Offer Letter</SelectItem>
                        <SelectItem value="invoice">Invoice</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="prompt">AI Prompt</Label>
                    <Textarea
                      id="prompt"
                      value={formData.prompt}
                      onChange={(e) => handleChange("prompt", e.target.value)}
                      placeholder="Describe any specific clauses or terms you want to include..."
                      rows={4}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Signer Information</h3>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="signer_first_name">First Name</Label>
                      <Input
                        id="signer_first_name"
                        value={formData.signer_first_name}
                        onChange={(e) => handleChange("signer_first_name", e.target.value)}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="signer_last_name">Last Name</Label>
                      <Input
                        id="signer_last_name"
                        value={formData.signer_last_name}
                        onChange={(e) => handleChange("signer_last_name", e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signer_username">Username</Label>
                    <Input
                      id="signer_username"
                      value={formData.signer_username}
                      onChange={(e) => handleChange("signer_username", e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signer_email">Email</Label>
                    <Input
                      id="signer_email"
                      type="email"
                      value={formData.signer_email}
                      onChange={(e) => handleChange("signer_email", e.target.value)}
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-medium">Additional Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Render dynamic fields based on document type */}
                  {dynamicFields.length === 0 && (
                    <div className="text-gray-500">Select a document type to enter additional information.</div>
                  )}
                  {dynamicFields.map((field) => (
                    <div className="space-y-2" key={field.name}>
                      <Label htmlFor={field.name}>{field.label}</Label>
                      <Input
                        id={field.name}
                        type={field.type || "text"}
                        value={formData.metadata[field.name] || ""}
                        onChange={(e) => handleMetadataChange(field.name, e.target.value)}
                        placeholder={field.placeholder}
                        required
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-4">
                <Link href="/dashboard">
                  <Button variant="outline">Cancel</Button>
                </Link>
                <Button type="submit" disabled={loading}>
                  {loading ? "Creating Document..." : "Create Document"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
