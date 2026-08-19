export default function SourcesList({ sources }) {
  if (!sources.length) {
    return (
      <div className="sources-empty">
        <div style={{ fontSize: 28, marginBottom: 8 }}>📭</div>
        No sources added yet.<br />
        <span style={{ fontSize: 12 }}>Upload a PDF or add a website above.</span>
      </div>
    )
  }

  return (
    <div className="sources-list">
      {sources.map((s, i) => (
        <div key={`${s.type}-${s.name}-${i}`} className="source-item">
          <div className={`source-icon ${s.type}`}>
            {s.type === 'pdf' ? '📄' : '🌐'}
          </div>
          <div className="source-info">
            <div className="source-name" title={s.name}>
              {s.type === 'pdf' ? s.name : shortenUrl(s.name)}
            </div>
            <div className="source-type">{s.type}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

function shortenUrl(url) {
  try {
    const u = new URL(url)
    return u.hostname + (u.pathname !== '/' ? u.pathname : '')
  } catch {
    return url
  }
}
