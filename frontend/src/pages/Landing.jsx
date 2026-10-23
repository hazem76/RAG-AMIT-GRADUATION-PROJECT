import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Zap, MessageCircle, BarChart3, Lock, Sparkles, ArrowRight } from 'lucide-react'
import useAuthStore from '../store/authStore'

export default function Landing() {
  const { isAuthenticated } = useAuthStore()

  const features = [
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "AI-Powered Chat",
      description: "Intelligent chatbot that learns from your knowledge base"
    },
    {
      icon: <MessageCircle className="w-6 h-6" />,
      title: "Smart Tickets",
      description: "Automatic ticket categorization and AI-suggested solutions"
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Analytics",
      description: "Real-time insights into support performance"
    },
    {
      icon: <Lock className="w-6 h-6" />,
      title: "Secure",
      description: "Enterprise-grade security with JWT authentication"
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden">
      {/* Navigation */}
      <nav className="glass fixed w-full top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gradient">SupportMind AI</h1>
          <div className="flex gap-4">
            {isAuthenticated() ? (
              <Link to="/dashboard" className="px-6 py-2 bg-primary rounded-lg hover:bg-orange-700 transition">
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="px-6 py-2 border border-primary rounded-lg hover:bg-primary/10 transition">
                  Login
                </Link>
                <Link to="/register" className="px-6 py-2 gradient-primary rounded-lg hover:opacity-90 transition">
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <h2 className="text-6xl font-bold mb-6 leading-tight">
            AI-Powered Customer Support
            <span className="text-gradient"> That Actually Works</span>
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            SupportMind AI uses advanced Retrieval-Augmented Generation to provide instant, accurate answers from your knowledge base.
          </p>
          <div className="flex gap-4 justify-center">
            {isAuthenticated() ? (
              <Link to="/chat" className="px-8 py-3 gradient-primary rounded-lg hover:opacity-90 transition font-semibold flex items-center gap-2">
                Open Chat <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link to="/register" className="px-8 py-3 gradient-primary rounded-lg hover:opacity-90 transition font-semibold flex items-center gap-2">
                  Get Started <ArrowRight className="w-4 h-4" />
                </Link>
                <Link to="/login" className="px-8 py-3 border border-primary rounded-lg hover:bg-primary/10 transition font-semibold">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </motion.div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-4xl font-bold text-center mb-16">Powerful Features</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="glass p-6 rounded-lg hover:bg-white/10 transition group"
              >
                <div className="text-primary mb-4 group-hover:scale-110 transition duration-300">
                  {feature.icon}
                </div>
                <h4 className="text-lg font-semibold mb-2">{feature.title}</h4>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 relative">
        <div className="max-w-2xl mx-auto text-center">
          <h3 className="text-4xl font-bold mb-6">Ready to Transform Customer Support?</h3>
          <p className="text-xl text-gray-300 mb-8">
            Start using SupportMind AI today for intelligent, fast, and accurate customer support.
          </p>
          {!isAuthenticated() && (
            <Link to="/register" className="inline-block px-8 py-3 gradient-primary rounded-lg hover:opacity-90 transition font-semibold">
              Start Free Today
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 px-4 text-center text-gray-400">
        <p>© 2024 SupportMind AI. All rights reserved.</p>
      </footer>
    </div>
  )
}
