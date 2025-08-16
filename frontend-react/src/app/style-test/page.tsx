// src/app/style-test/page.tsx
// Dummy page to test Option 2 layout design

'use client'

import React, { useState } from 'react'

export default function StyleTest() {
    const [sidebarOpen, setSidebarOpen] = useState(false)
    
    return (
        <div className="min-h-screen bg-black text-white">
            {/* TOP HEADER - Clean with status */}
            <header className="bg-gray-900 border-b border-gray-700">
                <div className="flex items-center justify-between px-6 py-4">
                    {/* Left: Logo + Sidebar Toggle */}
                    <div className="flex items-center space-x-4">
                        <button 
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                            style={{
                                boxShadow: sidebarOpen 
                                    ? 'inset 0 2px 4px rgba(0,0,0,0.3), 0 1px 3px rgba(59,130,246,0.5)' 
                                    : '0 4px 8px rgba(0,0,0,0.3), 0 1px 3px rgba(255,255,255,0.1)'
                            }}
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
                    
                    {/* Right: Status Indicator */}
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2 bg-green-900/30 px-4 py-2 rounded-lg border border-green-700/50">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            <span className="text-green-300 text-sm font-medium">API Connected</span>
                        </div>
                        
                        <button className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-all duration-200 transform hover:scale-110 active:scale-95 shadow-lg hover:shadow-xl"
                                style={{
                                    boxShadow: '0 4px 8px rgba(0,0,0,0.3), 0 1px 3px rgba(255,255,255,0.1)'
                                }}>
                            <span className="text-lg">⚙️</span>
                        </button>
                    </div>
                </div>
            </header>
            
            <div className="flex">
                {/* COLLAPSIBLE SIDEBAR */}
                <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden bg-gray-900 border-r border-gray-700`}>
                    <div className="p-6 h-full">
                        <h3 className="text-lg font-semibold text-white mb-6">🔧 System Information</h3>
                        
                        {/* Backend Status */}
                        <div className="mb-6">
                            <p className="text-gray-300 font-medium mb-3">Backend API Status:</p>
                            <div className="bg-green-900/30 border border-green-700/50 p-3 rounded-lg">
                                <p className="text-green-300 font-medium">🟢 Online - All services available</p>
                            </div>
                        </div>
                        
                        {/* Available Models */}
                        <div className="mb-6">
                            <p className="text-gray-300 font-medium mb-3">Available AI Models:</p>
                            <div className="space-y-2">
                                <div className="bg-blue-900/30 border border-blue-700/50 p-3 rounded-lg">
                                    <p className="text-blue-300 font-medium">GPT-4o</p>
                                    <p className="text-blue-200/70 text-sm">Fastest & Smartest</p>
                                </div>
                                <div className="bg-purple-900/30 border border-purple-700/50 p-3 rounded-lg">
                                    <p className="text-purple-300 font-medium">GPT-3.5 Turbo</p>
                                    <p className="text-purple-200/70 text-sm">Cheaper & Fast</p>
                                </div>
                                <div className="bg-indigo-900/30 border border-indigo-700/50 p-3 rounded-lg">
                                    <p className="text-indigo-300 font-medium">O3-Mini</p>
                                    <p className="text-indigo-200/70 text-sm">Reasoning Model</p>
                                </div>
                            </div>
                        </div>
                        
                        {/* Platform Features */}
                        <div className="mb-6">
                            <p className="text-gray-300 font-medium mb-3">✨ Platform Features</p>
                            <div className="space-y-2">
                                <div className="bg-gray-800/50 border border-gray-600 p-3 rounded-lg">
                                    <p className="text-gray-200 font-medium text-sm">🔍 Analysis Types:</p>
                                    <p className="text-gray-400 text-xs mt-1">Bug Detection • Optimization • Testing</p>
                                </div>
                                <div className="bg-gray-800/50 border border-gray-600 p-3 rounded-lg">
                                    <p className="text-gray-200 font-medium text-sm">📁 Project Support:</p>
                                    <p className="text-gray-400 text-xs mt-1">ZIP Files • GitHub Repos • Multi-file</p>
                                </div>
                            </div>
                        </div>
                        
                        {/* Quick Actions */}
                        <div className="space-y-3">
                            <p className="text-gray-300 font-medium mb-3">⚡ Quick Actions</p>
                            
                            <button className="w-full bg-blue-700 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                                    style={{
                                        boxShadow: '0 6px 12px rgba(59,130,246,0.3), 0 2px 4px rgba(0,0,0,0.3)'
                                    }}>
                                🔄 Refresh Connection
                            </button>
                            
                            <button className="w-full bg-yellow-700 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                                    style={{
                                        boxShadow: '0 6px 12px rgba(251,191,36,0.3), 0 2px 4px rgba(0,0,0,0.3)'
                                    }}>
                                🆕 New Upload
                            </button>
                            
                            <button className="w-full bg-red-700 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                                    style={{
                                        boxShadow: '0 6px 12px rgba(239,68,68,0.3), 0 2px 4px rgba(0,0,0,0.3)'
                                    }}>
                                🗑️ Clear All Data
                            </button>
                        </div>
                    </div>
                </div>
                
                {/* MAIN CONTENT AREA */}
                <div className="flex-1 p-8">
                    {/* Upload Section */}
                    <div className="mb-8">
                        <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                            <h2 className="text-2xl font-bold text-white mb-6">📂 Upload Your Code</h2>
                            
                            {/* Upload Tabs with 3D effect */}
                            <div className="flex space-x-1 mb-6 bg-gray-800 p-1 rounded-lg">
                                <button className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-md font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg"
                                        style={{
                                            boxShadow: '0 4px 8px rgba(59,130,246,0.4), inset 0 1px 0 rgba(255,255,255,0.1)'
                                        }}>
                                    📄 Single File
                                </button>
                                <button className="flex-1 text-gray-400 py-3 px-4 rounded-md font-medium hover:text-gray-200 transition-all duration-200 transform hover:scale-105 active:scale-95 hover:bg-gray-700"
                                        style={{
                                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                                        }}>
                                    📦 Project ZIP
                                </button>
                                <button className="flex-1 text-gray-400 py-3 px-4 rounded-md font-medium hover:text-gray-200 transition-all duration-200 transform hover:scale-105 active:scale-95 hover:bg-gray-700"
                                        style={{
                                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                                        }}>
                                    🔗 GitHub Repo
                                </button>
                            </div>
                            
                            {/* Upload Area */}
                            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
                                <div className="text-4xl mb-4">📄</div>
                                <p className="text-gray-300 text-lg mb-2">Drag and drop file here</p>
                                <p className="text-gray-500 text-sm">or click to browse</p>
                                <p className="text-gray-600 text-xs mt-2">Limit 200MB per file • PY</p>
                            </div>
                        </div>
                    </div>
                    
                    {/* Current Upload Display */}
                    <div className="mb-8">
                        <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                            <h2 className="text-xl font-bold text-white mb-4">📁 Current Upload</h2>
                            
                            <div className="flex items-center justify-between">
                                <div className="bg-green-900/30 border border-green-700/50 p-4 rounded-lg flex-1 mr-4">
                                    <p className="text-green-300 font-medium">
                                        📄 Single File: <span className="text-green-200">app.py</span>
                                    </p>
                                    <p className="text-green-200/70 text-sm mt-1">19,839 characters</p>
                                </div>
                                
                                <div className="flex space-x-3">
                                    <button className="bg-blue-700 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                                            style={{
                                                boxShadow: '0 6px 12px rgba(59,130,246,0.4), 0 2px 4px rgba(0,0,0,0.3)'
                                            }}>
                                        🔄 Upload Different
                                    </button>
                                    <button className="bg-red-700 hover:bg-red-600 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                                            style={{
                                                boxShadow: '0 6px 12px rgba(239,68,68,0.4), 0 2px 4px rgba(0,0,0,0.3)'
                                            }}>
                                        🗑️ Clear All
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {/* Analysis Section */}
                    <div className="mb-8">
                        <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                            <h2 className="text-xl font-bold text-white mb-6">🔍 Code Analysis</h2>
                            
                            {/* Analysis Configuration */}
                            <div className="grid grid-cols-2 gap-6 mb-6">
                                <div>
                                    <p className="text-gray-300 font-medium mb-3">Choose Analysis Type:</p>
                                    <div className="space-y-2">
                                        <label className="flex items-center space-x-3 bg-gray-800 p-3 rounded-lg cursor-pointer hover:bg-gray-750">
                                            <input type="checkbox" className="rounded bg-gray-700 border-gray-600" />
                                            <span className="text-gray-200">🐞 Bug Detection</span>
                                        </label>
                                        <label className="flex items-center space-x-3 bg-gray-800 p-3 rounded-lg cursor-pointer hover:bg-gray-750">
                                            <input type="checkbox" className="rounded bg-gray-700 border-gray-600" />
                                            <span className="text-gray-200">⚡ Code Optimization</span>
                                        </label>
                                        <label className="flex items-center space-x-3 bg-gray-800 p-3 rounded-lg cursor-pointer hover:bg-gray-750">
                                            <input type="checkbox" className="rounded bg-gray-700 border-gray-600" />
                                            <span className="text-gray-200">📘 Code Explanation</span>
                                        </label>
                                    </div>
                                </div>
                                
                                <div>
                                    <p className="text-gray-300 font-medium mb-3">Choose AI Model:</p>
                                    <select className="w-full bg-gray-800 border border-gray-600 text-gray-200 p-3 rounded-lg">
                                        <option>GPT-4o (Fastest & Smartest)</option>
                                        <option>GPT-3.5 Turbo (Cheaper & Fast)</option>
                                        <option>O3-Mini (Reasoning Model)</option>
                                    </select>
                                    
                                    <button className="w-full mt-4 bg-green-700 hover:bg-green-600 text-white py-3 px-6 rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                                            style={{
                                                boxShadow: '0 8px 16px rgba(34,197,94,0.4), 0 2px 4px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1)'
                                            }}>
                                        🚀 Analyze Code
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {/* Chat Section */}
                    <div className="mb-8">
                        <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                            <h2 className="text-xl font-bold text-white mb-6">💬 AI Assistant</h2>
                            
                            <div className="bg-gray-800 rounded-lg p-4 mb-4">
                                <p className="text-blue-300">💡 Chatting about: <span className="font-medium text-blue-200">app.py</span></p>
                            </div>
                            
                            <div className="flex space-x-4">
                                <input 
                                    type="text"
                                    placeholder="Ask something about your code..."
                                    className="flex-1 bg-gray-800 border border-gray-600 text-gray-200 placeholder-gray-500 p-3 rounded-lg"
                                />
                                <button className="bg-blue-700 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                                        style={{
                                            boxShadow: '0 6px 12px rgba(59,130,246,0.4), 0 2px 4px rgba(0,0,0,0.3)'
                                        }}>
                                    📩 Send
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* OVERLAY for mobile sidebar */}
            {sidebarOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    onClick={() => setSidebarOpen(false)}
                ></div>
            )}
        </div>
    )
}