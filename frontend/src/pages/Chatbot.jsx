import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Box,
  Typography,
  TextField,
  IconButton,
  Paper,
  Container,
  Chip,
  Avatar,
  CircularProgress,
} from '@mui/material'
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import api from '../api/client'

const lagosRed = '#C8102E'

const generateSessionId = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

const Chatbot = () => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [chatHistory, setChatHistory] = useState([])
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    setSessionId(generateSessionId())
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping, scrollToBottom])

  const fetchSuggestions = useCallback(async () => {
    try {
      const response = await api.get('/chatbot/sessions/suggestions/')
      setSuggestions(response.data.suggestions || response.data || [])
    } catch (err) {
      console.error('Failed to load suggestions:', err)
    }
  }, [])

  const fetchChatHistory = useCallback(async () => {
    if (!sessionId) return
    try {
      const response = await api.get('/chatbot/sessions/history/')
      const sessions = response.data || []
      setChatHistory(sessions.map(s => ({
        session_id: s.id,
        preview: s.messages?.length > 0 ? s.messages[0].content?.substring(0, 50) || 'Chat' : 'New chat',
        messages: s.messages || [],
        created_at: s.created_at,
      })))
      const currentSession = sessions.find(s => String(s.id) === String(sessionId))
      if (currentSession) {
        const history = (currentSession.messages || []).map(m => ({
          role: m.role,
          message: m.content,
          timestamp: m.created_at,
        }))
        setMessages(history)
      }
    } catch (err) {
      console.error('Failed to load chat history:', err)
    }
  }, [sessionId])

  useEffect(() => {
    fetchSuggestions()
  }, [fetchSuggestions])

  useEffect(() => {
    if (sessionId) {
      fetchChatHistory()
    }
  }, [sessionId, fetchChatHistory])

  const sendMessage = useCallback(
    async (text) => {
      const message = text || input.trim()
      if (!message || isLoading) return

      const userMessage = {
        role: 'user',
        message,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, userMessage])
      setInput('')
      setIsLoading(true)
      setIsTyping(true)

      try {
        const response = await api.post('/chatbot/sessions/send/', {
          session_id: sessionId,
          message,
        })

        const botMessage = {
          role: 'assistant',
          message: response.data.reply || response.data.message || response.data.content,
          timestamp: new Date().toISOString(),
        }
        setMessages((prev) => [...prev, botMessage])
        if (response.data.suggestions) {
          setSuggestions(response.data.suggestions)
        }
      } catch (err) {
        console.error('Failed to send message:', err)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            message: 'Sorry, something went wrong. Please try again.',
            timestamp: new Date().toISOString(),
          },
        ])
      } finally {
        setIsLoading(false)
        setIsTyping(false)
        inputRef.current?.focus()
      }
    },
    [input, sessionId, isLoading]
  )

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion)
  }

  const startNewChat = () => {
    setSessionId(generateSessionId())
    setMessages([])
  }

  return (
    <Box sx={{ display: 'flex', height: 'calc(100vh - 64px)', overflow: 'hidden' }}>
      {/* Sidebar - Chat History */}
      <Paper
        elevation={0}
        sx={{
          width: 280,
          flexShrink: 0,
          borderRight: '1px solid #e0e0e0',
          display: 'flex',
          flexDirection: 'column',
          bgcolor: '#fafafa',
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
          <Typography variant="subtitle1" fontWeight={600}>
            Chat History
          </Typography>
        </Box>
        <Box sx={{ flex: 1, overflowY: 'auto', p: 1 }}>
          {chatHistory.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
              No previous chats
            </Typography>
          ) : (
            chatHistory.map((chat) => (
              <Paper
                key={chat.session_id}
                elevation={0}
                onClick={() => {
                  if (chat.session_id !== sessionId) {
                    setSessionId(chat.session_id)
                    setMessages(chat.messages)
                  }
                }}
                sx={{
                  p: 1.5,
                  mb: 1,
                  cursor: 'pointer',
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: chat.session_id === sessionId ? lagosRed : 'transparent',
                  bgcolor: chat.session_id === sessionId ? '#fff5f5' : '#fff',
                  '&:hover': {
                    borderColor: chat.session_id === sessionId ? lagosRed : '#ccc',
                    bgcolor: chat.session_id === sessionId ? '#fff5f5' : '#f5f5f5',
                  },
                  transition: 'all 0.15s ease',
                }}
              >
                <Typography variant="body2" noWrap sx={{ fontWeight: 500, mb: 0.5 }}>
                  {chat.preview}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(chat.created_at).toLocaleDateString()}
                </Typography>
              </Paper>
            ))
          )}
        </Box>
        <Box sx={{ p: 1.5, borderTop: '1px solid #e0e0e0' }}>
          <IconButton
            fullWidth
            onClick={startNewChat}
            sx={{
              justifyContent: 'center',
              gap: 1,
              textTransform: 'none',
              bgcolor: lagosRed,
              color: '#fff',
              borderRadius: 2,
              py: 1,
              '&:hover': { bgcolor: '#a00d24' },
            }}
          >
            <RefreshIcon fontSize="small" />
            <Typography variant="body2">New Chat</Typography>
          </IconButton>
        </Box>
      </Paper>

      {/* Main Chat Area */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Header */}
        <Box
          sx={{
            px: 3,
            py: 2,
            borderBottom: '1px solid #e0e0e0',
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            bgcolor: '#fff',
          }}
        >
          <Avatar sx={{ bgcolor: lagosRed, width: 36, height: 36 }}>
            <BotIcon fontSize="small" />
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={600} lineHeight={1.2}>
              AI Assistant
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Ask me anything about school management
            </Typography>
          </Box>
        </Box>

        {/* Messages */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            px: 3,
            py: 2,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            bgcolor: '#f9fafb',
          }}
        >
          {messages.length === 0 && !isTyping && (
            <Box
              sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 2,
              }}
            >
              <Avatar sx={{ bgcolor: lagosRed, width: 56, height: 56 }}>
                <BotIcon fontSize="medium" />
              </Avatar>
              <Typography variant="h5" fontWeight={600}>
                How can I help you today?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Choose a suggestion below or type your question
              </Typography>
            </Box>
          )}

          {messages.map((msg, index) => {
            const isUser = msg.role === 'user'
            return (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: isUser ? 'flex-end' : 'flex-start',
                  gap: 1,
                  alignItems: 'flex-end',
                }}
              >
                {!isUser && (
                  <Avatar
                    sx={{
                      bgcolor: '#e0e0e0',
                      color: '#616161',
                      width: 32,
                      height: 32,
                    }}
                  >
                    <BotIcon fontSize="small" />
                  </Avatar>
                )}
                <Paper
                  elevation={0}
                  sx={{
                    maxWidth: '70%',
                    px: 2,
                    py: 1.5,
                    borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                    bgcolor: isUser ? lagosRed : '#fff',
                    color: isUser ? '#fff' : 'text.primary',
                    border: isUser ? 'none' : '1px solid #e0e0e0',
                    wordBreak: 'break-word',
                  }}
                >
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {msg.message}
                  </Typography>
                  {msg.timestamp && (
                    <Typography
                      variant="caption"
                      sx={{
                        display: 'block',
                        mt: 0.5,
                        opacity: 0.7,
                        fontSize: '0.65rem',
                      }}
                    >
                      {new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Typography>
                  )}
                </Paper>
                {isUser && (
                  <Avatar sx={{ bgcolor: lagosRed, width: 32, height: 32 }}>
                    <PersonIcon fontSize="small" />
                  </Avatar>
                )}
              </Box>
            )
          })}

          {/* Typing Indicator */}
          {isTyping && (
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
              <Avatar sx={{ bgcolor: '#e0e0e0', color: '#616161', width: 32, height: 32 }}>
                <BotIcon fontSize="small" />
              </Avatar>
              <Paper
                elevation={0}
                sx={{
                  px: 2,
                  py: 1.5,
                  borderRadius: '16px 16px 16px 4px',
                  bgcolor: '#fff',
                  border: '1px solid #e0e0e0',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                <CircularProgress size={14} sx={{ color: lagosRed }} />
                <Typography variant="body2" color="text.secondary">
                  Thinking...
                </Typography>
              </Paper>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        {/* Suggestions */}
        {messages.length <= 1 && suggestions.length > 0 && (
          <Box
            sx={{
              px: 3,
              pb: 1,
              display: 'flex',
              flexWrap: 'wrap',
              gap: 1,
            }}
          >
            {suggestions.map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                onClick={() => handleSuggestionClick(suggestion)}
                variant="outlined"
                sx={{
                  borderColor: '#ccc',
                  bgcolor: '#fff',
                  '&:hover': {
                    borderColor: lagosRed,
                    bgcolor: '#fff5f5',
                  },
                  transition: 'all 0.15s ease',
                }}
              />
            ))}
          </Box>
        )}

        {/* Input Area */}
        <Box
          sx={{
            px: 3,
            py: 2,
            borderTop: '1px solid #e0e0e0',
            bgcolor: '#fff',
          }}
        >
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <TextField
              inputRef={inputRef}
              fullWidth
              multiline
              maxRows={4}
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              variant="outlined"
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  bgcolor: '#f9fafb',
                  '& fieldset': { borderColor: '#e0e0e0' },
                  '&:hover fieldset': { borderColor: '#bdbdbd' },
                  '&.Mui-focused fieldset': { borderColor: lagosRed },
                },
              }}
            />
            <IconButton
              onClick={() => sendMessage()}
              disabled={!input.trim() || isLoading}
              sx={{
                bgcolor: lagosRed,
                color: '#fff',
                width: 40,
                height: 40,
                '&:hover': { bgcolor: '#a00d24' },
                '&.Mui-disabled': { bgcolor: '#e0e0e0', color: '#9e9e9e' },
              }}
            >
              {isLoading ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : <SendIcon />}
            </IconButton>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default Chatbot
