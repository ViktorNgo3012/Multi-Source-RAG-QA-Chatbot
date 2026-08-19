const MODELS = [
  'llama-3.3-70b-versatile',
  'llama-3.1-8b-instant',
  'gemma2-9b-it',
]

export default function Settings({ settings, onChange }) {
  const update = (key, val) => onChange({ ...settings, [key]: val })

  return (
    <div className="settings-grid">
      {/* Model */}
      <div className="setting-row">
        <div className="setting-label-row">
          <span className="setting-label">🧠 Groq Model</span>
        </div>
        <select
          className="model-select"
          value={settings.model}
          onChange={e => update('model', e.target.value)}
        >
          {MODELS.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

      {/* Temperature */}
      <div className="setting-row">
        <div className="setting-label-row">
          <span className="setting-label">🌡️ Temperature</span>
          <span className="setting-value">{settings.temperature.toFixed(1)}</span>
        </div>
        <input
          type="range"
          className="range-slider"
          min={0} max={1} step={0.1}
          value={settings.temperature}
          onChange={e => update('temperature', parseFloat(e.target.value))}
        />
      </div>

      {/* K Chunks */}
      <div className="setting-row">
        <div className="setting-label-row">
          <span className="setting-label">🔍 Chunks retrieved (k)</span>
          <span className="setting-value">{settings.kChunks}</span>
        </div>
        <input
          type="range"
          className="range-slider"
          min={1} max={8} step={1}
          value={settings.kChunks}
          onChange={e => update('kChunks', parseInt(e.target.value))}
        />
      </div>

      {/* Show sources toggle */}
      <div className="setting-row" style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="setting-label">📎 Show source snippets</span>
        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={settings.showSources}
            onChange={e => update('showSources', e.target.checked)}
            style={{ display: 'none' }}
          />
          <span style={{
            width: 40,
            height: 22,
            borderRadius: 99,
            background: settings.showSources
              ? 'linear-gradient(135deg,#6366f1,#22d3ee)'
              : 'var(--color-surface-2)',
            border: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            padding: 3,
            transition: '0.2s',
            cursor: 'pointer',
          }}>
            <span style={{
              width: 14, height: 14, borderRadius: '50%', background: '#fff',
              transform: settings.showSources ? 'translateX(18px)' : 'translateX(0)',
              transition: '0.2s',
              boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
            }} />
          </span>
        </label>
      </div>
    </div>
  )
}
