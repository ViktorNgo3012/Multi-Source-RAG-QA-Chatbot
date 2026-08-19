import { useState } from 'react'
import { addWebsite } from '../api'

export default function WebsiteAdder({ sessionId, onSuccess, toast }) {
  const [url, setUrl]       = useState('')
  const [loading, setLoading] = useState(false)

  const handleAdd = async () => {
    const trimmed = url.trim()
    if (!trimmed) { toast.error('Please enter a URL.'); return }
    if (!/^https?:\/\/.+/.test(trimmed)) {
      toast.error('URL must start with http:// or https://')
      return
    }
    setLoading(true)
    try {
      const result = await addWebsite(sessionId, trimmed)
      toast.success(`Website indexed — ${result.chunks_added} chunks added.`)
      setUrl('')
      onSuccess()
    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      toast.error(`Failed: ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAdd() }
  }

  return (
    <div>
      <div className="input-group">
        <label className="form-label">Website URL</label>
        <input
          type="url"
          className="text-input"
          placeholder="https://example.com/article"
          value={url}
          onChange={e => setUrl(e.target.value)}
          onKeyDown={handleKey}
          disabled={loading}
        />
      </div>
      <button
        className="btn btn-primary"
        onClick={handleAdd}
        disabled={loading || !url.trim()}
      >
        {loading ? '⏳ Scraping…' : '🌐 Add Website'}
      </button>
    </div>
  )
}
