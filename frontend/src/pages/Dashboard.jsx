import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { MessageCircle, Ticket, BarChart3, LogOut } from 'lucide-react'
import useAuthStore from '../store/authStore'

export default function Dashboard() {
  const { user, logout } = useAuthStore()

  const menuItems = [
    {
      icon: <MessageCircle className="w-6 h-6" />,
      title: "Chat with AI",
      description: "Ask questions and get instant answers",
      path: "/chat",
      color: "from-blue-600 to-cyan-600"
    },
    {
      icon: <Ticket className="w-6 h-6" />,
      title: "Support Tickets",
      description: "Manage your support requests",
      path: "/tickets",
      color: "from-purple-600 to-pink-600"
    },
  ]

  if (user?.role === 'admin') {
    menuItems.push({
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Analytics",
      description: "View system analytics and metrics",
      path: "/analytics",
      color: "from-green-600 to-teal-600"
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <div className="glass sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gradient">SupportMind AI</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-300">{user?.name}</span>
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
        {/* Welcome */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-4xl font-bold mb-2">Welcome back, {user?.name}!</h2>
          <p className="text-xl text-gray-400">
            {user?.role === 'admin' ? 'You are logged in as Administrator' : 'You are logged in as a regular user'}
          </p>
        </motion.div>

        {/* Menu Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {menuItems.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Link
                to={item.path}
                className={`group block h-full`}
              >
                <div className={`glass p-8 rounded-lg h-full hover:scale-105 transition duration-300 bg-gradient-to-br ${item.color}/10`}>
                  <div className={`text-primary mb-4 group-hover:scale-110 transition duration-300`}>
                    {item.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  <p className="text-gray-400">{item.description}</p>
                  <div className="mt-4 text-primary font-semibold group-hover:translate-x-2 transition">
                    Get Started →
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Quick Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-16 glass p-8 rounded-lg"
        >
          <h3 className="text-2xl font-bold mb-4">Quick Start Guide</h3>
          <div className="space-y-3 text-gray-300">
            <p>1. <strong>Upload Documents</strong> (Admin only) - Add PDFs, Word docs, or text files to the knowledge base</p>
            <p>2. <strong>Create Tickets</strong> - Submit support requests and get AI-powered suggestions</p>
            <p>3. <strong>Chat with AI</strong> - Ask questions and get instant answers from your knowledge base</p>
            <p>4. <strong>View Analytics</strong> (Admin only) - Monitor support metrics and performance</p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
