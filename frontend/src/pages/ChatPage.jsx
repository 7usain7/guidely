import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, FileText, Clock, Zap, AlertCircle } from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  "How do I book PTO or report a sick day?",
  "What are the rules for software and expense approvals?",
  "How do I troubleshoot VPN connection issues?"
];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am Guidely, your internal knowledge assistant. Ask me anything about company policies, technical guides, IT FAQs, or employee handbooks.',
      sources: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [topK, setTopK] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (questionText = input) => {
    const q = questionText.trim();
    setError(null);

    if (!q) {
      setError("Please enter a question or click one of the suggested prompts.");
      return;
    }

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Append user message
    const userMsg = { sender: 'user', text: q, timestamp: timeStr };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, top_k: Number(topK) })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to complete Q&A search');
      }

      // Append bot response
      const botMsg = {
        sender: 'bot',
        text: data.answer,
        sources: data.sources || [],
        latency_ms: data.latency_ms,
        cache_hit: data.cache_hit,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: `⚠️ Error: ${err.message}`,
        sources: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      {/* Messages Stream */}
      <div className="messages-list">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message-row ${msg.sender}`}>
            <div className={`avatar ${msg.sender}`}>
              {msg.sender === 'user' ? 'You' : 'G'}
            </div>

            <div className={`bubble ${msg.sender}`}>
              {msg.sender === 'user' ? (
                <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
              ) : (
                <div className="markdown-body">
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </div>
              )}

              {/* Source Citations for Bot Messages */}
              {msg.sender === 'bot' && msg.sources && msg.sources.length > 0 && (
                <div className="citation-box">
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Referenced Sources ({msg.sources.length}):
                  </div>
                  {msg.sources.map((src, sIdx) => (
                    <div key={sIdx} className="citation-card">
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, color: '#ffffff' }}>
                          <FileText size={14} color="#60a5fa" />
                          {src.filename}
                        </div>
                        <span className="tag">Relevance: {(src.relevance_score * 100).toFixed(0)}%</span>
                      </div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontStyle: 'italic' }}>
                        "{src.snippet}"
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Metadata Footer */}
              {msg.sender === 'bot' && msg.latency_ms !== undefined && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '8px', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                    <Clock size={12} /> {msg.latency_ms} ms
                  </span>
                  {msg.cache_hit && (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '3px', color: 'var(--success)' }}>
                      <Zap size={12} /> Cache Hit
                    </span>
                  )}
                  <span>• {msg.timestamp}</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Bubble */}
        {loading && (
          <div className="message-row bot">
            <div className="avatar bot">G</div>
            <div className="bubble bot" style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>Searching internal documents...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Question Pills */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
        {SUGGESTED_QUESTIONS.map((sq, idx) => (
          <button
            key={idx}
            onClick={() => { setInput(sq); handleSend(sq); }}
            style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              borderRadius: '14px',
              padding: '5px 12px',
              fontSize: '0.78rem',
              transition: 'all 0.15s'
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent-blue)'; e.currentTarget.style.color = '#ffffff'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-color)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Error Alert */}
      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '10px 14px', marginBottom: '12px', color: '#fca5a5', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Fixed Bottom Input Bar */}
      <div className="chat-input-bar">
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="input-wrapper">
          <input
            type="text"
            className="chat-input"
            placeholder="Type your question about company docs..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          <select
            value={topK}
            onChange={(e) => setTopK(e.target.value)}
            style={{
              background: 'var(--bg-main)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              borderRadius: '6px',
              padding: '4px 8px',
              fontSize: '0.8rem'
            }}
            title="Top-K context chunks"
          >
            <option value={3}>Top 3 Sources</option>
            <option value={5}>Top 5 Sources</option>
          </select>

          <button type="submit" disabled={loading || !input.trim()} className="send-btn">
            <Send size={15} />
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
