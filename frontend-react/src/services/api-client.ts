interface ApiResponse {
  status: string
  result?: string
  message?: string
  execution_time?: number
  model_used?: string
}

interface ProjectUploadResponse {
  status: string
  project_id: string
  project_name: string
  total_files: number
  files: any[]
  message?: string  // Optional error message
  download_info?: any  // Optional download metadata
}

interface ChatResponse {
  status: string
  response: string
  session_id: string
  execution_time: number
  model_used: string
  message?: string  // Optional error message
}

// Main API Client Class (like your Python class)
export default class APIClient {
  public baseUrl: string = "http://35.202.213.228:8000" 
  // Getter for base URL (public access)
  get url(): string {
    return this.baseUrl
  }
  
  // Backend health check (like is_backend_healthy)
  async isBackendHealthy(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })
      return response.ok
    } catch {
      return false
    }
  }
  
  // Health check (like health_check)
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`)
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`)
    }
    return response.json()
  }
  
  // Get available models (like get_available_models)
  getAvailableModels(): string[] {
    return ['gpt-4o', 'gpt-3.5-turbo', 'o3-mini']
  }
  
  // Get model info (like get_model_info)
  getModelInfo(model: string): string {
    const modelInfo: Record<string, string> = {
      'gpt-4o': 'GPT-4o (Fastest & Smartest)',
      'gpt-3.5-turbo': 'GPT-3.5 Turbo (Cheaper & Fast)', 
      'o3-mini': 'O3-Mini (Reasoning Model)'
    }
    return modelInfo[model] || model
  }
  
  // Analysis Methods (like your analyze_* methods)
  
  // Bug analysis (like analyze_bugs)
  async analyzeBugs(code: string, modelChoice: string = "gpt-4o"): Promise<ApiResponse> {
    try {
      const payload = {
        code: code,
        model_choice: modelChoice
      }
      
      const response = await fetch(`${this.baseUrl}/api/v1/analyze/bugs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(60000) // 60 second timeout
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const result = await response.json()
      
      // Normalize response (like your Python normalization)
      return {
        status: result.status || "success",
        result: result.result || "",
        execution_time: result.execution_time || 0,
        model_used: result.model_used || modelChoice
      }
      
    } catch (error) {
      return {
        status: "error",
        message: `Bug analysis error: ${error instanceof Error ? error.message : String(error)}`
      }
    }
  }
  
  // Code explanation (like explain_code)
  async explainCode(code: string, modelChoice: string = "gpt-4o"): Promise<ApiResponse> {
    try {
      const payload = { code, model_choice: modelChoice }
      
      const response = await fetch(`${this.baseUrl}/api/v1/analyze/explaincode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(60000)
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      const result = await response.json()
      
      return {
        status: result.status || "success",
        result: result.explanation || "",  // Backend returns 'explanation'
        execution_time: result.execution_time || 0,
        model_used: result.model_used || modelChoice
      }
      
    } catch (error) {
      return {
        status: "error", 
        message: `Code explanation error: ${error}`
      }
    }
  }
  
  // Code optimization (like optimize_code)
  async optimizeCode(code: string, modelChoice: string = "gpt-4o"): Promise<ApiResponse> {
    try {
      const payload = { code, model_choice: modelChoice }
      
      const response = await fetch(`${this.baseUrl}/api/v1/analyze/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(60000)
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      const result = await response.json()
      
      return {
        status: result.status || "success",
        result: result.optimized_code || "",  // Backend returns 'optimized_code'
        execution_time: result.execution_time || 0,
        model_used: result.model_used || modelChoice
      }
      
    } catch (error) {
      return {
        status: "error",
        message: `Code optimization error: ${error}`
      }
    }
  }
  
  // Generate edge cases (like generate_edge_cases)
  async generateEdgeCases(code: string, modelChoice: string = "gpt-4o"): Promise<ApiResponse> {
    try {
      const payload = { code, model_choice: modelChoice }
      
      const response = await fetch(`${this.baseUrl}/api/v1/analyze/edgecase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(60000)
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      const result = await response.json()
      
      return {
        status: result.status || "success",
        result: result.edge_case_analysis || "",  // Backend returns 'edge_case_analysis'
        execution_time: result.execution_time || 0,
        model_used: result.model_used || modelChoice
      }
      
    } catch (error) {
      return {
        status: "error",
        message: `Edge case generation error: ${error}`
      }
    }
  }
  
  // Generate tests (like generate_tests)
  async generateTests(code: string, modelChoice: string = "gpt-4o"): Promise<ApiResponse> {
    try {
      const payload = { code, model_choice: modelChoice }
      
      const response = await fetch(`${this.baseUrl}/api/v1/analyze/unittest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(60000)
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      const result = await response.json()
      
      return {
        status: result.status || "success",
        result: result.unit_tests || "",  // Backend returns 'unit_tests'
        execution_time: result.execution_time || 0,
        model_used: result.model_used || modelChoice
      }
      
    } catch (error) {
      return {
        status: "error",
        message: `Unit test generation error: ${error}`
      }
    }
  }
  
  // Chat Methods
  
  // Chat about code (like chat_about_code)
  async chatAboutCode(code: string, question: string, sessionId: string, modelChoice: string = "gpt-4o"): Promise<ChatResponse> {
    try {
      const payload = {
        code,
        question,
        session_id: sessionId,
        model_choice: modelChoice
      }
      
      const response = await fetch(`${this.baseUrl}/api/v1/conversational/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(60000)
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      return response.json()
      
    } catch (error) {
      return {
        status: "error",
        message: `Chat error: ${error}`,
        response: "",
        session_id: sessionId,
        execution_time: 0,
        model_used: modelChoice
      }
    }
  }
  
  // Chat about project (like chat_about_project)
  async chatAboutProject(projectId: string, question: string, fileIndex: number | null, sessionId: string): Promise<ChatResponse> {
    try {
      const payload: any = {
        question,
        session_id: sessionId
      }
      
      if (fileIndex !== null) {
        payload.file_index = fileIndex
      }
      
      const response = await fetch(`${this.baseUrl}/api/v1/conversational/${projectId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(60000)
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      return response.json()
      
    } catch (error) {
      return {
        status: "error",
        message: `Project chat error: ${error}`,
        response: "",
        session_id: sessionId,
        execution_time: 0,
        model_used: "gpt-4o"
      }
    }
  }
  
  // Project Methods
  
  // Upload project (like upload_project)
  async uploadProject(file: File): Promise<ProjectUploadResponse> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch(`${this.baseUrl}/api/v1/projects/upload`, {
        method: 'POST',
        body: formData,  // No Content-Type header for FormData
        signal: AbortSignal.timeout(120000) // 2 minute timeout
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      return response.json()
      
    } catch (error) {
      return {
        status: "error",
        message: `Project upload error: ${error}`,
        project_id: "",
        project_name: "",
        total_files: 0,
        files: []
      }
    }
  }
  
  // Download GitHub repo (like download_github_repo)
  async downloadGithubRepo(githubUrl: string): Promise<ProjectUploadResponse> {
    try {
      // Validate first
      const validation = await this.validateGithubRepo(githubUrl)
      
      if (!validation.valid) {
        return {
          status: "error",
          message: `Invalid repository: ${validation.error}`,
          project_id: "",
          project_name: "",
          total_files: 0,
          files: []
        }
      }
      
      const payload = { repo_url: githubUrl }
      
      const response = await fetch(`${this.baseUrl}/api/v1/projects/github`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(120000)
      })
      
      if (response.status === 404) {
        throw new Error("Repository not found or is private")
      } else if (response.status === 408) {
        throw new Error("Download timed out. Repository might be too large")
      } else if (!response.ok) {
        throw new Error(`GitHub API error: HTTP ${response.status}`)
      }
      
      const result = await response.json()
      
      // Add download info (like your Python version)
      result.download_info = {
        original_url: githubUrl,
        repo_name: validation.name,
        language: validation.language,
        description: validation.description
      }
      
      return result
      
    } catch (error) {
      return {
        status: "error",
        message: `GitHub download error: ${error}`,
        project_id: "",
        project_name: "",
        total_files: 0,
        files: []
      }
    }
  }
  
  // Validate GitHub repo (like validate_github_repo)
  async validateGithubRepo(githubUrl: string): Promise<any> {
    try {
      const params = new URLSearchParams({ repo_url: githubUrl })
      
      const response = await fetch(`${this.baseUrl}/api/v1/projects/github/validate?${params}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(10000)
      })
      
      if (response.ok) {
        return response.json()
      } else {
        return {
          valid: false,
          error: `Validation API error: ${response.status}`
        }
      }
      
    } catch (error) {
      return {
        valid: false,
        error: `Validation failed: ${error}`
      }
    }
  }
  
  // Analyze project file (like analyze_project_file)
  async analyzeProjectFile(projectId: string, fileIndex: number, analysisType: string, modelChoice: string): Promise<ApiResponse> {
    try {
      const payload = {
        file_index: fileIndex,
        analysis_type: analysisType,
        model_choice: modelChoice
      }
      
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(120000)
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      return response.json()
      
    } catch (error) {
      return {
        status: "error",
        message: `Project file analysis error: ${error}`
      }
    }
  }
}