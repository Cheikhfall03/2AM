import { useEffect, useRef, useState } from 'react'
import Header from '../components/Header'
import { audioUrl, deleteAudio, listMapping, updateMapping, uploadAudio } from '../api'
import './Library.css'

const OBJECT_ICONS = {
  person:         '🚶',
  car:            '🚗',
  bicycle:        '🚲',
  dog:            '🐕',
  bench:          '🪑',
  bottle:         '🍶',
  chair:          '🪑',
  'stop sign':    '🛑',
  'traffic light':'🚦',
  backpack:       '🎒',
  cat:            '🐈',
  motorcycle:     '🏍',
  bus:            '🚌',
  truck:          '🚛',
}

function AudioRow({ entry, onUpdate }) {
  const [expanded, setExpanded] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [editing, setEditing] = useState(false)
  const [phrase, setPhrase] = useState(entry.phrase_wolof)
  const [savingPhrase, setSavingPhrase] = useState(false)
  const audioRef = useRef(null)
  const fileRef  = useRef(null)

  const icon = OBJECT_ICONS[entry.label] ?? '📦'

  async function toggleEnabled() {
    const updated = await updateMapping(entry.label, { enabled: !entry.enabled })
    onUpdate(updated)
  }

  async function handleUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const updated = await uploadAudio(entry.label, file)
      onUpdate(updated)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  async function handleDelete() {
    const updated = await deleteAudio(entry.label)
    onUpdate(updated)
  }

  async function savePhrase() {
    setSavingPhrase(true)
    try {
      const updated = await updateMapping(entry.label, { phrase_wolof: phrase })
      onUpdate(updated)
      setEditing(false)
    } finally {
      setSavingPhrase(false)
    }
  }

  function togglePlay() {
    if (!entry.has_audio) return
    if (playing && audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setPlaying(false)
      return
    }
    const a = new Audio(audioUrl(entry.label))
    audioRef.current = a
    a.onended = () => setPlaying(false)
    a.play().then(() => setPlaying(true)).catch(() => setPlaying(false))
  }

  return (
    <div className={`audio-row${expanded ? ' expanded' : ''}`}>
      {/* Main row */}
      <div
        className="audio-row-main"
        onClick={() => setExpanded(e => !e)}
        role="button"
        tabIndex={0}
        aria-expanded={expanded}
        onKeyDown={e => e.key === 'Enter' && setExpanded(v => !v)}
      >
        <div className="audio-icon-wrap">{icon}</div>

        <div className="audio-info">
          <div className="audio-labels">
            <span className="audio-label-fr">{entry.label_fr}</span>
            {entry.phrase_wolof && (
              <span className="audio-phrase">{entry.phrase_wolof}</span>
            )}
          </div>
        </div>

        <div className="audio-right">
          {entry.has_audio && (
            <span className="badge badge-green">Audio</span>
          )}
          {!entry.enabled && (
            <span className="badge badge-muted">Off</span>
          )}
          <span className="audio-chevron" aria-hidden>
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06z" clipRule="evenodd" />
            </svg>
          </span>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="audio-drawer">
          <hr className="divider" />

          {/* Phrase wolof */}
          <div className="drawer-section">
            <span className="drawer-label">Phrase wolof</span>
            {editing ? (
              <div className="phrase-edit">
                <input
                  className="phrase-input"
                  value={phrase}
                  onChange={e => setPhrase(e.target.value)}
                  autoFocus
                  placeholder="Ex : Nit ci kanam"
                />
                <button
                  className="btn-sm btn-amber"
                  onClick={savePhrase}
                  disabled={savingPhrase}
                >
                  {savingPhrase ? '…' : 'Sauvegarder'}
                </button>
                <button className="btn-sm btn-ghost-sm" onClick={() => { setEditing(false); setPhrase(entry.phrase_wolof) }}>
                  Annuler
                </button>
              </div>
            ) : (
              <div className="phrase-display">
                <span className="phrase-value">{entry.phrase_wolof || '—'}</span>
                <button className="icon-btn" onClick={() => setEditing(true)} aria-label="Modifier la phrase">
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path d="m5.433 13.917 1.262-3.155A4 4 0 0 1 7.58 9.42l6.92-6.918a2.121 2.121 0 0 1 3 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 0 1-.65-.65Z" />
                  </svg>
                </button>
              </div>
            )}
          </div>

          {/* Audio file */}
          <div className="drawer-section">
            <span className="drawer-label">Enregistrement</span>
            <div className="audio-actions">
              {entry.has_audio && (
                <button
                  className={`btn-sm btn-play${playing ? ' playing' : ''}`}
                  onClick={togglePlay}
                  aria-label={playing ? 'Arrêter' : 'Écouter'}
                >
                  {playing ? (
                    <svg viewBox="0 0 20 20" fill="currentColor">
                      <path d="M5.75 3a.75.75 0 0 0-.75.75v12.5c0 .414.336.75.75.75h1.5a.75.75 0 0 0 .75-.75V3.75A.75.75 0 0 0 7.25 3h-1.5ZM12.75 3a.75.75 0 0 0-.75.75v12.5c0 .414.336.75.75.75h1.5a.75.75 0 0 0 .75-.75V3.75a.75.75 0 0 0-.75-.75h-1.5Z" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 20 20" fill="currentColor">
                      <path d="M6.3 2.84A1.5 1.5 0 0 0 4 4.11v11.78a1.5 1.5 0 0 0 2.3 1.27l9.344-5.891a1.5 1.5 0 0 0 0-2.538L6.3 2.84Z" />
                    </svg>
                  )}
                  {playing ? 'Arrêter' : 'Écouter'}
                </button>
              )}

              <label className={`btn-sm btn-upload${uploading ? ' uploading' : ''}`} aria-label="Téléverser un fichier audio">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M13.75 7h-3V3.66l1.95 2.1a.75.75 0 1 0 1.1-1.02l-3.25-3.5a.75.75 0 0 0-1.1 0L6.2 4.74a.75.75 0 0 0 1.1 1.02l1.95-2.1V7h-3A2.25 2.25 0 0 0 4 9.25v7.5A2.25 2.25 0 0 0 6.25 19h7.5A2.25 2.25 0 0 0 16 16.75v-7.5A2.25 2.25 0 0 0 13.75 7Zm-3 0h-1.5v5.25a.75.75 0 0 0 1.5 0V7Z" clipRule="evenodd" />
                </svg>
                {uploading ? 'Upload…' : 'Importer'}
                <input
                  ref={fileRef}
                  type="file"
                  accept=".wav,.mp3,.ogg,.m4a"
                  className="sr-only"
                  onChange={handleUpload}
                />
              </label>

              {entry.has_audio && (
                <button
                  className="btn-sm btn-danger-ghost"
                  onClick={handleDelete}
                  aria-label="Supprimer l'enregistrement"
                >
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 1 0 .23 1.482l.149-.022.841 10.518A2.75 2.75 0 0 0 7.596 19h4.807a2.75 2.75 0 0 0 2.742-2.53l.841-10.52.149.023a.75.75 0 0 0 .23-1.482A41.03 41.03 0 0 0 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4ZM8.58 7.72a.75.75 0 0 0-1.5.06l.3 7.5a.75.75 0 1 0 1.5-.06l-.3-7.5Zm4.34.06a.75.75 0 1 0-1.5-.06l-.3 7.5a.75.75 0 1 0 1.5.06l.3-7.5Z" clipRule="evenodd" />
                  </svg>
                  Supprimer
                </button>
              )}
            </div>
          </div>

          {/* Enable toggle */}
          <div className="drawer-section drawer-section-row">
            <span className="drawer-label">Annonces actives</span>
            <button
              className={`toggle${entry.enabled ? ' on' : ''}`}
              onClick={toggleEnabled}
              role="switch"
              aria-checked={entry.enabled}
              aria-label={`${entry.label_fr} — ${entry.enabled ? 'activé' : 'désactivé'}`}
            >
              <span className="toggle-thumb" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function Library() {
  const [entries,  setEntries]  = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState(null)
  const [filter,   setFilter]   = useState('all')

  useEffect(() => {
    listMapping()
      .then(data => setEntries(data))
      .catch(() => setError('Impossible de charger la bibliothèque.'))
      .finally(() => setLoading(false))
  }, [])

  function handleUpdate(updated) {
    setEntries(prev => prev.map(e => e.label === updated.label ? updated : e))
  }

  const filtered = filter === 'all'
    ? entries
    : filter === 'ready'
    ? entries.filter(e => e.has_audio && e.enabled)
    : entries.filter(e => !e.has_audio)

  const countReady   = entries.filter(e => e.has_audio).length
  const countMissing = entries.filter(e => !e.has_audio).length

  return (
    <div className="library-page">
      <Header title="Bibliothèque" />

      {/* Stats bar */}
      <div className="stats-bar">
        <div className="stat">
          <span className="stat-val">{entries.length}</span>
          <span className="stat-key">Objets</span>
        </div>
        <div className="stat-divider" />
        <div className="stat">
          <span className="stat-val stat-green">{countReady}</span>
          <span className="stat-key">Avec audio</span>
        </div>
        <div className="stat-divider" />
        <div className="stat">
          <span className="stat-val stat-amber">{countMissing}</span>
          <span className="stat-key">Sans audio</span>
        </div>
      </div>

      {/* Filter chips */}
      <div className="filter-row">
        {[
          { id: 'all',     label: 'Tous' },
          { id: 'ready',   label: 'Prêts' },
          { id: 'missing', label: 'Manquants' },
        ].map(f => (
          <button
            key={f.id}
            className={`chip${filter === f.id ? ' active' : ''}`}
            onClick={() => setFilter(f.id)}
          >
            {f.label}
          </button>
        ))}
      </div>

      <hr className="divider" />

      {/* List */}
      {loading && (
        <div className="lib-state">
          <span className="spinner-dark" aria-label="Chargement…" />
        </div>
      )}

      {error && (
        <div className="lib-error" role="alert">{error}</div>
      )}

      {!loading && !error && (
        <div className="audio-list">
          {filtered.length === 0 ? (
            <div className="lib-state lib-empty">Aucun élément</div>
          ) : (
            filtered.map(e => (
              <AudioRow key={e.label} entry={e} onUpdate={handleUpdate} />
            ))
          )}
        </div>
      )}
    </div>
  )
}
