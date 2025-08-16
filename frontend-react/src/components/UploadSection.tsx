'use client'
import React, { useState } from 'react'
import APIClient from '@/services/api-client'

// TypeScript interface (like Python type hints)
interface UploadResult {
  type: string
  data: any
  source: string
}

interface UploadSectionProps {
  apiClient: APIClient
  onUploadComplete: (result: UploadResult) => void
}

// Main component (like create_upload_section function)
export default function UploadSection({ apiClient, onUploadComplete }: UploadSectionProps) {
  // State for active tab (like Streamlit tabs)
  const [activeTab, setActiveTab] = useState('single-file')
  
  // Tab content data
  const tabs = [
  { id: 'single-file', label: '📄 Single File', icon: '📄' },
  { id: 'project-zip', label: '📦 Project ZIP', icon: '📦' },
  { id: 'github-repo', label: '🔗 GitHub Repo', icon: '🔗' }
]

return (
  <div className="w-full">
    {/* Title (like st.markdown) */}
    <h3 className="text-xl font-semibold mb-6 text-white">📂 Upload Your Code</h3>
    
    {/* Tab Navigation (like st.tabs) */}
    <div className="flex border-b border-gray-700 mb-6">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`px-6 py-3 font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 ${
            activeTab === tab.id
              ? 'border-b-2 border-blue-500 text-blue-400 bg-gray-800'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
      
      {/* Tab Content (like with upload_tab1, upload_tab2, etc.) */}
      <div className="min-h-96">
        {activeTab === 'single-file' && (
          <SingleFileUpload onUploadComplete={onUploadComplete} />
        )}
        
        {activeTab === 'project-zip' && (
          <ProjectUpload apiClient={apiClient} onUploadComplete={onUploadComplete} />
        )}
        
        {activeTab === 'github-repo' && (
          <GitHubUpload apiClient={apiClient} onUploadComplete={onUploadComplete} />
        )}
      </div>
    </div>
  )
}

// Single File Upload Component (like _handle_single_file_upload)
function SingleFileUpload({ onUploadComplete }: { onUploadComplete: (result: UploadResult) => void }) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [codeInput, setCodeInput] = useState('')
  
  // Handle file upload (like st.file_uploader)
  function handleFileUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (file && file.name.endsWith('.py')) {
      setUploadedFile(file)
      
      // Read file content (like uploaded_file.read().decode())
      const reader = new FileReader()
      reader.onload = (e) => {
        const code = e.target?.result as string
        
        // Success message (like st.success)
        const result = {
          type: "single_file",
          data: {
            code: code,
            filename: file.name
          },
          source: "file_upload"
        }
        
        onUploadComplete(result)
      }
      reader.readAsText(file)
    } else {
      alert("❌ Please upload a valid Python (.py) file")
    }
  }
  
  // Handle text input (like st.text_area)
  function handleCodeSubmit() {
    if (codeInput.trim()) {
      const result = {
        type: "single_file",
        data: {
          code: codeInput,
          filename: "pasted_code.py"
        },
        source: "text_input"
      }
      onUploadComplete(result)
    }
  }
  
  return (
    <div className="space-y-6">
      {/* File Upload (like st.file_uploader) */}
      <div>
        <label className="block text-sm font-medium mb-2">Upload a Python File</label>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
          <input
            type="file"
            accept=".py"
            onChange={handleFileUpload}
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <div className="text-gray-600">
              <div className="text-4xl mb-2">📄</div>
              <div className="text-lg font-medium">Drag and drop file here</div>
              <div className="text-sm">or click to browse</div>
              <div className="text-xs mt-2">Limit 200MB per file • PY</div>
            </div>
          </label>
        </div>
        
        {uploadedFile && (
          <div className="mt-4 p-4 bg-green-100 text-green-800 rounded">
            ✅ File uploaded: {uploadedFile.name} ({uploadedFile.size} bytes)
          </div>
        )}
      </div>
      
      {/* Text Input Fallback (like st.text_area) */}
      {!uploadedFile && (
        <div>
          <label className="block text-sm font-medium mb-2">✍️ Or paste your Python code below:</label>
          <textarea
            value={codeInput}
            onChange={(e) => setCodeInput(e.target.value)}
            placeholder="def hello_world():\n    return 'Hello, World!'"
            className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm"
          />
          
          {codeInput.trim() && (
            <button
              onClick={handleCodeSubmit}
              className="mt-4 bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
            >
              ✅ Use Pasted Code
            </button>
          )}
        </div>
      )}
    </div>
  )
}

// Project ZIP Upload Component (like _handle_project_upload)
function ProjectUpload({ apiClient, onUploadComplete }: { 
  apiClient: APIClient
  onUploadComplete: (result: UploadResult) => void 
}) {
  const [uploading, setUploading] = useState(false)
  
  async function handleZipUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file || !file.name.endsWith('.zip')) {
      alert("❌ Please upload a ZIP file")
      return
    }
    
    // Validate file size (like your 50MB limit)
    if (file.size > 50 * 1024 * 1024) {
      alert("❌ File too large. Please keep ZIP files under 50MB.")
      return
    }
    
    setUploading(true)
    
    try {
      // Call backend API (like api_client.upload_project)
      const apiResponse = await apiClient.uploadProject(file)
      
      if (apiResponse.status === "success") {
        const result = {
          type: "project",
          data: apiResponse,
          source: "zip_upload"
        }
        onUploadComplete(result)
      } else {
        alert(`❌ Upload failed: ${apiResponse.message || 'Unknown error'}`)
      }
    } catch (error) {
      alert(`❌ Upload error: ${error}`)
    } finally {
      setUploading(false)
    }
  }
  
  return (
    <div>
      <label className="block text-sm font-medium mb-2">Upload Python Project ZIP File</label>
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <input
          type="file"
          accept=".zip"
          onChange={handleZipUpload}
          disabled={uploading}
          className="hidden"
          id="zip-upload"
        />
        <label htmlFor="zip-upload" className="cursor-pointer">
          <div className="text-gray-600">
            <div className="text-4xl mb-2">📦</div>
            <div className="text-lg font-medium">
              {uploading ? "⏳ Uploading..." : "Upload ZIP Project"}
            </div>
            <div className="text-sm">Click to browse for ZIP file</div>
            <div className="text-xs mt-2">Limit 50MB per file • ZIP</div>
          </div>
        </label>
      </div>
    </div>
  )
}

// GitHub Upload Component (like _handle_github_upload)
function GitHubUpload({ apiClient, onUploadComplete }: { 
  apiClient: APIClient
  onUploadComplete: (result: UploadResult) => void 
}) {
  const [githubUrl, setGithubUrl] = useState('')
  const [validating, setValidating] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [validation, setValidation] = useState<any>(null)
  
  // Validate GitHub URL (like your validate_button logic)
  async function handleValidate() {
    if (!githubUrl) return
    
    setValidating(true)
    try {
      const validationResult = await apiClient.validateGithubRepo(githubUrl)
      setValidation(validationResult)
    } catch (error) {
      setValidation({ valid: false, error: 'Validation failed' })
    } finally {
      setValidating(false)
    }
  }
  
  // Download GitHub repo (like your analyze_github logic)
  async function handleDownload() {
    if (!githubUrl) return
    
    setDownloading(true)
    try {
      const apiResponse = await apiClient.downloadGithubRepo(githubUrl)
      
      if (apiResponse.status === "success") {
        const result = {
          type: "github",
          data: apiResponse,
          source: "github_download"
        }
        onUploadComplete(result)
      } else {
        alert(`❌ Download failed: ${apiResponse.message}`)
      }
    } catch (error) {
      alert(`❌ GitHub error: ${error}`)
    } finally {
      setDownloading(false)
    }
  }
  
  return (
    <div className="space-y-6">
      <h4 className="text-lg font-medium">GitHub Repository Analysis</h4>
      <p className="text-gray-600">Download and analyze any public GitHub repository</p>
      
      {/* GitHub URL Input (like st.text_input) */}
      <div className="flex gap-4">
        <div className="flex-1">
          <input
            type="url"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
            placeholder="https://github.com/username/repository"
            className="w-full p-3 border border-gray-300 rounded-lg"
          />
        </div>
        <button
          onClick={handleValidate}
          disabled={!githubUrl || validating}
          className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:opacity-50"
        >
          {validating ? "⏳" : "✅"} Validate
        </button>
      </div>
      
      {/* Validation Results (like your validation display) */}
      {validation && (
        <div className={`p-4 rounded-lg ${validation.valid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {validation.valid ? (
            <div>
              <p className="font-medium">✅ Repository is valid and accessible!</p>
              <div className="mt-2 text-sm">
                <p>📁 <strong>Repository:</strong> {validation.name}</p>
                <p>💻 <strong>Language:</strong> {validation.language}</p>
                <p>📝 <strong>Description:</strong> {validation.description}</p>
              </div>
            </div>
          ) : (
            <div>
              <p className="font-medium">❌ Validation failed: {validation.error}</p>
              <div className="mt-2 text-sm">
                <p>💡 <strong>Tips:</strong></p>
                <ul className="ml-4">
                  <li>• Make sure the repository is public</li>
                  <li>• Check the URL format</li>
                  <li>• Verify the repository exists</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Download Section (like your download options) */}
      {githubUrl && validation?.valid && (
        <div className="border-t pt-6">
          <div className="bg-blue-50 p-4 rounded-lg mb-4">
            🎯 Ready to download: <strong>{githubUrl.split('/').pop()}</strong>
          </div>
          
          <div className="flex gap-4">
            <div className="flex-1">
              <p className="text-sm text-gray-600">
                {validation ? "✅ Repository validated and ready for download" : "💡 Click 'Validate' first"}
              </p>
            </div>
            <button
              onClick={handleDownload}
              disabled={downloading || !validation?.valid}
              className="bg-red-500 text-white px-6 py-3 rounded-lg hover:bg-red-600 disabled:opacity-50"
            >
              {downloading ? "⏳ Downloading..." : "🚀 Download & Analyze"}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Helper Components for Project Overview (like _display_project_overview)
export function ProjectOverview({ projectData, isGithub = false }: { 
  projectData: any
  isGithub?: boolean 
}) {
  const [showFileList, setShowFileList] = useState(false)
  
  const sourceLabel = isGithub ? "GitHub Repository" : "📦 ZIP Project"
  const totalSize = projectData.files?.reduce((sum: number, file: any) => sum + file.size, 0) || 0
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-semibold mb-4">📊 {sourceLabel} Overview</h3>
      
      {/* Project Metrics (like st.columns(3)) */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{projectData.project_name}</div>
          <div className="text-sm text-gray-600">📁 Project</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{projectData.total_files}</div>
          <div className="text-sm text-gray-600">📄 Python Files</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">{totalSize.toLocaleString()}</div>
          <div className="text-sm text-gray-600">💾 Total Bytes</div>
        </div>
      </div>
      
      {/* File List Toggle (like st.checkbox) */}
      <div className="border-t pt-4">
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showFileList}
            onChange={(e) => setShowFileList(e.target.checked)}
            className="rounded"
          />
          <span className="font-medium">📋 Show File List</span>
        </label>
        
        {/* File List (like your for loop) */}
        {showFileList && (
          <div className="mt-4 space-y-2">
            <p className="font-medium">📁 Project Files:</p>
            <div className="max-h-64 overflow-y-auto space-y-1">
              {projectData.files?.slice(0, 10).map((file: any, index: number) => (
                <div key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                  📄 <strong>{file.name}</strong> - {(file.size / 1024).toFixed(1)} KB - 
                  <code className="text-xs">{file.path}</code>
                </div>
              ))}
              {projectData.files?.length > 10 && (
                <p className="text-xs text-gray-500">
                  ... and {projectData.files.length - 10} more files
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}