import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  X,
  Send,
  Sparkles,
  Bot,
  User,
  ShieldAlert,
  RotateCcw,
  Minimize2,
  Maximize2,
  ChevronRight,
  HelpCircle,
  Camera,
  FileText,
  AlertTriangle
} from 'lucide-react';
import { chatbotAPI } from '../services/api';

const QUICK_PROMPTS = [
  { icon: ShieldAlert, label: '3-Strike Proctoring Rules', prompt: 'What are the AI proctoring rules and three-strike policy?' },
  { icon: FileText, label: '20-Question Assessments', prompt: 'How do the 20-question technical assessments work?' },
  { icon: Camera, label: 'Camera Troubleshooting', prompt: 'My camera is not working or not detected. How can I fix it?' },
  { icon: Sparkles, label: 'Resume OCR & Matching', prompt: 'How does resume OCR parsing and skill match scoring work?' },
];

export default function AIChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'model',
      content:
        "👋 **Welcome to SkillSphere AI Assistant!**\n\nI can answer questions regarding our **20-Question Technical Assessments**, **MediaPipe AI Camera Proctoring & Three-Strike rules**, **Resume OCR extraction**, or help you troubleshoot camera and platform issues.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [botStatus, setBotStatus] = useState({ online: true, mode: 'Gemini AI' });
  const [unreadCount, setUnreadCount] = useState(0);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen && !isMinimized) {
      scrollToBottom();
      setUnreadCount(0);
    }
  }, [messages, isOpen, isMinimized]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [isOpen, isMinimized]);

  // Check backend chatbot status on mount
  useEffect(() => {
    async function checkStatus() {
      try {
        const res = await chatbotAPI.getStatus();
        if (res.data) {
          setBotStatus({
            online: res.data.status === 'online',
            mode: res.data.mode || 'Gemini 1.5/2.0 API',
          });
        }
      } catch (err) {
        // Fallback engine remains available
        setBotStatus({ online: true, mode: 'SkillSphere Native AI' });
      }
    }
    checkStatus();
  }, []);

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    const userMsgId = 'usr_' + Date.now();
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const newMessages = [
      ...messages,
      {
        id: userMsgId,
        role: 'user',
        content: text,
        timestamp: timeStr,
      },
    ];

    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Build lightweight conversation history
      const historyPayload = newMessages
        .filter((m) => m.id !== 'welcome')
        .slice(-6)
        .map((m) => ({
          role: m.role,
          content: m.content,
        }));

      const response = await chatbotAPI.sendMessage(text, historyPayload);
      const replyData = response.data;

      setMessages((prev) => [
        ...prev,
        {
          id: 'bot_' + Date.now(),
          role: 'model',
          content: replyData.reply || 'I am here to assist with SkillSphere assessments and proctoring.',
          provider: replyData.provider,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (error) {
      console.error('Chatbot API error:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: 'bot_err_' + Date.now(),
          role: 'model',
          content:
            "⚠️ **Temporary Service Notice:** I was unable to connect to the cloud AI service. However, our built-in rules system is active:\n\n- **Technical Assessment:** 20 questions, 25 minutes limit, 60% passing mark.\n- **Camera Proctoring:** 3-strike policy (Strike 1: Yellow Warning, Strike 2: Final Warning, Strike 3: Immediate Auto-Submission).\n- **Camera Setup:** Grant camera access in your browser bar and keep your face visible in frame.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome_reset',
        role: 'model',
        content:
          "✨ **Chat history reset.**\n\nHow can I help you today with assessments, camera proctoring, or technical questions?",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  // Helper to render basic markdown formatting cleanly
  const renderFormattedContent = (content) => {
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      // Headers
      if (line.startsWith('### ')) {
        return (
          <h4 key={idx} className="text-sm font-bold text-cyan-300 mt-2 mb-1">
            {line.replace('### ', '')}
          </h4>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h3 key={idx} className="text-base font-bold text-white mt-2 mb-1">
            {line.replace('## ', '')}
          </h3>
        );
      }
      // Blockquotes
      if (line.startsWith('> ')) {
        return (
          <div key={idx} className="my-1.5 p-2 rounded-lg bg-cyan-500/10 border-l-2 border-cyan-400 text-xs text-cyan-200">
            {line.replace('> ', '')}
          </div>
        );
      }
      // List items
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        const itemText = line.trim().substring(2);
        return (
          <div key={idx} className="flex items-start gap-1.5 my-0.5 text-xs text-slate-300 pl-1">
            <span className="text-cyan-400 mt-0.5">•</span>
            <span>{parseInlineMarkdown(itemText)}</span>
          </div>
        );
      }
      // Numbered lists
      const numMatch = line.trim().match(/^(\d+)\.\s+(.*)/);
      if (numMatch) {
        return (
          <div key={idx} className="flex items-start gap-1.5 my-0.5 text-xs text-slate-300 pl-1">
            <span className="font-mono text-cyan-400 text-[11px] shrink-0">{numMatch[1]}.</span>
            <span>{parseInlineMarkdown(numMatch[2])}</span>
          </div>
        );
      }
      if (!line.trim()) {
        return <div key={idx} className="h-1" />;
      }
      return (
        <p key={idx} className="text-xs text-slate-200 my-0.5 leading-relaxed">
          {parseInlineMarkdown(line)}
        </p>
      );
    });
  };

  // Helper for inline **bold** and `code`
  const parseInlineMarkdown = (text) => {
    const parts = [];
    let remaining = text;
    let keyIdx = 0;

    while (remaining.length > 0) {
      // Match **bold**
      const boldMatch = remaining.match(/\*\*(.*?)\*\*/);
      // Match `code`
      const codeMatch = remaining.match(/`(.*?)`/);

      let firstMatch = null;
      let matchType = null;

      if (boldMatch && (!codeMatch || boldMatch.index < codeMatch.index)) {
        firstMatch = boldMatch;
        matchType = 'bold';
      } else if (codeMatch) {
        firstMatch = codeMatch;
        matchType = 'code';
      }

      if (firstMatch && firstMatch.index !== undefined) {
        if (firstMatch.index > 0) {
          parts.push(remaining.substring(0, firstMatch.index));
        }
        if (matchType === 'bold') {
          parts.push(
            <strong key={keyIdx++} className="font-semibold text-white">
              {firstMatch[1]}
            </strong>
          );
        } else if (matchType === 'code') {
          parts.push(
            <code key={keyIdx++} className="px-1 py-0.5 rounded bg-black/40 text-cyan-300 font-mono text-[11px]">
              {firstMatch[1]}
            </code>
          );
        }
        remaining = remaining.substring(firstMatch.index + firstMatch[0].length);
      } else {
        parts.push(remaining);
        break;
      }
    }

    return parts;
  };

  return (
    <>
      {/* Floating Action Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <AnimatePresence>
          {!isOpen && (
            <motion.button
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setIsOpen(true);
                setIsMinimized(false);
              }}
              className="relative group p-4 rounded-full bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 text-white shadow-xl shadow-cyan-500/25 border border-cyan-400/40 backdrop-blur-md flex items-center justify-center"
              aria-label="Open SkillSphere AI Chatbot"
            >
              {/* Glowing animated ping rings */}
              <span className="absolute -inset-1 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 opacity-40 blur-sm group-hover:opacity-80 transition duration-500 animate-pulse" />
              
              <Bot className="w-6 h-6 text-white relative z-10" />

              {/* Unread badge */}
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 px-1.5 py-0.5 rounded-full bg-rose-500 text-white text-[10px] font-bold shadow-md">
                  {unreadCount}
                </span>
              )}

              {/* Tooltip on hover */}
              <span className="absolute right-full mr-3 px-3 py-1.5 rounded-xl bg-slate-900/90 text-xs font-semibold text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity border border-white/10 shadow-lg pointer-events-none">
                SkillSphere AI Assistant
              </span>
            </motion.button>
          )}
        </AnimatePresence>

        {/* Chat Window */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: 30, scale: 0.95 }}
              animate={{
                opacity: 1,
                y: 0,
                scale: 1,
                height: isMinimized ? 'auto' : '620px',
              }}
              exit={{ opacity: 0, y: 30, scale: 0.95 }}
              transition={{ duration: 0.22 }}
              className="w-[92vw] sm:w-[420px] max-w-[420px] rounded-2xl bg-dark-900/95 border border-cyan-500/30 backdrop-blur-2xl shadow-2xl shadow-cyan-950/50 flex flex-col overflow-hidden"
              style={{ maxHeight: '82vh' }}
            >
              {/* Header */}
              <div className="p-4 bg-gradient-to-r from-cyan-950/60 via-slate-900/80 to-blue-950/60 border-b border-cyan-500/20 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-black font-black shadow-md shadow-cyan-500/20">
                      <Bot className="w-5 h-5 text-black" />
                    </div>
                    <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-dark-900" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-white tracking-tight">SkillSphere AI</h3>
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                        {botStatus.mode.includes('Gemini') ? 'Gemini 1.5' : 'Native AI'}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      Ready to assist • 24/7
                    </p>
                  </div>
                </div>

                {/* Header Controls */}
                <div className="flex items-center gap-1">
                  <button
                    onClick={clearChat}
                    title="Clear Conversation"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setIsMinimized(!isMinimized)}
                    title={isMinimized ? 'Expand' : 'Minimize'}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                  >
                    {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    title="Close Chat"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Body (hidden when minimized) */}
              {!isMinimized && (
                <>
                  {/* Messages Scroll Area */}
                  <div className="flex-1 p-4 overflow-y-auto space-y-3.5 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                    {messages.map((msg) => {
                      const isUser = msg.role === 'user';
                      return (
                        <div
                          key={msg.id}
                          className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
                        >
                          {/* Avatar */}
                          <div
                            className={`w-7 h-7 rounded-lg shrink-0 flex items-center justify-center text-xs ${
                              isUser
                                ? 'bg-cyan-500 text-black font-bold shadow-sm'
                                : 'bg-slate-800 text-cyan-400 border border-cyan-500/30'
                            }`}
                          >
                            {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                          </div>

                          {/* Message Bubble */}
                          <div className={`max-w-[82%] ${isUser ? 'text-right' : 'text-left'}`}>
                            <div
                              className={`p-3 rounded-2xl text-xs ${
                                isUser
                                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-tr-none shadow-md shadow-cyan-600/10'
                                  : 'bg-white/5 border border-white/10 text-slate-200 rounded-tl-none shadow-sm'
                              }`}
                            >
                              {isUser ? (
                                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                              ) : (
                                renderFormattedContent(msg.content)
                              )}
                            </div>
                            <span className="text-[10px] text-slate-500 mt-1 px-1 inline-block">
                              {msg.timestamp}
                            </span>
                          </div>
                        </div>
                      );
                    })}

                    {/* Typing Animation */}
                    {isLoading && (
                      <div className="flex items-start gap-2.5">
                        <div className="w-7 h-7 rounded-lg bg-slate-800 text-cyan-400 border border-cyan-500/30 shrink-0 flex items-center justify-center">
                          <Bot className="w-3.5 h-3.5" />
                        </div>
                        <div className="p-3 rounded-2xl rounded-tl-none bg-white/5 border border-white/10 flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                      </div>
                    )}

                    <div ref={messagesEndRef} />
                  </div>

                  {/* Quick Prompts Bar */}
                  <div className="px-4 py-2 border-t border-white/5 bg-slate-950/40">
                    <p className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-1.5 flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-cyan-400" />
                      Quick Questions
                    </p>
                    <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
                      {QUICK_PROMPTS.map((qp, idx) => {
                        const Icon = qp.icon;
                        return (
                          <button
                            key={idx}
                            disabled={isLoading}
                            onClick={() => handleSendMessage(qp.prompt)}
                            className="shrink-0 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-cyan-500/10 border border-white/10 hover:border-cyan-500/30 text-[11px] text-slate-300 hover:text-cyan-300 transition-colors flex items-center gap-1.5 disabled:opacity-50"
                          >
                            <Icon className="w-3 h-3 text-cyan-400" />
                            <span>{qp.label}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Input Box */}
                  <div className="p-3 border-t border-white/10 bg-dark-900/90">
                    <div className="flex items-center gap-2">
                      <input
                        ref={inputRef}
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={isLoading}
                        placeholder="Ask about proctoring, 20-question tests, rules..."
                        className="flex-1 px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-xs text-white placeholder-slate-500 disabled:opacity-50"
                      />
                      <button
                        onClick={() => handleSendMessage()}
                        disabled={!inputMessage.trim() || isLoading}
                        className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-black font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 transition-all shadow-md shadow-cyan-500/20 shrink-0"
                        aria-label="Send Message"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-[10px] text-slate-500 text-center mt-2">
                      SkillSphere AI Assistant • Powered by Google Gemini API
                    </p>
                  </div>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
}
