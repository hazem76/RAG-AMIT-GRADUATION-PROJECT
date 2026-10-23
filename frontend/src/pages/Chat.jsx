import React, { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { MessageCircle, Plus, LogOut, Send, Loader, Trash2, Edit2, Check, X } from 'lucide-react'
import useAuthStore from '../store/authStore'
import { chatAPI } from '../services/api'

export default function Chat() {
  const navigate = useNavigate()
  const { chatId } = useParams()
  const { user, logout } = useAuthStore()

  const [chats, setChats] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingChats, setLoadingChats] = useState(true)
  const [editingChatId, setEditingChatId] = useState(null)
  const [editingTitle, setEditingTitle] = useState('')
  const messagesEndRef = useRef(null)

  // Load chats on mount
  useEffect(() => {
    fetchChats()
  }, [])

  // Auto-select chat from URL or first chat
  useEffect(() => {
    if (chatId && chats.length > 0) {
      const chat = chats.find(c => c.id === parseInt(chatId))
      if (chat) {
        selectChat(chat.id)
      }
    } else if (chats.length > 0 && !currentChat) {
      selectChat(chats[0].id)
    }
  }, [chats, chatId])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchChats = async () => {
    try {
      setLoadingChats(true)
      const response = await chatAPI.getChats(0, 50)
      setChats(response.data)
    } catch (error) {
      console.error('Error fetching chats:', error)
    } finally {
      setLoadingChats(false)
    }
  }

  const selectChat = async (chatId) => {
    try {
      setLoading(true)
      const response = await chatAPI.getChat(chatId)
      setCurrentChat({ ...response.data, id: chatId })
      setMessages(response.data.messages || [])
      navigate(`/chat/${chatId}`)
    } catch (error) {
      console.error('Error loading chat:', error)
    } finally {
      setLoading(false)
    }
  }

  const createNewChat = async () => {
    try {
      const response = await chatAPI.createChat({ title: 'New Chat' })
      const newChat = response.data
      setChats([newChat, ...chats])
      selectChat(newChat.id)
    } catch (error) {
      console.error('Error creating chat:', error)
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || !currentChat || loading) return

    const userMessage = inputValue
    setInputValue('')

    try {
      setLoading(true)
      // Add user message optimistically
      setMessages([...messages, { role: 'user', content: userMessage, id: Date.now() }])

      // Send to API
      const response = await chatAPI.sendMessage(currentChat.id, {
        query: userMessage,
        top_k: 5
      })

      // Add assistant message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.answer,
        confidence_score: response.data.confidence_score,
        citations: response.data.citations,
        id: Date.now() + 1
      }])

      // Refresh chat to get updated messages
      const updatedChat = await chatAPI.getChat(currentChat.id)
      setMessages(updatedChat.data.messages || [])
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your message. Please try again.',
        id: Date.now() + 1
      }])
    } finally {
      setLoading(false)
    }
  }

  const deleteChat = async (chatId) => {
    if (!window.confirm('Delete this chat?')) return
    try {
      await chatAPI.deleteChat(chatId)
      setChats(chats.filter(c => c.id !== chatId))
      if (currentChat?.id === chatId) {
        if (chats.length > 1) {
          selectChat(chats[0].id)
        } else {
          setCurrentChat(null)
          setMessages([])
          navigate('/chat')
        }
      }
    } catch (error) {
      console.error('Error deleting chat:', error)
    }
  }

  const updateChatTitle = async (chatId, newTitle) => {
    try {
      await chatAPI.updateTitle(chatId, newTitle)
      setChats(chats.map(c => c.id === chatId ? { ...c, title: newTitle } : c))
      if (currentChat?.id === chatId) {
        setCurrentChat({ ...currentChat, title: newTitle })
      }
      setEditingChatId(null)
    } catch (error) {
      console.error('Error updating chat title:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex flex-col">
      {/* Header */}
      <div className="glass sticky top-0 z-50 border-b border-white/10">
        <div className="mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gradient">Chat</h1>
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
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - Chats List */}
        <div className="w-64 bg-black/20 border-r border-white/10 flex flex-col overflow-hidden">
          <div className="p-4 border-b border-white/10">
            <button
              onClick={createNewChat}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 gradient-primary rounded-lg hover:opacity-90 transition"
            >
              <Plus className="w-4 h-4" />
              New Chat
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
            {loadingChats ? (
              <div className="flex justify-center items-center h-full">
                <Loader className="w-5 h-5 animate-spin" />
              </div>
            ) : chats.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                <p>No chats yet</p>
              </div>
            ) : (
              <div className="space-y-2 p-4">
                {chats.map(chat => (
                  <div
                    key={chat.id}
                    className={`p-3 rounded-lg cursor-pointer transition group ${
                      currentChat?.id === chat.id
                        ? 'bg-purple-600/50 border border-purple-400'
                        : 'hover:bg-white/10'
                    }`}
                  >
                    {editingChatId === chat.id ? (
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          className="flex-1 bg-white/10 rounded px-2 py-1 text-sm"
                          autoFocus
                        />
                        <button
                          onClick={() => updateChatTitle(chat.id, editingTitle)}
                          className="p-1 hover:bg-white/20 rounded"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setEditingChatId(null)}
                          className="p-1 hover:bg-white/20 rounded"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex justify-between items-start">
                        <div
                          onClick={() => selectChat(chat.id)}
                          className="flex-1 min-w-0"
                        >
                          <p className="text-sm font-medium truncate">{chat.title}</p>
                          <p className="text-xs text-gray-400">
                            {new Date(chat.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="opacity-0 group-hover:opacity-100 flex gap-1 ml-2">
                          <button
                            onClick={() => {
                              setEditingChatId(chat.id)
                              setEditingTitle(chat.title)
                            }}
                            className="p-1 hover:bg-white/20 rounded"
                          >
                            <Edit2 className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => deleteChat(chat.id)}
                            className="p-1 hover:bg-red-500/20 rounded"
                          >
                            <Trash2 className="w-3 h-3 text-red-400" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat Area */}
        {currentChat ? (
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <MessageCircle className="w-12 h-12 mx-auto text-gray-500 mb-4" />
                    <p className="text-gray-400">Start a conversation</p>
                  </div>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-md px-4 py-2 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-purple-600/50 text-white'
                          : 'bg-white/10 text-gray-100'
                      }`}
                    >
                      <p className="text-sm">{msg.content}</p>
                      {msg.confidence_score !== undefined && (
                        <p className="text-xs text-gray-400 mt-1">
                          Confidence: {(msg.confidence_score * 100).toFixed(0)}%
                        </p>
                      )}
                    </div>
                  </motion.div>
                ))
              )}
              {loading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="bg-white/10 px-4 py-2 rounded-lg flex items-center gap-2">
                    <Loader className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-white/10 bg-black/20 p-4">
              <form onSubmit={sendMessage} className="flex gap-3">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask a question..."
                  disabled={loading}
                  className="flex-1 bg-white/10 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={loading || !inputValue.trim()}
                  className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-2 rounded-lg flex items-center gap-2 transition"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 mx-auto text-gray-500 mb-4" />
              <p className="text-gray-400">Select a chat or create a new one to get started</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
