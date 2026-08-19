import { useRef, useState, useEffect } from 'react'

export default function ChatInput({ onSend, disabled, hasSource }) {
  const [text, setText] = useState('')
  const textareaRef     = useRef()

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'
  }, [text])

  const handleSend = () => {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="input-bar">
      <div className="input-bar-inner">
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          placeholder={
            !hasSource
              ? 'Add a PDF or website first…'
              : 'Ask a question about your sources…'
          }
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKey}
          disabled={disabled || !hasSource}
          rows={1}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={disabled || !text.trim() || !hasSource}
          title="Send (Enter)"
        >
          {disabled
            ? <Spinner />
            : <SendIcon />
          }
        </button>
      </div>
      <p className="input-hint">
        Press <kbd style={{ background: 'var(--color-surface-2)', padding: '1px 5px', borderRadius: 4, fontSize: 10, border: '1px solid var(--color-border)' }}>Enter</kbd> to send &nbsp;·&nbsp;
        <kbd style={{ background: 'var(--color-surface-2)', padding: '1px 5px', borderRadius: 4, fontSize: 10, border: '1px solid var(--color-border)' }}>Shift + Enter</kbd> for new line
      </p>
    </div>
  )
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  )
}

function Spinner() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83">
        <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite" />
      </path>
    </svg>
  )
}
