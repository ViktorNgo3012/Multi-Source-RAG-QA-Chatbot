import { useState, useRef } from 'react'
import { uploadPDFs } from '../api'

export default function PDFUploader({ sessionId, onSuccess, toast }) {
  const [files, setFiles]       = useState([])
  const [loading, setLoading]   = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const inputRef                = useRef()

  const addFiles = (incoming) => {
    const pdfs = Array.from(incoming).filter(f => f.type === 'application/pdf')
    if (!pdfs.length) { toast.error('Only PDF files are supported.'); return }
    setFiles(prev => {
      const names = new Set(prev.map(f => f.name))
      return [...prev, ...pdfs.filter(f => !names.has(f.name))]
    })
  }

  const removeFile = (name) => setFiles(prev => prev.filter(f => f.name !== name))

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    addFiles(e.dataTransfer.files)
  }

  const handleUpload = async () => {
    if (!files.length) { toast.error('Select at least one PDF first.'); return }
    setLoading(true)
    try {
      const result = await uploadPDFs(sessionId, files)
      const total  = result.reduce((s, r) => s + r.chunks_added, 0)
      toast.success(`${files.length} PDF(s) indexed — ${total} chunks added.`)
      setFiles([])
      onSuccess()
    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      toast.error(`Upload failed: ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* Drop zone */}
      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <div className="drop-zone-icon">📄</div>
        <div className="drop-zone-text">
          Drop PDFs here or <strong>click to browse</strong>
        </div>
        <div className="drop-zone-sub">Supports multiple files</div>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          multiple
          style={{ display: 'none' }}
          onChange={e => addFiles(e.target.files)}
        />
      </div>

      {/* Selected files */}
      {files.length > 0 && (
        <div className="file-chips">
          {files.map(f => (
            <div key={f.name} className="file-chip">
              <span>📎</span>
              <span className="file-chip-name">{f.name}</span>
              <button className="file-chip-remove" onClick={() => removeFile(f.name)}>✕</button>
            </div>
          ))}
        </div>
      )}

      <button
        className="btn btn-primary"
        onClick={handleUpload}
        disabled={loading || !files.length}
      >
        {loading ? '⏳ Indexing…' : `➕ Add ${files.length || ''} PDF${files.length !== 1 ? 's' : ''}`}
      </button>
    </div>
  )
}
