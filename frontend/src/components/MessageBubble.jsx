import { useState } from 'react'
import ReactMarkdown from 'react-markdown'

function SourcesAccordion({ sources }) {
  const [open, setOpen] = useState(false)
  if (!sources || !sources.length) return null

  return (
    <div className="sources-accordion">
      <button className="sources-toggle" onClick={() => setOpen(o => !o)}>
        <span>{open ? '▾' : '▸'}</span>
        <span>
          {open ? 'Hide' : 'Show'} {sources.length} source{sources.length !== 1 ? 's' : ''}
        </span>
      </button>
      {open && (
        <div className="sources-content">
          {sources.map((s, i) => (
            <div key={i} className="source-snippet-card">
              <div className="snippet-label">
                <span>📎</span>
                {s.label}
              </div>
              <div className="snippet-text">{s.snippet}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function TypingIndicator() {
  return (
    <div className="message-row bot">
      <div className="message-avatar bot-avatar">🤖</div>
      <div className="message-body">
        <div className="typing-indicator">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
      </div>
    </div>
  )
}

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`message-row ${isUser ? 'user' : 'bot'}`}>
      <div className={`message-avatar ${isUser ? 'user-avatar' : 'bot-avatar'}`}>
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-body">
        <div className={`message-bubble ${isUser ? 'user' : 'bot'}`}>
          {isUser
            ? message.content
            : <ReactMarkdown>{message.content}</ReactMarkdown>
          }
        </div>
        <span className="message-time">{formatTime(message.timestamp)}</span>
        {!isUser && <SourcesAccordion sources={message.sources} />}
      </div>
    </div>
  )
}
