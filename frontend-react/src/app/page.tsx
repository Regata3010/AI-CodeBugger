'use client'

import React, { useState, useEffect } from 'react'
import APIClient from '@/services/api-client'
import UploadSection from '@/components/UploadSection'
import AnalysisSection from '@/components/AnalysisSection'
import ChatSection from '@/components/ChatSection'

interface UploadResult {
  type: string
  data: any
  source: string
}

export default function Home() {
    // State management
    const [apiClient] = useState(() => new APIClient())
    const [backendStatus, setBackendStatus] = useState('checking')
    const [uploadResult, setUploadResult] = useState<UploadResult | null>(null)
    const [analysisResult, setAnalysisResult] = useState(null)
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const [showDebugInfo, setShowDebugInfo] = useState(false)
    
    // Backend health check
    useEffect(() => {
        checkBackendHealth()
        const healthCheck = setInterval(checkBackendHealth, 60000)
        return () => clearInterval(healthCheck)
    }, [])
    
    async function checkBackendHealth() {
        try {
            const isHealthy = await apiClient.isBackendHealthy()
            setBackendStatus(isHealthy ? 'connected' : 'error')
        } catch (error) {
            setBackendStatus('error')
        }
    }
    
    function handleUploadDifferent() {
        setUploadResult(null)
        setAnalysisResult(null)
    }
    
    function handleClearAll() {
        setUploadResult(null)
        setAnalysisResult(null)
    }
    
    return (
        <div className="min-h-screen bg-black text-white">
            {/* HEADER */}
            <header className="bg-gray-900 border-b border-gray-700">
                <div className="flex items-center justify-between px-6 py-4">
                    <div className="flex items-center space-x-4">
                        <button 
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-all duration-200 transform hover:scale-105 active:scale-95"
                        >
                            <span className="text-xl">☰</span>
                        </button>
                        
                        <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                                <span className="text-sm">🧠</span>
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-white">AI Code Review Platform</h1>
                                <p className="text-gray-400 text-sm">Enterprise Architecture</p>
                            </div>
                        </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 bg-green-900/30 px-4 py-2 rounded-lg border border-green-700/50">
                        <div className={`w-2 h-2 rounded-full ${
                            backendStatus === 'connected' ? 'bg-green-400' : 'bg-red-400'
                        }`}></div>
                        <span className="text-green-300 text-sm font-medium">
                            {backendStatus === 'connected' ? 'API Connected' : 'API Offline'}
                        </span>
                    </div>
                </div>
            </header>
            
            <div className="flex">
                {/* SIDEBAR */}
                <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden bg-gray-900 border-r border-gray-700`}>
                    <div className="p-6">
                        <h3 className="text-lg font-semibold text-white mb-6">🔧 System Information</h3>
                        
                        <div className="space-y-3">
                            <button 
                                onClick={checkBackendHealth}
                                className="w-full bg-blue-600 hover:bg-blue-800 text-white px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95"
                            >
                                🔄 Refresh Connection
                            </button>
                            
                            {uploadResult && (
                                <button 
                                    onClick={handleUploadDifferent}
                                    className="w-full bg-yellow-600 hover:bg-yellow-800 text-white px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95"
                                >
                                    🆕 New Upload
                                </button>
                            )}
                            
                            <button 
                                onClick={handleClearAll}
                                className="w-full bg-red-600 hover:bg-red-800 text-white px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95"
                            >
                                🗑️ Clear All Data
                            </button>
                        </div>
                    </div>
                </div>
                
                {/* MAIN CONTENT */}
                <div className="flex-1 p-8">
                    {/* System Status */}
                    <div className="mb-8">
                        <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">🔌 System Status</h2>
                            
                            {backendStatus === 'connected' && (
                                <div className="bg-green-900/30 border border-green-700/50 text-green-200 p-4 rounded-lg">
                                    <span className="font-medium">✅ Connected to AI Backend API</span>
                                </div>
                            )}
                            
                            {backendStatus === 'error' && (
                                <div className="bg-red-900/30 border border-red-700/50 text-red-200 p-4 rounded-lg">
                                    <span className="font-medium">❌ Backend API is not running</span>
                                </div>
                            )}
                        </div>
                    </div>
                    
                    {/* Upload Section */}
                    {backendStatus === 'connected' && (
                        <div className="mb-8">
                            <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                                <h2 className="text-2xl font-bold text-white mb-6">📂 Upload Your Code</h2>
                                <UploadSection 
                                    apiClient={apiClient}
                                    onUploadComplete={setUploadResult}
                                />
                            </div>
                        </div>
                    )}
                    
                    {/* Current Upload Display - FIXED */}
                    {uploadResult && (
                        <div className="mb-8">
                            <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                                <h2 className="text-xl font-bold text-white mb-4">📁 Current Upload</h2>
                                
                                <div className="flex items-center justify-between">
                                    <div className="bg-green-900/30 border border-green-700/50 p-4 rounded-lg flex-1 mr-4">
                                        {/* Single File Display */}
                                        {uploadResult.type === "single_file" && (
                                            <>
                                                <p className="text-green-300 font-medium">
                                                    📄 Single File: <span className="text-green-200">{uploadResult.data?.filename || 'Unknown'}</span>
                                                </p>
                                                <p className="text-green-200/70 text-sm mt-1">
                                                    {uploadResult.data?.code?.length?.toLocaleString() || 0} characters
                                                </p>
                                            </>
                                        )}
                                        
                                        {/* GitHub/Project Display */}
                                        {(uploadResult.type === "github" || uploadResult.type === "project") && (
                                            <>
                                                <p className="text-green-300 font-medium">
                                                    {uploadResult.type === "github" ? "🔗 GitHub:" : "📦 Project:"} <span className="text-green-200">{uploadResult.data?.project_name || 'Unknown'}</span>
                                                </p>
                                                <p className="text-green-200/70 text-sm mt-1">
                                                    {uploadResult.data?.total_files || 0} files available
                                                </p>
                                            </>
                                        )}
                                    </div>
                                    
                                    <div className="flex space-x-3">
                                        <button 
                                            onClick={handleUploadDifferent}
                                            className="bg-blue-600 hover:bg-blue-800 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95"
                                        >
                                            🔄 Upload Different
                                        </button>
                                        <button 
                                            onClick={handleClearAll}
                                            className="bg-red-600 hover:bg-red-800 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95"
                                        >
                                            🗑️ Clear All
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    {/* Analysis Section */}
                    {uploadResult && (
                        <div className="mb-8">
                            <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                                <h2 className="text-xl font-semibold text-white mb-6">🔍 Code Analysis</h2>
                                <AnalysisSection 
                                    uploadData={uploadResult}
                                    apiClient={apiClient}
                                    onAnalysisComplete={setAnalysisResult}
                                />
                            </div>
                        </div>
                    )}
                    
                    {/* Chat Section */}
                    {uploadResult && (
                        <div className="mb-8">
                            <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                                <ChatSection 
                                    uploadData={uploadResult}
                                    apiClient={apiClient}
                                    analysisResult={analysisResult}
                                />
                            </div>
                        </div>
                    )}
                    
                    {/* No Upload Message */}
                    {!uploadResult && backendStatus === 'connected' && (
                        <div className="text-center">
                            <div className="bg-blue-900/30 border border-blue-700/50 text-blue-200 p-8 rounded-xl max-w-2xl mx-auto">
                                <div className="text-4xl mb-4">🚀</div>
                                <h3 className="text-xl font-semibold mb-2">Ready for AI Analysis</h3>
                                <p>Upload a Python file, ZIP project, or GitHub repository to get started!</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}