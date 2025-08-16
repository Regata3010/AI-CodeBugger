'use client'
import React, { useState, useEffect } from 'react'
import APIClient from '@/services/api-client'

// TypeScript interfaces
interface UploadData {
  type: string
  data: any
  source: string
}

interface ChatMessage {
  question: string
  response: string
  timestamp: number
}

interface ChatSectionProps {
  uploadData: UploadData
  apiClient: APIClient
  analysisResult?: any
}

// Main Chat Component (like create_chat_section)
export default function ChatSection({ uploadData, apiClient, analysisResult }: ChatSectionProps) {
  return (
    <div className="w-full">
      {/* Horizontal line (like st.markdown("---")) */}
      <hr className="my-8 border-gray-300" />
      
      {/* Title (like st.markdown) */}
      <h3 className="text-xl font-semibold mb-6">💬 AI Code Assistant</h3>
      
      {/* Determine chat context (like your if upload_data["type"]) */}
      {uploadData.type === "single_file" && (
        <SingleFileChat 
          uploadData={uploadData}
          apiClient={apiClient}
          analysisResult={analysisResult}
        />
      )}
      
      {(uploadData.type === "project" || uploadData.type === "github") && (
        <ProjectChat 
          uploadData={uploadData}
          apiClient={apiClient}
          analysisResult={analysisResult}
        />
      )}
    </div>
  )
}

// Single File Chat Component (like _handle_single_file_chat)
function SingleFileChat({ uploadData, apiClient, analysisResult }: {
  uploadData: UploadData
  apiClient: APIClient
  analysisResult?: any
}) {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const code = uploadData.data.code
  const filename = uploadData.data.filename
  
  // Quick questions (like your quick action buttons)
  const quickQuestions = [
    "Can you explain the analysis results in simple terms?",
    "Based on the analysis, how can I improve this code?",
    "What should I test for this code?"
  ]
  
  // Handle quick question (like _ask_quick_question)
  async function handleQuickQuestion(question: string) {
    setIsLoading(true)
    try {
      const sessionId = `quick_${Date.now()}`
      const apiResponse = await apiClient.chatAboutCode(code, question, sessionId, "gpt-4o")
      
      if (apiResponse.status === "success") {
        const newMessage = {
          question,
          response: apiResponse.response,
          timestamp: Date.now()
        }
        setChatHistory(prev => [...prev, newMessage])
      } else {
        alert(`❌ Quick question failed: ${apiResponse.message || 'Unknown error'}`)
      }
    } catch (error) {
      alert(`❌ Quick question error: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }
  
  // Handle regular chat (like _process_single_file_chat)
  async function handleChat() {
    if (!currentQuestion.trim()) return
    
    setIsLoading(true)
    try {
      const sessionId = `user_${Date.now()}`
      const apiResponse = await apiClient.chatAboutCode(code, currentQuestion, sessionId, "gpt-4o")
      
      if (apiResponse.status === "success") {
        const newMessage = {
          question: currentQuestion,
          response: apiResponse.response,
          timestamp: Date.now()
        }
        setChatHistory(prev => [...prev, newMessage])
        setCurrentQuestion('') // Clear input
      } else {
        alert(`❌ Chat failed: ${apiResponse.message || 'Unknown error'}`)
      }
    } catch (error) {
      alert(`❌ Chat error: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="space-y-6">
      {/* Chat Context (like st.info) */}
      <div className="bg-blue-100 text-blue-800 p-4 rounded-lg">
        💡 Chatting about: <strong>{filename}</strong>
      </div>
      
      {/* Quick Questions (like your if analysis_results) */}
      {analysisResult && (
        <div>
          <h4 className="text-lg font-medium mb-4">⚡ Quick Follow-up Questions</h4>
          <div className="grid grid-cols-3 gap-4">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuestion(question)}
                disabled={isLoading}
                className="p-3 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50"
              >
                {index === 0 && "🔍 Explain results"}
                {index === 1 && "🚀 How to improve?"}
                {index === 2 && "🧪 Testing advice?"}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Chat History Display */}
      {chatHistory.length > 0 && (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          <h4 className="text-lg font-medium">💬 Conversation History</h4>
          {chatHistory.map((message, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              {/* User Message */}
              <div className="mb-3">
                <p className="font-medium text-gray-900">🧑 You:</p>
                <p className="text-gray-700 mt-1">{message.question}</p>
              </div>
              
              {/* AI Response */}
              <div>
                <p className="font-medium text-gray-900">🤖 AI Assistant:</p>
                <div className="text-gray-700 mt-1 whitespace-pre-wrap">{message.response}</div>
                <p className="text-xs text-gray-500 mt-2">
                  ⏱️ {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Chat Input Interface (like _create_chat_interface) */}
      <div className="border-t pt-6">
        <div className="space-y-4">
          {/* Chat Input (like st.text_input) */}
          <div>
            <input
              type="text"
              value={currentQuestion}
              onChange={(e) => setCurrentQuestion(e.target.value)}
              placeholder="e.g., 'How does this function work?' or 'Any security issues?'"
              className="w-full p-3 border border-gray-300 rounded-lg"
              onKeyPress={(e) => e.key === 'Enter' && handleChat()}
            />
            <p className="text-xs text-gray-500 mt-1">
              Ask any question about your code - the AI will provide context-aware answers
            </p>
          </div>
          
          {/* Chat Buttons (like st.columns) */}
          <div className="flex gap-4">
            <button
              onClick={handleChat}
              disabled={!currentQuestion.trim() || isLoading}
              className="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? "🤔 Thinking..." : "📩 Send Question"}
            </button>
            
            <button
              onClick={() => setChatHistory([])}
              className="bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600"
            >
              🗑️ Clear Chat
            </button>
          </div>
        </div>
      </div>
      
      {/* Chat Suggestions (like display_chat_suggestions) */}
      <ChatSuggestions uploadData={uploadData} onSuggestionClick={setCurrentQuestion} />
    </div>
  )
}

// Project Chat Component (like _handle_project_chat)
function ProjectChat({ uploadData, apiClient, analysisResult }: {
  uploadData: UploadData
  apiClient: APIClient
  analysisResult?: any
}) {
  const [chatScope, setChatScope] = useState<'entire' | 'specific'>('entire')
  const [selectedFileIndex, setSelectedFileIndex] = useState<number>(0)
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const projectData = uploadData.data
  const projectName = projectData.project_name
  const files = projectData.files || []
  
  // Handle project chat (like _process_project_chat)
  async function handleProjectChat() {
    if (!currentQuestion.trim()) return
    
    setIsLoading(true)
    try {
      const sessionId = `project_${projectData.project_id}_user`
      const fileIndex = chatScope === 'specific' ? selectedFileIndex : null
      
      const apiResponse = await apiClient.chatAboutProject(
        projectData.project_id,
        currentQuestion,
        fileIndex,
        sessionId
      )
      
      if (apiResponse.status === "success") {
        const newMessage = {
          question: currentQuestion,
          response: apiResponse.response,
          timestamp: Date.now()
        }
        setChatHistory(prev => [...prev, newMessage])
        setCurrentQuestion('')
      } else {
        alert(`❌ Project chat failed: ${apiResponse.message || 'Unknown error'}`)
      }
    } catch (error) {
      alert(`❌ Project chat error: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="space-y-6">
      {/* Project Context (like st.info) */}
      <div className="bg-blue-100 text-blue-800 p-4 rounded-lg">
        📁 Project chat: <strong>{projectName}</strong> ({files.length} files)
      </div>
      
      {/* Chat Scope Selection (like st.radio) */}
      <div>
        <p className="font-medium mb-3">Chat about:</p>
        <div className="flex gap-4">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="radio"
              name="chatScope"
              checked={chatScope === 'entire'}
              onChange={() => setChatScope('entire')}
            />
            <span>💬 Entire Project</span>
          </label>
          
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="radio"
              name="chatScope"
              checked={chatScope === 'specific'}
              onChange={() => setChatScope('specific')}
            />
            <span>📄 Specific File</span>
          </label>
        </div>
        <p className="text-xs text-gray-500 mt-1">Choose whether to discuss the whole project or focus on one file</p>
      </div>
      
      {/* File Selection (like st.selectbox) */}
      {chatScope === 'specific' && files.length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-2">Select file to discuss:</label>
          <select
            value={selectedFileIndex}
            onChange={(e) => setSelectedFileIndex(parseInt(e.target.value))}
            className="w-full p-3 border border-gray-300 rounded-lg"
          >
            {files.map((file: any, index: number) => (
              <option key={index} value={index}>
                📄 {file.name} ({file.size} bytes)
              </option>
            ))}
          </select>
          
          {files[selectedFileIndex] && (
            <div className="mt-2 bg-green-100 text-green-800 p-3 rounded">
              💡 Chatting about: <strong>{files[selectedFileIndex].name}</strong>
            </div>
          )}
        </div>
      )}
      
      {/* Chat Interface */}
      <div className="space-y-4">
        {/* Context Info (like st.caption) */}
        <p className="text-sm text-gray-600">
          🎯 Current context: {chatScope === 'entire' ? `Project: ${projectName}` : `File: ${files[selectedFileIndex]?.name}`}
        </p>
        
        {/* Chat Input */}
        <div>
          <input
            type="text"
            value={currentQuestion}
            onChange={(e) => setCurrentQuestion(e.target.value)}
            placeholder="e.g., 'How do these files work together?' or 'What's the architecture?'"
            className="w-full p-3 border border-gray-300 rounded-lg"
            onKeyPress={(e) => e.key === 'Enter' && handleProjectChat()}
          />
          <p className="text-xs text-gray-500 mt-1">
            Ask questions about your project - specify files or ask about overall architecture
          </p>
        </div>
        
        {/* Send Buttons (like st.columns) */}
        <div className="flex gap-4">
          <button
            onClick={handleProjectChat}
            disabled={!currentQuestion.trim() || isLoading}
            className="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {isLoading ? "🤔 Thinking..." : "📩 Send Question"}
          </button>
          
          <button
            onClick={() => setChatHistory([])}
            className="bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600"
          >
            🗑️ Clear Project Chat
          </button>
        </div>
      </div>
      
      {/* Chat History */}
      {chatHistory.length > 0 && (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          <h4 className="text-lg font-medium">💬 Project Conversation</h4>
          {chatHistory.map((message, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="mb-3">
                <p className="font-medium">🧑 You:</p>
                <p className="text-gray-700 mt-1">{message.question}</p>
              </div>
              
              <div>
                <p className="font-medium">🤖 AI Assistant:</p>
                <div className="text-gray-700 mt-1 whitespace-pre-wrap">{message.response}</div>
                <p className="text-xs text-gray-500 mt-2">
                  ⏱️ {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Chat Suggestions Component (like display_chat_suggestions)
function ChatSuggestions({ uploadData, onSuggestionClick }: {
  uploadData: UploadData
  onSuggestionClick: (suggestion: string) => void
}) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  // Generate suggestions based on upload type (like your if upload_data["type"])
  const suggestions = uploadData.type === "single_file" ? [
    "What does this code do?",
    "Are there any security issues?",
    "How can I optimize this?",
    "What edge cases should I consider?",
    "Is this code following best practices?"
  ] : [
    "What is the overall architecture?",
    "How do these files work together?",
    "What's the main entry point?",
    "Any architectural improvements?",
    "Which files are most critical?"
  ]
  
  return (
    <div className="border border-gray-200 rounded-lg">
      {/* Expandable Header (like st.expander) */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left p-3 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95"
      >
        <span className="font-medium">💡 Suggested Questions</span>
        <span className="text-gray-400">{isExpanded ? '▼' : '▶'}</span>
      </button>
      
      {/* Suggestions List */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-4">
          <p className="text-sm text-gray-600 mb-3">Click any question to ask:</p>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => onSuggestionClick(suggestion)}
                className="w-full text-left p-3 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95"
              >
                ❓ {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Enhanced Chat Interface Component (like create_enhanced_chat_interface)
export function EnhancedChatInterface({ uploadData, apiClient }: {
  uploadData: UploadData
  apiClient: APIClient
}) {
  const [recentHistory, setRecentHistory] = useState<ChatMessage[]>([])
  
  // Load recent chat history (like _display_recent_chat_history)
  useEffect(() => {
    // In a real app, you'd load this from localStorage or backend
    const historyKey = uploadData.type === "single_file" 
      ? "single_file_chat_history" 
      : `project_${uploadData.data.project_id}_chat_history`
    
    // For now, just use empty array
    setRecentHistory([])
  }, [uploadData])
  
  return (
    <div className="w-full">
      <h3 className="text-xl font-semibold mb-6">💬 Enhanced AI Code Assistant</h3>
      
      {/* Current Context (like st.success) */}
      <div className="bg-green-100 text-green-800 p-4 rounded-lg mb-6">
        🎯 Ready to chat about: <strong>
          {uploadData.type === "single_file" 
            ? uploadData.data.filename
            : uploadData.data.project_name
          }
        </strong>
      </div>
      
      {/* Recent Conversation (like _display_recent_chat_history) */}
      {recentHistory.length > 0 && (
        <div className="mb-6">
          <details className="border border-gray-200 rounded-lg">
            <summary className="p-4 cursor-pointer font-medium hover:bg-gray-50">
              📜 Recent Conversation
            </summary>
            <div className="border-t border-gray-200 p-4 space-y-3">
              {recentHistory.slice(-3).map((item, index) => (
                <div key={index}>
                  <p className="font-medium">🧑 You: {item.question}</p>
                  <p className="text-gray-700 mt-1">
                    🤖 AI: {item.response.substring(0, 200)}{item.response.length > 200 ? '...' : ''}
                  </p>
                  {index < recentHistory.slice(-3).length - 1 && <hr className="my-2" />}
                </div>
              ))}
            </div>
          </details>
        </div>
      )}
      
      {/* Main Chat Interface */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Type your question about the code..."
          className="flex-1 p-3 border border-gray-300 rounded-lg"
        />
        <button className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600">
          📩 Send
        </button>
      </div>
    </div>
  )
}

// Utility functions (like your helper functions)
export function getChatContextInfo(uploadData: UploadData, fileIndex?: number): string {
  if (uploadData.type === "single_file") {
    return `Single file: ${uploadData.data.filename}`
  } else if (uploadData.type === "project" || uploadData.type === "github") {
    const projectName = uploadData.data.project_name
    if (fileIndex !== undefined && uploadData.data.files) {
      const fileName = uploadData.data.files[fileIndex]?.name
      return `Project file: ${fileName} in ${projectName}`
    } else {
      return `Entire project: ${projectName}`
    }
  }
  
  return "Unknown context"
}

export function isChatAvailable(uploadData: UploadData): boolean {
  if (uploadData.type === "single_file") {
    return Boolean(uploadData.data.code?.trim())
  } else if (uploadData.type === "project" || uploadData.type === "github") {
    return Boolean(uploadData.data.project_id)
  }
  
  return false
}