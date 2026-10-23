import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Ticket, Plus, LogOut, Search, Filter, X, Loader,
  ChevronRight, AlertCircle, Clock, CheckCircle, XCircle,
  LayoutGrid, List, ArrowUpDown, LayoutDashboard,
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
  low:      { label: 'Low',      color: 'bg-slate-500/20 text-slate-300 border-slate-500/30' },
  medium:   { label: 'Medium',   color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  high:     { label: 'High',     color: 'bg-orange-500/20 text-orange-300 border-orange-500/30' },
  critical: { label: 'Critical', color: 'bg-red-500/20 text-red-300 border-red-500/30' },
}

const CATEGORY_META = {
  billing:   { label: 'Billing',   color: 'bg-purple-500/20 text-purple-300' },
  technical: { label: 'Technical', color: 'bg-cyan-500/20 text-cyan-300' },
  general:   { label: 'General',   color: 'bg-teal-500/20 text-teal-300' },
}

const STATUS_TABS = [
  { key: 'all', label: 'All' },
  { key: 'open', label: 'Open' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'resolved', label: 'Resolved' },
  { key: 'closed', label: 'Closed' },
]

// ─── Sub-components ───────────────────────────────────────────────────────────

function StatusBadge({ status }) {
  const meta = STATUS_META[status] || STATUS_META.open
  const Icon = meta.icon
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full border ${meta.color}`}>
      <Icon className="w-3 h-3" />
      {meta.label}
    </span>
  )
}

function PriorityBadge({ priority }) {
  const meta = PRIORITY_META[priority] || PRIORITY_META.medium
  return (
    <span className={`inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full border ${meta.color}`}>
      {meta.label}
    </span>
  )
}

function CategoryBadge({ category }) {
  const meta = CATEGORY_META[category] || CATEGORY_META.general
  return (
    <span className={`inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full ${meta.color}`}>
      {meta.label}
    </span>
  )
}

function StatCard({ label, value, color, icon: Icon }) {
  return (
    <div className="glass rounded-xl p-4 flex items-center gap-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-xs text-gray-400">{label}</p>
      </div>
    </div>
  )
}

// ─── Create Ticket Modal ──────────────────────────────────────────────────────

function CreateTicketModal({ onClose, onCreate }) {
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'general',
    priority: 'medium',
  })
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState({})

  const validate = () => {
    const e = {}
    if (form.title.trim().length < 5) e.title = 'Title must be at least 5 characters'
    if (form.description.trim().length < 10) e.description = 'Description must be at least 10 characters'
    return e
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    try {
      setSubmitting(true)
      const res = await ticketAPI.createTicket(form)
      onCreate(res.data)
      toast.success('Ticket created — AI is analysing it!')
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create ticket')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-lg glass rounded-2xl p-8 shadow-2xl z-10"
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gradient">New Ticket</h2>
            <p className="text-sm text-gray-400 mt-0.5">AI will auto-generate a summary and solution</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-white/10 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Title</label>
            <input
              type="text"
              value={form.title}
              onChange={e => setForm({ ...form, title: e.target.value })}
              placeholder="Brief description of your issue"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition"
            />
            {errors.title && <p className="text-red-400 text-xs mt-1">{errors.title}</p>}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Description</label>
            <textarea
              value={form.description}
              onChange={e => setForm({ ...form, description: e.target.value })}
              placeholder="Describe your issue in detail..."
              rows={4}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition resize-none"
            />
            {errors.description && <p className="text-red-400 text-xs mt-1">{errors.description}</p>}
          </div>

          {/* Category + Priority row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Category</label>
              <select
                value={form.category}
                onChange={e => setForm({ ...form, category: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/50 transition"
              >
                <option value="general">General</option>
                <option value="technical">Technical</option>
                <option value="billing">Billing</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Priority</label>
              <select
                value={form.priority}
                onChange={e => setForm({ ...form, priority: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/50 transition"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 border border-white/20 rounded-lg hover:bg-white/5 transition text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 gradient-primary px-4 py-2.5 rounded-lg hover:opacity-90 transition text-sm font-semibold disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {submitting ? <Loader className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              {submitting ? 'Submitting…' : 'Submit Ticket'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}

// ─── Ticket Card ──────────────────────────────────────────────────────────────

function TicketCard({ ticket, onClick }) {
  const timeAgo = (date) => {
    const diff = Date.now() - new Date(date)
    const mins = Math.floor(diff / 60000)
    if (mins < 60) return `${mins}m ago`
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return `${hrs}h ago`
    return `${Math.floor(hrs / 24)}d ago`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      onClick={onClick}
      className="glass rounded-xl p-5 cursor-pointer hover:border-orange-500/30 hover:bg-white/[0.07] transition-all duration-200 group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {/* badges */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <StatusBadge status={ticket.status} />
            <PriorityBadge priority={ticket.priority} />
            <CategoryBadge category={ticket.category} />
          </div>

          {/* title */}
          <h3 className="font-semibold text-white truncate group-hover:text-orange-300 transition-colors">
            {ticket.title}
          </h3>

          {/* description preview */}
          <p className="text-sm text-gray-400 mt-1 line-clamp-2">{ticket.description}</p>

          {/* ai indicator */}
          {ticket.ai_summary && (
            <div className="mt-2 flex items-center gap-1.5 text-xs text-teal-400">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
              AI analysis available
            </div>
          )}
        </div>

        <div className="flex flex-col items-end gap-2 shrink-0">
          <span className="text-xs text-gray-500">{timeAgo(ticket.created_at)}</span>
          <span className="text-xs text-gray-600">#{ticket.id}</span>
          <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-orange-400 group-hover:translate-x-0.5 transition-all" />
        </div>
      </div>
    </motion.div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function Tickets() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const isAdmin = user?.role === 'admin'

  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [activeTab, setActiveTab] = useState('all')
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [showAdminAll, setShowAdminAll] = useState(false)

  // Stats derived from ticket list
  const stats = {
    total:       tickets.length,
    open:        tickets.filter(t => t.status === 'open').length,
    in_progress: tickets.filter(t => t.status === 'in_progress').length,
    resolved:    tickets.filter(t => t.status === 'resolved').length,
  }

  const fetchTickets = useCallback(async () => {
    try {
      setLoading(true)
      const res = isAdmin && showAdminAll
        ? await ticketAPI.getAllTickets(0, 100)
        : await ticketAPI.getTickets(0, 100)
      setTickets(res.data)
    } catch (err) {
      toast.error('Failed to load tickets')
    } finally {
      setLoading(false)
    }
  }, [isAdmin, showAdminAll])

  useEffect(() => { fetchTickets() }, [fetchTickets])

  const filtered = tickets.filter(t => {
    const matchStatus   = activeTab === 'all' || t.status === activeTab
    const matchCategory = categoryFilter === 'all' || t.category === categoryFilter
    const matchSearch   = !search ||
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase())
    return matchStatus && matchCategory && matchSearch
  })

  const handleCreate = (newTicket) => {
    setTickets(prev => [newTicket, ...prev])
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* ── Header ── */}
      <div className="glass sticky top-0 z-40 border-b border-white/10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Ticket className="w-6 h-6 text-orange-400" />
            <h1 className="text-2xl font-bold text-gradient">Support Tickets</h1>
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

      <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        {/* ── Stats ── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-2 sm:grid-cols-4 gap-4"
        >
          <StatCard label="Total Tickets"  value={stats.total}       color="bg-orange-500/20 text-orange-300" icon={Ticket} />
          <StatCard label="Open"           value={stats.open}        color="bg-blue-500/20 text-blue-300"     icon={AlertCircle} />
          <StatCard label="In Progress"    value={stats.in_progress} color="bg-amber-500/20 text-amber-300"   icon={Clock} />
          <StatCard label="Resolved"       value={stats.resolved}    color="bg-green-500/20 text-green-300"   icon={CheckCircle} />
        </motion.div>

        {/* ── Toolbar ── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between"
        >
          {/* Search */}
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search tickets…"
              className="w-full pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/50 transition"
            />
            {search && (
              <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2">
                <X className="w-3.5 h-3.5 text-gray-500 hover:text-white" />
              </button>
            )}
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Category filter */}
            <div className="flex items-center gap-1.5 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5">
              <Filter className="w-3.5 h-3.5 text-gray-400" />
              <select
                value={categoryFilter}
                onChange={e => setCategoryFilter(e.target.value)}
                className="bg-transparent text-sm focus:outline-none"
              >
                <option value="all">All Categories</option>
                <option value="general">General</option>
                <option value="technical">Technical</option>
                <option value="billing">Billing</option>
              </select>
            </div>

            {/* Admin toggle */}
            {isAdmin && (
              <button
                onClick={() => setShowAdminAll(v => !v)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border transition ${
                  showAdminAll
                    ? 'border-orange-500/50 bg-orange-500/10 text-orange-300'
                    : 'border-white/10 hover:bg-white/10'
                }`}
              >
                <ArrowUpDown className="w-3.5 h-3.5" />
                {showAdminAll ? 'All Users' : 'My Tickets'}
              </button>
            )}

            {/* Create button */}
            <button
              onClick={() => setShowCreate(true)}
              className="gradient-primary flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition glow"
            >
              <Plus className="w-4 h-4" />
              New Ticket
            </button>
          </div>
        </motion.div>

        {/* ── Status Tabs ── */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex gap-1 bg-white/5 rounded-xl p-1 w-fit"
        >
          {STATUS_TABS.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.key
                  ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-white/10'
              }`}
            >
              {tab.label}
              {tab.key !== 'all' && (
                <span className={`ml-1.5 text-xs ${activeTab === tab.key ? 'opacity-80' : 'opacity-50'}`}>
                  ({tickets.filter(t => t.status === tab.key).length})
                </span>
              )}
            </button>
          ))}
        </motion.div>

        {/* ── Ticket List ── */}
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <Loader className="w-8 h-8 animate-spin text-orange-400" />
          </div>
        ) : filtered.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass rounded-2xl p-16 text-center"
          >
            <Ticket className="w-14 h-14 mx-auto mb-4 text-gray-600" />
            <h3 className="text-xl font-semibold mb-2 text-gray-300">
              {search || categoryFilter !== 'all' || activeTab !== 'all'
                ? 'No matching tickets'
                : 'No tickets yet'}
            </h3>
            <p className="text-gray-500 mb-6 text-sm">
              {search || categoryFilter !== 'all' || activeTab !== 'all'
                ? 'Try adjusting your filters'
                : 'Submit a support request and our AI will help resolve it'}
            </p>
            {activeTab === 'all' && !search && categoryFilter === 'all' && (
              <button
                onClick={() => setShowCreate(true)}
                className="gradient-primary px-6 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition inline-flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Create First Ticket
              </button>
            )}
          </motion.div>
        ) : (
          <div className="space-y-3">
            {filtered.map((ticket, i) => (
              <motion.div
                key={ticket.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <TicketCard
                  ticket={ticket}
                  onClick={() => navigate(`/tickets/${ticket.id}`)}
                />
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* ── Create Modal ── */}
      <AnimatePresence>
        {showCreate && (
          <CreateTicketModal
            onClose={() => setShowCreate(false)}
            onCreate={handleCreate}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
