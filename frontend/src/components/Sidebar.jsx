import { useState } from 'react'
import PDFUploader  from './PDFUploader'
import WebsiteAdder from './WebsiteAdder'
import SourcesList  from './SourcesList'
import Settings     from './Settings'
import { exportChat } from '../api'

export default function Sidebar({
  sessionId,
  docCount,
  sources,
  settings,
  onSettingsChange,
  onSourceAdded,
  onReset,
  toast,
}) {
  const [sourceTab,   setSourceTab]   = useState('pdf')   // 'pdf' | 'web'
  const [settingsOpen, setSettingsOpen] = useState(false)

  const handleExport = async () => {
    if (!sessionId) return
    try {
      const data = await exportChat(sessionId)
      const blob = new Blob([data.content], { type: 'text/plain' })
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `chat_${new Date().toISOString().slice(0, 16).replace('T', '_')}.txt`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Chat exported!')
    } catch {
      toast.error('Export failed.')
    }
  }

  return (
    <aside className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div className="brand">
          <div className="brand-icon">🤖</div>
          <div>
            <div className="brand-name">RAG ChatBot</div>
          </div>
        </div>
        {sessionId && (
          <div className="session-badge">
            <span className="session-dot" />
            <span>Session active</span>
          </div>
        )}
      </div>

      <div className="sidebar-scroll">

        {/* Stats */}
        {docCount > 0 && (
          <div className="stats-bar">
            <div className="stat-pill">
              <div className="stat-value">{docCount}</div>
              <div className="stat-label">Chunks</div>
            </div>
            <div className="stat-pill">
              <div className="stat-value">{sources.length}</div>
              <div className="stat-label">Sources</div>
            </div>
          </div>
        )}

        {/* Sources input */}
        <div>
          <div className="section-label">📚 Add Knowledge</div>
          <div className="tab-bar">
            <button
              className={`tab-btn ${sourceTab === 'pdf' ? 'active' : ''}`}
              onClick={() => setSourceTab('pdf')}
            >
              📄 PDF
            </button>
            <button
              className={`tab-btn ${sourceTab === 'web' ? 'active' : ''}`}
              onClick={() => setSourceTab('web')}
            >
              🌐 Website
            </button>
          </div>

          {sourceTab === 'pdf'
            ? <PDFUploader
                sessionId={sessionId}
                onSuccess={onSourceAdded}
                toast={toast}
              />
            : <WebsiteAdder
                sessionId={sessionId}
                onSuccess={onSourceAdded}
                toast={toast}
              />
          }
        </div>

        <div className="divider" />

        {/* Indexed sources */}
        <div>
          <div className="section-label">✅ Indexed Sources</div>
          <SourcesList sources={sources} />
        </div>

        <div className="divider" />

        {/* Settings */}
        <div>
          <button
            style={{
              width: '100%',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 0,
              textAlign: 'left',
            }}
            onClick={() => setSettingsOpen(o => !o)}
          >
            <div className="section-label" style={{ cursor: 'pointer', userSelect: 'none' }}>
              ⚙️ Settings
              <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--color-text-muted)' }}>
                {settingsOpen ? '▾' : '▸'}
              </span>
            </div>
          </button>
          {settingsOpen && (
            <Settings settings={settings} onChange={onSettingsChange} />
          )}
        </div>

      </div>

      {/* Footer actions */}
      <div className="sidebar-footer">
        <button className="btn btn-danger-ghost" onClick={onReset} title="Reset all">
          🗑️ Reset
        </button>
        <button className="btn btn-ghost" onClick={handleExport} title="Export chat">
          ⬇️ Export
        </button>
      </div>
    </aside>
  )
}
