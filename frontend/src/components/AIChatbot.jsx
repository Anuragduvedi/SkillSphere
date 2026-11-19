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
  Camera,
  FileText,
  Briefcase,
  HelpCircle,
  Globe,
  AlertCircle,
  Clock,
  Compass,
  Film,
  Code
} from 'lucide-react';
import { chatbotAPI } from '../services/api';

const DEFAULT_WELCOME_MESSAGE = {
  id: 'welcome',
  role: 'model',
  content:
    "Hey! 😄 What's on your mind today? We can chat casually about your day, movies, tech, coding roadmaps, or check your SkillSphere jobs and assessments! Hindi, Punjabi, English or Hinglish – I'm comfortable with all!",
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
};

const MULTILINGUAL_QUICK_PROMPTS = [
  { icon: Sparkles, label: 'Ki haal aa veere? 🙏', prompt: 'ki haal aa veere?' },
  { icon: Film, label: 'Thriller Movies 🍿', prompt: 'suggest me some thriller movies' },
  { icon: Code, label: 'Learn Python 🐍', prompt: 'bro mujhe Python seekhni hai' },
  { icon: Compass, label: 'Mera Status Kya Hai?', prompt: 'Mera status kya hai aur agla step kya hai?' },
  { icon: FileText, label: 'Pending Assessment 📝', prompt: 'mera assessment pending hai, ab kya karun?' },
  { icon: ShieldAlert, label: 'AI 3-Strike Rules 🛡️', prompt: 'What are the AI proctoring rules and three-strike policy?' },
];

export default function AIChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  
  // Restore session chat history if present
  const [messages, setMessages] = useState(() => {
    try {
      const saved = sessionStorage.getItem('skillsphere_chat_history');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Could not read session chat history:', e);
    }
    return [DEFAULT_WELCOME_MESSAGE];
  });

  const [isLoading, setIsLoading] = useState(false);
  const [botStatus, setBotStatus] = useState({ online: true, mode: 'Native AI Engine' });
  const [unreadCount, setUnreadCount] = useState(0);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Persist messages to sessionStorage
  useEffect(() => {
    try {
      sessionStorage.setItem('skillsphere_chat_history', JSON.stringify(messages));
    } catch (e) {
      // Ignore quota storage issues
    }
  }, [messages]);

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

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 250);
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
            mode: res.data.gemini_configured ? 'Gemini 1.5' : 'Native AI Engine',
          });
        }
      } catch (err) {
        setBotStatus({ online: true, mode: 'Native AI Engine' });
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
      // Build conversation history of prior turns for backend context
      const historyPayload = messages
        .filter((m) => m.id !== 'welcome')
        .slice(-10)
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
          content: replyData.reply || 'I am here to guide you with your applications and assessments.',
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
            "⚠️ **Service Note:** I am temporarily having trouble reaching the main network, but here is quick help:\n\n- **Assessments:** 20 technical questions, 25-minute timer, 60% passing mark.\n- **Camera:** Grant permission in your browser address bar and face the camera.\n- **3-Strike Rules:** Strike 1 Yellow Warning, Strike 2 Orange Warning, Strike 3 Red Auto-Submission.",
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
    const resetMessages = [
      {
        id: 'welcome_' + Date.now(),
        role: 'model',
        content:
          "✨ **Chat history cleared.**\n\nHey again! What would you like to know about SkillSphere jobs, assessments, or your status? Ask in English, Hindi, Punjabi or Hinglish!",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ];
    setMessages(resetMessages);
    sessionStorage.removeItem('skillsphere_chat_history');
  };

  // Helper to render basic markdown formatting cleanly
  const renderFormattedContent = (content) => {
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      // Headers
      if (line.startsWith('### ')) {
        return (
          <h4 key={idx} className="text-sm font-bold text-cyan-300 mt-2.5 mb-1">
            {line.replace('### ', '')}
          </h4>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h3 key={idx} className="text-sm font-bold text-white mt-2 mb-1">
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
          <div key={idx} className="flex items-start gap-1.5 my-0.5 text-xs text-slate-200 pl-1 leading-relaxed">
            <span className="text-cyan-400 mt-0.5 shrink-0">•</span>
            <span>{parseInlineMarkdown(itemText)}</span>
          </div>
        );
      }
      // Numbered lists
      const numMatch = line.trim().match(/^(\d+)\.\s+(.*)/);
      if (numMatch) {
        return (
          <div key={idx} className="flex items-start gap-1.5 my-0.5 text-xs text-slate-200 pl-1 leading-relaxed">
            <span className="font-mono text-cyan-400 text-[11px] shrink-0">{numMatch[1]}.</span>
            <span>{parseInlineMarkdown(numMatch[2])}</span>
          </div>
        );
      }
      if (!line.trim()) {
        return <div key={idx} className="h-1.5" />;
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
      const boldMatch = remaining.match(/\*\*(.*?)\*\*/);
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
            <code key={keyIdx++} className="px-1.5 py-0.5 rounded bg-black/50 text-cyan-300 font-mono text-[11px] border border-white/5">
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
              className="relative group p-4 rounded-full bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 text-white shadow-2xl shadow-cyan-500/30 border border-cyan-400/50 backdrop-blur-md flex items-center justify-center cursor-pointer"
              aria-label="Open SkillSphere AI Chatbot"
            >
              {/* Glowing animated ping rings */}
              <span className="absolute -inset-1 rounded-full bg-gradient-to-r from-cyan-400 to-indigo-500 opacity-40 blur-md group-hover:opacity-80 transition duration-500 animate-pulse" />
              
              <Bot className="w-6 h-6 text-white relative z-10" />

              {/* Unread badge */}
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 px-1.5 py-0.5 rounded-full bg-rose-500 text-white text-[10px] font-bold shadow-md z-20">
                  {unreadCount}
                </span>
              )}

              {/* Tooltip on hover */}
              <span className="absolute right-full mr-3 px-3 py-1.5 rounded-xl bg-slate-900/90 text-xs font-semibold text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity border border-white/10 shadow-lg pointer-events-none hidden sm:block">
                SkillSphere AI Assistant 🌐
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
                height: isMinimized ? 'auto' : '640px',
              }}
              exit={{ opacity: 0, y: 30, scale: 0.95 }}
              transition={{ duration: 0.22 }}
              className="w-[94vw] sm:w-[440px] max-w-[440px] rounded-3xl bg-dark-900/95 border border-cyan-500/30 backdrop-blur-2xl shadow-2xl shadow-cyan-950/60 flex flex-col overflow-hidden"
              style={{ maxHeight: '85vh' }}
            >
              {/* Header */}
              <div className="p-4 bg-gradient-to-r from-cyan-950/70 via-slate-900/90 to-indigo-950/70 border-b border-cyan-500/20 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-400 to-indigo-600 flex items-center justify-center text-black font-black shadow-md shadow-cyan-500/20">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-dark-900" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-white tracking-tight">SkillSphere AI</h3>
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                        {botStatus.mode}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 flex items-center gap-1">
                      <Globe className="w-3 h-3 text-cyan-400" />
                      <span>Hindi • Punjabi • English • Hinglish</span>
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
                            {isUser ? <User className="w-3.5 h-3.5 text-black" /> : <Bot className="w-3.5 h-3.5" />}
                          </div>

                          {/* Message Bubble */}
                          <div className={`max-w-[84%] ${isUser ? 'text-right' : 'text-left'}`}>
                            <div
                              className={`p-3.5 rounded-2xl text-xs leading-relaxed ${
                                isUser
                                  ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white rounded-tr-none shadow-md shadow-cyan-600/10'
                                  : 'bg-white/5 border border-white/10 text-slate-200 rounded-tl-none shadow-sm'
                              }`}
                            >
                              {isUser ? (
                                <p className="whitespace-pre-wrap">{msg.content}</p>
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
                          <span className="text-[11px] text-slate-400 ml-1">Thinking...</span>
                        </div>
                      </div>
                    )}

                    <div ref={messagesEndRef} />
                  </div>

                  {/* Multilingual Quick Prompts Bar */}
                  <div className="px-4 py-2 border-t border-white/5 bg-slate-950/50">
                    <div className="flex items-center justify-between mb-1.5">
                      <p className="text-[10px] uppercase font-bold tracking-wider text-slate-400 flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-cyan-400" />
                        Suggested Questions
                      </p>
                      <span className="text-[10px] text-cyan-300">Tap to Ask</span>
                    </div>
                    <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
                      {MULTILINGUAL_QUICK_PROMPTS.map((qp, idx) => {
                        const Icon = qp.icon;
                        return (
                          <button
                            key={idx}
                            disabled={isLoading}
                            onClick={() => handleSendMessage(qp.prompt)}
                            className="shrink-0 px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-cyan-500/15 border border-white/10 hover:border-cyan-500/40 text-[11px] text-slate-300 hover:text-cyan-300 transition-colors flex items-center gap-1.5 disabled:opacity-50"
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
                        placeholder="Chat casually, ask anything, or inquire about jobs & tests..."
                        className="flex-1 px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 text-xs text-white placeholder-slate-500 disabled:opacity-50"
                      />
                      <button
                        onClick={() => handleSendMessage()}
                        disabled={!inputMessage.trim() || isLoading}
                        className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 transition-all shadow-md shadow-cyan-500/20 shrink-0 cursor-pointer"
                        aria-label="Send Message"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-[10px] text-slate-500 text-center mt-2 flex items-center justify-center gap-1">
                      <span>Conversational AI Assistant</span>
                      <span>•</span>
                      <span>General Chat & SkillSphere Intelligence</span>
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
