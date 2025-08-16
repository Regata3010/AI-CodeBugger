'use client'
import React, { useState, useEffect } from 'react'
import APIClient from '@/services/api-client'

// TypeScript interfaces (like Python type hints)
interface UploadData {
  type: string
  data: any
  source: string
}

interface AnalysisResult {
  status: string
  result?: string  // Make it optional to match ApiResponse
  execution_time?: number  // Make it optional to match ApiResponse
  model_used?: string  // Make it optional to match ApiResponse
  message?: string
}

interface AnalysisSectionProps {
  uploadData: UploadData
  apiClient: APIClient
  onAnalysisComplete: (result: any) => void
}

// Main Analysis Component (like create_analysis_section)
export default function AnalysisSection({ uploadData, apiClient, onAnalysisComplete }: AnalysisSectionProps) {
  // State management (like Streamlit session state)
  const [selectedAnalysisTypes, setSelectedAnalysisTypes] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState('gpt-4o')
  const [selectedFileIndex, setSelectedFileIndex] = useState<number>(0) // NEW: For file selection
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<Record<string, AnalysisResult>>({})
  const [progress, setProgress] = useState(0)
  const [statusText, setStatusText] = useState('')

  // Analysis type options (like your list)
  const analysisTypes = [
    'Bug Detection',
    'Code Optimization', 
    'Code Explanation',
    'Unit Test Generation',
    'Edge Case Detection'
  ]

  // Model options (like your model_options dict)
  const modelOptions = {
    'gpt-4o': 'GPT-4o (Fastest & Smartest)',
    'gpt-3.5-turbo': 'GPT-3.5 Turbo (Cheaper & Fast)', 
    'o3-mini': 'O3-Mini (Reasoning Model)'
  }

  // Auto-select first file when GitHub/project is uploaded
  useEffect(() => {
    if ((uploadData.type === "project" || uploadData.type === "github") && uploadData.data.files) {
      setSelectedFileIndex(0)
    }
  }, [uploadData])

  // Handle analysis type selection (like st.multiselect)
  function toggleAnalysisType(type: string) {
    setSelectedAnalysisTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)  // Remove if already selected
        : [...prev, type]               // Add if not selected
    )
  }

  // Get current file data based on upload type
  function getCurrentFileData() {
    if (uploadData.type === "single_file") {
      return {
        code: uploadData.data.code,
        filename: uploadData.data.filename
      }
    } else if (uploadData.type === "project" || uploadData.type === "github") {
      const files = uploadData.data.files || []
      const selectedFile = files[selectedFileIndex]
      return {
        code: selectedFile?.content || selectedFile?.code || '',
        filename: selectedFile?.name || 'unknown_file.py'
      }
    }
    return { code: '', filename: '' }
  }

  // Main analysis handler (like your if upload_data["type"] logic)
  function handleAnalysis() {
    if (uploadData.type === "single_file") {
      runSingleFileAnalysis()
    } else if (uploadData.type === "project" || uploadData.type === "github") {
      runProjectFileAnalysis() // NEW: Handle project/GitHub analysis
    }
  }

  // Single file analysis (like _run_single_file_analysis)
  async function runSingleFileAnalysis() {
    if (!uploadData.data.code) return
    
    setIsAnalyzing(true)
    setProgress(0)
    const results: Record<string, AnalysisResult> = {}
    
    // Loop through selected analysis types (like your for loop)
    for (let i = 0; i < selectedAnalysisTypes.length; i++) {
      const analysisType = selectedAnalysisTypes[i]
      
      setStatusText(`Running ${analysisType}...`)
      setProgress((i + 0.5) / selectedAnalysisTypes.length)
      
      try {
        // Make API call (like _make_analysis_api_call)
        const apiResponse = await makeAnalysisApiCall(analysisType, uploadData.data.code, selectedModel)
        
        if (apiResponse.status === "success") {
          // Convert ApiResponse to AnalysisResult with proper type safety
          results[analysisType] = {
            status: apiResponse.status,
            result: apiResponse.result ?? "",  // Use nullish coalescing
            execution_time: apiResponse.execution_time ?? 0,
            model_used: apiResponse.model_used ?? selectedModel,
            message: apiResponse.message
          } as AnalysisResult
        } else {
          console.error(`${analysisType} failed:`, apiResponse.message || 'Unknown error')
        }
      } catch (error) {
        console.error(`${analysisType} error:`, error)
      }
      
      setProgress((i + 1) / selectedAnalysisTypes.length)
    }
    
    setStatusText("✅ Analysis complete!")
    setAnalysisResults(results)
    setIsAnalyzing(false)
    onAnalysisComplete(results)
  }

  // NEW: Project file analysis (handles GitHub/ZIP projects)
  async function runProjectFileAnalysis() {
    if (!uploadData.data.project_id) {
      alert("⚠️ Project ID missing")
      return
    }
    
    setIsAnalyzing(true)
    setProgress(0)
    const results: Record<string, AnalysisResult> = {}
    
    // Loop through selected analysis types
    for (let i = 0; i < selectedAnalysisTypes.length; i++) {
      const analysisType = selectedAnalysisTypes[i]
      
      setStatusText(`Running ${analysisType} on file ${selectedFileIndex + 1}...`)
      setProgress((i + 0.5) / selectedAnalysisTypes.length)
      
      try {
        // Use the PROJECT analysis endpoint instead of single file endpoints
        const apiResponse = await apiClient.analyzeProjectFile(
          uploadData.data.project_id,
          selectedFileIndex,
          mapAnalysisType(analysisType), // Map frontend type to backend type
          selectedModel
        )
        
        if (apiResponse.status === "success") {
          results[analysisType] = apiResponse
        } else {
          console.error(`${analysisType} failed:`, apiResponse.message || 'Unknown error')
        }
      } catch (error) {
        console.error(`${analysisType} error:`, error)
      }
      
      setProgress((i + 1) / selectedAnalysisTypes.length)
    }
    
    setStatusText("✅ Analysis complete!")
    setAnalysisResults(results)
    setIsAnalyzing(false)
    onAnalysisComplete(results)
  }

  // API call mapping (like _make_analysis_api_call)
  async function makeAnalysisApiCall(analysisType: string, code: string, modelChoice: string) {
    const apiMapping: Record<string, keyof APIClient> = {
      "Bug Detection": "analyzeBugs",
      "Code Optimization": "optimizeCode",
      "Code Explanation": "explainCode",
      "Unit Test Generation": "generateTests",
      "Edge Case Detection": "generateEdgeCases"
    }

    const apiMethod = apiMapping[analysisType]
    if (!apiMethod) {
      throw new Error(`Unknown analysis type: ${analysisType}`)
    }

    // Call the appropriate API method
    return await (apiClient[apiMethod] as any)(code, modelChoice)
  }

  // NEW: Map frontend analysis types to backend types
  function mapAnalysisType(frontendType: string): string {
    const mapping: Record<string, string> = {
      "Bug Detection": "bugs",
      "Code Explanation": "explain", 
      "Code Optimization": "optimize",
      "Unit Test Generation": "tests",
      "Edge Case Detection": "edge-cases"
    }
    return mapping[frontendType] || frontendType
  }

  // Get files for project/GitHub uploads
  const projectFiles = (uploadData.type === "project" || uploadData.type === "github") ? uploadData.data.files || [] : []

  return (
    <div className="w-full">
      {/* Analysis Configuration Title (like st.markdown) */}
      <h3 className="text-xl font-semibold mb-6">🔍 Analysis Configuration</h3>
      
      {/* NEW: File Selection for Project/GitHub (matching ChatSection pattern) */}
      {(uploadData.type === "project" || uploadData.type === "github") && projectFiles.length > 0 && (
        <div className="mb-6">
          <label className="block text-sm font-medium mb-3">📁 Select File to Analyze:</label>
          <select
            value={selectedFileIndex}
            onChange={(e) => setSelectedFileIndex(parseInt(e.target.value))}
            className="w-full p-3 border border-gray-300 rounded-lg"
          >
            {projectFiles.map((file: any, index: number) => (
              <option key={index} value={index}>
                📄 {file.name} ({file.size} bytes)
              </option>
            ))}
          </select>
          
          {projectFiles[selectedFileIndex] && (
            <div className="mt-2 bg-green-100 text-green-800 p-3 rounded">
              💡 Analyzing: <strong>{projectFiles[selectedFileIndex].name}</strong>
            </div>
          )}
        </div>
      )}

      {/* Current Upload Display */}
      <div className="bg-gray-800 p-4 rounded-lg mb-6 border border-gray-600">
        <h4 className="text-md font-medium mb-2 text-gray-200">📁 Current Upload</h4>
        {uploadData.type === "single_file" ? (
          <div className="bg-gray-700 p-3 border border-gray-500 rounded text-gray-200">
            <p className="text-sm">
              📄 Single File: <strong>{uploadData.data.filename}</strong>
            </p>
            <p className="text-xs text-gray-400">{uploadData.data.code?.length || 0} characters</p>
          </div>
        ) : (
          <div className="bg-gray-700 p-3 border border-gray-500 rounded text-gray-200">
            <p className="text-sm">
              {uploadData.type === "github" ? "🔗 GitHub:" : "📦 Project:"} <strong>{uploadData.data.project_name}</strong>
            </p>
            <p className="text-xs text-gray-400">{projectFiles.length} files available</p>
            {projectFiles[selectedFileIndex] && (
              <p className="text-xs text-blue-400 mt-1">
                Currently selected: {projectFiles[selectedFileIndex].name}
              </p>
            )}
          </div>
        )}
      </div>
      
      {/* Analysis Type Selection (like st.multiselect) */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-3">Choose Analysis Type:</label>
        <div className="grid grid-cols-2 gap-3">
          {analysisTypes.map(type => (
            <label key={type} className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-100 hover:text-gray-800 transition-colors duration-200">
              <input
                type="checkbox"
                checked={selectedAnalysisTypes.includes(type)}
                onChange={() => toggleAnalysisType(type)}
                className="rounded"
              />
              <span className="text-sm">{type}</span>
            </label>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-2">Select one or more analysis types to run on your code</p>
      </div>

      {/* Model Selection (like st.selectbox) */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Choose AI Model:</label>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg"
        >
          {Object.entries(modelOptions).map(([key, label]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>
      </div>

      {/* Analysis Type Warning (like your if not analysis_types) */}
      {selectedAnalysisTypes.length === 0 && (
        <div className="bg-blue-100 text-blue-800 p-4 rounded-lg mb-6">
          👆 Please select at least one analysis type to continue
        </div>
      )}

      {/* Analysis Button (like st.button) */}
      {selectedAnalysisTypes.length > 0 && (
        <button
          onClick={handleAnalysis}
          disabled={isAnalyzing}
          className="w-full bg-blue-600 text-gray-100 py-3 px-6 rounded-lg font-medium hover:bg-blue-700 hover:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          {isAnalyzing ? "⏳ Analyzing..." : "🚀 Analyze Code"}
        </button>
      )}

      {/* Progress Bar (like st.progress) */}
      {isAnalyzing && (
        <div className="mt-6">
          <div className="mb-2">
            <div className="flex justify-between text-sm">
              <span>{statusText}</span>
              <span>{Math.round(progress * 100)}%</span>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Analysis Results Display (like _display_analysis_result) */}
      {Object.keys(analysisResults).length > 0 && (
        <div className="mt-8 space-y-6">
          <h4 className="text-lg font-semibold">📋 Analysis Results</h4>
          
          {Object.entries(analysisResults).map(([analysisType, result]) => (
            <AnalysisResultCard 
              key={analysisType}
              analysisType={analysisType}
              result={result}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// Analysis Result Card Component (like _display_analysis_result)
function AnalysisResultCard({ analysisType, result }: { 
  analysisType: string
  result: AnalysisResult 
}) {
  const [isExpanded, setIsExpanded] = useState(true)
  
  // Determine if result should be displayed as code (like your if statement)
  const isCodeResult = ["Bug Detection", "Unit Test Generation", "Edge Case Detection"].includes(analysisType)
  
  // Download functionality
  function handleDownload() {
    const fileExtension = isCodeResult ? "py" : "md"
    const filename = `${analysisType.toLowerCase().replace(' ', '_')}_result.${fileExtension}`
    const mimeType = isCodeResult ? "text/x-python" : "text/markdown"
    
    const blob = new Blob([result.result || ''], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  
  return (
    <div className="border border-gray-200 rounded-lg">
      {/* Expandable Header (like st.expander) */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex justify-between items-center p-4 text-left hover:bg-gray-50"
      >
        <span className="font-medium">📋 {analysisType} Results</span>
        <span className="text-gray-400">{isExpanded ? '▼' : '▶'}</span>
      </button>
      
      {/* Expandable Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-4">
          {/* Metadata (like your col1, col2) */}
          <div className="flex justify-between text-sm text-gray-600 mb-4">
            <span>⏱️ Completed in {(result.execution_time || 0).toFixed(2)} seconds</span>
            <span>🤖 Model: {result.model_used || 'Unknown'}</span>
          </div>
          
          {/* Result Display */}
          {isCodeResult ? (
            // Code display (like st.code)
            <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono">
              <code>{result.result || 'No code result'}</code>
            </pre>
          ) : (
            // Markdown display (like st.markdown)
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-sm">{result.result || 'No result available'}</div>
            </div>
          )}
          
          {/* Download Button (like st.download_button) */}
          <button
            onClick={handleDownload}
            className="mt-4 bg-blue-500 text-white px-4 py-2 rounded text-sm hover:bg-blue-600"
          >
            📄 Download {analysisType} Results
          </button>
        </div>
      )}
    </div>
  )
}