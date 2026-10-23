import React from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Upload, LogOut } from 'lucide-react'
import useAuthStore from '../store/authStore'

export default function KnowledgeBase() {
  const navigate = useNavigate()
  const { logout } = useAuthStore()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <div className="glass sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gradient">Knowledge Base</h1>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 hover:bg-white/10 rounded-lg transition"
            >
              Dashboard
            </button>
            <button
              onClick={logout}
              className="flex items-center gap-2 px-4 py-2 hover:bg-white/10 rounded-lg transition"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-12 rounded-lg text-center"
        >
          <Upload className="w-16 h-16 mx-auto mb-4 text-primary" />
          <h2 className="text-3xl font-bold mb-2">Knowledge Base Management</h2>
          <p className="text-gray-400 mb-6">
            Upload PDF, Word, and text documents to build your AI knowledge base. Supported formats: PDF, DOCX, TXT
          </p>
          <div className="flex gap-4 justify-center">
            <button className="px-6 py-2 gradient-primary rounded-lg hover:opacity-90 transition flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload Document
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 border border-primary rounded-lg hover:bg-primary/10 transition"
            >
              Back to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
