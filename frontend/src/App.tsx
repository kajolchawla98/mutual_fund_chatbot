import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Sparkles, TrendingUp, Shield, Zap } from 'lucide-react';
import axios from 'axios';

// Basic Types
type Message = {
  id: string;
  type: 'bot' | 'user';
  text: string;
  footer?: string;
  citationUrl?: string;
};

const SAMPLE_QUESTIONS = [
  "What is the exit load for HDFC Mid-Cap fund?",
  "What is the minimum SIP for Motilal Oswal Small Cap?",
  "Tell me the expense ratio of ICICI Prudential Bluechip.",
];

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async (textToProcess?: string) => {
    const query = textToProcess || input;
    if (!query.trim()) return;

    setHasStarted(true);

    // Add user message
    const userMsg: Message = { id: Date.now().toString(), type: 'user', text: query };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await axios.post(`${apiBaseUrl}/chat/query`, {
        session_id: 'session_' + Date.now(),
        user_message: query,
      });

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: response.data.answer_text,
        footer: response.data.last_updated_date
          ? `Last updated from sources: ${response.data.last_updated_date}`
          : undefined,
        citationUrl: response.data.citation_url || undefined,
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error(error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: 'Sorry, I am having trouble connecting to the factual database right now. Please try again in a moment.',
        footer: `Last updated from sources: ${new Date().toISOString().split('T')[0]}`,
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const parseMarkdownLink = (text: string) => {
    const parts = text.split(/(\[.*?\]\(.*?\))/g);
    return parts.map((part, i) => {
      const match = part.match(/\[(.*?)\]\((.*?)\)/);
      if (match) {
        return (
          <a key={i} href={match[2]} target="_blank" rel="noopener noreferrer" className="chat-link">
            {match[1]}
          </a>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="app-shell">
      {/* Ambient background effects */}
      <div className="ambient-glow glow-1" />
      <div className="ambient-glow glow-2" />
      <div className="ambient-glow glow-3" />
      <div className="ambient-glow glow-4" />

      {/* Header */}
      <header className="app-header" id="main-header">
        <div className="header-brand">
          <div className="brand-icon">
            <TrendingUp size={20} />
          </div>
          <h1 className="brand-title">MF Assist</h1>
          <span className="brand-badge">AI Powered</span>
        </div>
        <div className="header-status">
          <span className="status-dot" />
          <span className="status-text">Connected to Official Sources</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {!hasStarted ? (
          /* Welcome Screen */
          <div className="welcome-screen">
            <div className="welcome-hero">
              <div className="welcome-icon-wrapper">
                <Bot size={40} />
                <div className="welcome-icon-ring" />
              </div>
              <h2 className="welcome-title">
                Mutual Fund <span className="text-gradient">Assistant</span>
              </h2>
              <p className="welcome-subtitle">
                Get factual information about mutual funds directly from official AMC sources. No investment advice — just verified data.
              </p>
            </div>

            {/* Feature cards */}
            <div className="feature-cards">
              <div className="feature-card">
                <div className="feature-icon">
                  <Shield size={20} />
                </div>
                <h3>Facts Only</h3>
                <p>Data sourced from official fund documents and AMC websites</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">
                  <Zap size={20} />
                </div>
                <h3>Instant Answers</h3>
                <p>RAG-powered retrieval for accurate, real-time responses</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">
                  <Sparkles size={20} />
                </div>
                <h3>AI Powered</h3>
                <p>LLM-enhanced query understanding for smarter searches</p>
              </div>
            </div>

            {/* Sample questions */}
            <div className="sample-section">
              <p className="sample-label">Try asking:</p>
              <div className="sample-questions">
                {SAMPLE_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    className="sample-btn"
                    id={`sample-question-${idx}`}
                    onClick={() => handleSend(q)}
                  >
                    <Sparkles size={14} />
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Chat Messages */
          <div className="chat-messages" id="chat-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.type}`}>
                {msg.type === 'bot' && (
                  <div className="message-avatar">
                    <Bot size={16} />
                  </div>
                )}
                <div className="message-bubble">
                  <div className="message-content">
                    {parseMarkdownLink(msg.text)}
                  </div>
                  {msg.footer && (
                    <div className="message-footer">
                      {msg.footer}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message bot">
                <div className="message-avatar">
                  <Bot size={16} />
                </div>
                <div className="message-bubble">
                  <div className="typing-indicator">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input Area - Always visible */}
      <footer className="input-footer" id="chat-input-area">
        <div className="input-container">
          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              className="chat-input"
              id="chat-input"
              placeholder="Ask about HDFC, ICICI, Motilal Oswal, or Aditya Birla funds..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={isLoading}
            />
            <button
              className="send-btn"
              id="send-button"
              onClick={() => handleSend()}
              disabled={isLoading || !input.trim()}
            >
              <Send size={18} />
            </button>
          </div>
          <p className="input-disclaimer">
            ⚠️ Facts-only assistant. This is not investment advice. Always verify with official sources.
          </p>
        </div>
      </footer>
    </div>
  );
}
