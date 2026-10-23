import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  ArrowLeft, LogOut, Loader, AlertCircle, Clock, CheckCircle,
  XCircle, Sparkles, Lightbulb, Calendar, Tag, Flag,
  ChevronDown, Trash2, LayoutDashboard, RefreshCw,
} from 'lucide-react'
import useAuthStore from '../store/authStore'
import { ticketAPI } from '../services/api'

// ─── Constants ────────────────────────────────────────────────────────────────

const STATUS_META = {
  open:        { label: 'Open',        color: 'bg-blue-500/20 text-blue-300 border-blue-500/30',    icon: AlertCircle },
  in_progress: { label: 'In Progress', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30', icon: Clock },
  resolved:    { label: 'Resolved',    color: 'bg-green-500/20 text-green-300 border-green-500/30', icon: CheckCircle },
  closed:      { label: 'Closed',      color: 'bg-gray-500/20 text-gray-400 border-gray-500/30',    icon: XCircle },
}

const PRIORITY_META = {
  low:      { label: 'Low',      dot: 'bg-slate-400' },
  medium:   { label: 'Medium',   dot: 'bg-blue-400' },
  high:     { label: 'High',     dot: 'bg-orange-400' },
  critical: { label: 'Critical', dot: 'bg-red-400' },
}

const CATEGORY_META = {
  billing:   { label: 'Billing',   color: 'bg-purple-500/20 text-purple-300' },
  technical: { label: 'Technical', color: 'bg-cyan-500/20 text-cyan-300' },
  general:   { label: 'General',   color: 'bg-teal-500/20 text-teal-300' },
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function StatusBadge({ status }) {
  const meta = STATUS_META[status] || STATUS_META.open
  const Icon = meta.icon
  return (
    <span className={`inline-flex items-center gap-1.5 text-sm font-medium px-3 py-1 rounded-full border ${meta.color}`}>
      <Icon className="w-3.5 h-3.5" />
      {meta.label}
    </span>
  )
}

function InfoChip({ icon: Icon, label, value, colorClass = 'text-gray-300' }) {
  return (
    <div className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-2">
      <Icon className={`w-3.5 h-3.5 ${colorClass}`} />
      <span className="text-xs text-gray-500">{label}</span>
      <span className="text-xs font-medium text-gray-200">{value}</span>
    </div>
  )
}

function AIBlock({ icon: Icon, iconColor, title, content, delay = 0 }) {
  if (!content) return null
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass rounded-xl overflow-hidden"
    >
      <div className={`px-5 py-3 border-b border-white/10 flex items-center gap-2 ${iconColor}`}>
        <Icon className="w-4 h-4" />
        <span className="text-sm font-semibold">{title}</span>
        <span className="ml-auto text-xs opacity-60 bg-white/10 px-2 py-0.5 rounded-full">AI Generated</span>
      </div>
      <div className="px-5 py-4">
        <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
    </motion.div>
  )
}

// ─── Update Panel ─────────────────────────────────────────────────────────────

function UpdatePanel({ ticket, onUpdate, isAdmin }) {
  const [status, setStatus] = useState(ticket.status)
  const [priority, setPriority] = useState(ticket.priority)
  const [saving, setSaving] = useState(false)

  const isDirty = status !== ticket.status || priority !== ticket.priority

  const handleSave = async () => {
    if (!isDirty) return
    try {
      setSaving(true)
      const updates = {}
      if (status !== ticket.status) updates.status = status
      if (priority !== ticket.priority) updates.priority = priority
      const res = await ticketAPI.updateTicket(ticket.id, updates)
      onUpdate(res.data)
      toast.success('Ticket updated')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed')
      // reset
      setStatus(ticket.status)
      setPriority(ticket.priority)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="glass rounded-xl p-5 space-y-4">
      <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Manage Ticket</h3>

      {/* Status */}
      <div>
        <label className="block text-xs text-gray-500 mb-1.5">Status</label>
        <div className="relative">
          <select
            value={status}
            onChange={e => setStatus(e.target.value)}
            className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/40 transition pr-8"
          >
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
          <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
        </div>
      </div>

      {/* Priority — admin only */}
      {isAdmin && (
        <div>
          <label className="block text-xs text-gray-500 mb-1.5">Priority</label>
          <div className="relative">
            <select
              value={priority}
              onChange={e => setPriority(e.target.value)}
              className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/40 transition pr-8"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
          </div>
        </div>
      )}

      <button
        onClick={handleSave}
        disabled={!isDirty || saving}
        className="w-full gradient-primary py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {saving ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
        {saving ? 'Saving…' : 'Save Changes'}
      </button>
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function TicketDetail() {
  const navigate = useNavigate()
  const { ticketId } = useParams()
  const { user, logout } = useAuthStore()
  const isAdmin = user?.role === 'admin'

  const [ticket, setTicket] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const fetchTicket = async () => {
      try {
        setLoading(true)
        const res = await ticketAPI.getTicket(ticketId)
        setTicket(res.data)
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Ticket not found')
        navigate('/tickets')
      } finally {
        setLoading(false)
      }
    }
    if (ticketId) fetchTicket()
  }, [ticketId])

  const handleUpdate = (updated) => setTicket(updated)

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this ticket? This cannot be undone.')) return
    try {
      setDeleting(true)
      await ticketAPI.deleteTicket(ticket.id)
      toast.success('Ticket deleted')
      navigate('/tickets')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Delete failed')
      setDeleting(false)
    }
  }

  const fmt = (date) =>
    new Date(date).toLocaleString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })

  // ── Loading ──
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader className="w-10 h-10 animate-spin text-orange-400 mx-auto" />
          <p className="text-gray-400 text-sm">Loading ticket…</p>
        </div>
      </div>
    )
  }

  if (!ticket) return null

  const priorityMeta = PRIORITY_META[ticket.priority] || PRIORITY_META.medium
  const categoryMeta = CATEGORY_META[ticket.category] || CATEGORY_META.general

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* ── Header ── */}
      <div className="glass sticky top-0 z-40 border-b border-white/10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/tickets')}
              className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            <span className="text-gray-700">/</span>
            <span className="text-sm text-gray-400">Ticket <span className="text-orange-400 font-medium">#{ticket.id}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm hover:bg-white/10 rounded-lg transition"
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </button>
            <button
              onClick={logout}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm hover:bg-white/10 rounded-lg transition text-gray-400"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">

          {/* ── Left Column: Ticket Content ── */}
          <div className="lg:col-span-2 space-y-5">

            {/* Title + Status */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex-1">
                  <h1 className="text-2xl font-bold leading-snug mb-3">{ticket.title}</h1>
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusBadge status={ticket.status} />
                    <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full ${categoryMeta.color}`}>
                      <Tag className="w-3 h-3" />
                      {categoryMeta.label}
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-white/5 text-gray-300">
                      <span className={`w-2 h-2 rounded-full ${priorityMeta.dot}`} />
                      {priorityMeta.label} Priority
                    </span>
                  </div>
                </div>
              </div>

              {/* Meta chips */}
              <div className="flex flex-wrap gap-2 mb-5">
                <InfoChip icon={Calendar} label="Created" value={fmt(ticket.created_at)} />
                <InfoChip icon={Calendar} label="Updated" value={fmt(ticket.updated_at)} />
              </div>

              {/* Description */}
              <div>
                <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Description</h2>
                <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap bg-white/5 rounded-lg p-4">
                  {ticket.description}
                </p>
              </div>
            </motion.div>

            {/* AI Summary */}
            <AIBlock
              icon={Sparkles}
              iconColor="text-teal-400"
              title="AI Summary"
              content={ticket.ai_summary}
              delay={0.1}
            />

            {/* AI Solution */}
            <AIBlock
              icon={Lightbulb}
              iconColor="text-orange-400"
              title="AI Suggested Solution"
              content={ticket.ai_solution}
              delay={0.15}
            />

            {/* No AI yet */}
            {!ticket.ai_summary && !ticket.ai_solution && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="glass rounded-xl p-6 text-center text-gray-500 text-sm"
              >
                <Sparkles className="w-8 h-8 mx-auto mb-2 text-gray-600" />
                AI analysis is being processed for this ticket.
              </motion.div>
            )}
          </div>

          {/* ── Right Column: Sidebar ── */}
          <div className="space-y-4">

            {/* Update Panel */}
            <motion.div
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.05 }}
            >
              <UpdatePanel ticket={ticket} onUpdate={handleUpdate} isAdmin={isAdmin} />
            </motion.div>

            {/* Ticket info card */}
            <motion.div
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-xl p-5 space-y-3"
            >
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Ticket ID</span>
                  <span className="font-mono text-orange-400">#{ticket.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Category</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${categoryMeta.color}`}>
                    {categoryMeta.label}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Priority</span>
                  <span className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${priorityMeta.dot}`} />
                    {priorityMeta.label}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Status</span>
                  <StatusBadge status={ticket.status} />
                </div>
              </div>
            </motion.div>

            {/* Delete — admin only */}
            {isAdmin && (
              <motion.div
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 }}
              >
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="w-full flex items-center justify-center gap-2 py-2.5 border border-red-500/30 text-red-400 rounded-xl text-sm hover:bg-red-500/10 transition disabled:opacity-40"
                >
                  {deleting ? <Loader className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                  {deleting ? 'Deleting…' : 'Delete Ticket'}
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
