import { useCallback, useEffect, useRef, useState } from 'react'
import Header from '../components/Header'
import { audioUrl, detect } from '../api'

function resolveAudio(announcement) {
  if (!announcement) return null
  return announcement.audio_url ? audioUrl(announcement.label) : null
}
import './Live.css'

const SESSION_ID = `session-${Date.now()}`
const POSITION_LABELS = { left: 'Gauche', center: 'Centre', right: 'Droite' }

function AnnouncementBanner({ announcement, onDismiss }) {
  const audioRef = useRef(null)

  useEffect(() => {
    const url = resolveAudio(announcement)
    if (!url) return
    const a = new Audio(url)
    a.play().catch(() => {})
    return () => { a.pause(); a.src = '' }
  }, [announcement])

  if (!announcement) return null

  const dist = announcement.distance_m
  const urgency = dist !== null && dist <= 2 ? 'urgent' : dist !== null && dist <= 4 ? 'warn' : 'info'

  return (
    <div className={`announcement announcement-${urgency}`} role="alert" aria-live="assertive">
      <div className="announcement-main">
        <span className="announcement-phrase">{announcement.phrase_wolof}</span>
        <span className="announcement-label">{announcement.label_fr}</span>
      </div>
      <div className="announcement-meta">
        {dist !== null && (
          <span className="announcement-dist">
            {dist.toFixed(1)} m
          </span>
        )}
        <span className="announcement-pos">
          {POSITION_LABELS[announcement.position] ?? announcement.position}
        </span>
        {announcement.audio_url && (
          <button
            className="announcement-replay"
            onClick={() => new Audio(resolveAudio(announcement)).play().catch(() => {})}
            aria-label="Rejouer l'annonce"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path d="M6.3 2.84A1.5 1.5 0 0 0 4 4.11v11.78a1.5 1.5 0 0 0 2.3 1.27l9.344-5.891a1.5 1.5 0 0 0 0-2.538L6.3 2.84Z" />
            </svg>
          </button>
        )}
      </div>
      <button className="announcement-close" onClick={onDismiss} aria-label="Fermer">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
        </svg>
      </button>
    </div>
  )
}

function DetectionRow({ det }) {
  const dist = det.distance_m
  const urgency = dist !== null && dist <= 2 ? 'urgent' : dist !== null && dist <= 4 ? 'warn' : 'ok'
  return (
    <div className={`det-row det-row-${urgency}`}>
      <div className="det-info">
        <span className="det-label">{det.label_fr}</span>
        <span className="det-pos">{POSITION_LABELS[det.position] ?? det.position}</span>
      </div>
      <div className="det-right">
        {dist !== null && <span className="det-dist">{dist.toFixed(1)} m</span>}
        <span className="det-conf">{(det.confidence * 100).toFixed(0)}%</span>
      </div>
    </div>
  )
}

export default function Live() {
  const videoRef    = useRef(null)
  const canvasRef   = useRef(null)
  const streamRef   = useRef(null)
  const intervalRef = useRef(null)

  const [cameraOn,      setCameraOn]      = useState(false)
  const [auto,          setAuto]          = useState(false)
  const [detecting,     setDetecting]     = useState(false)
  const [announcement,  setAnnouncement]  = useState(null)
  const [detections,    setDetections]    = useState([])
  const [scene,         setScene]         = useState(null)
  const [error,         setError]         = useState(null)

  /* ── Camera ── */
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
      setCameraOn(true)
      setAuto(true)
      setError(null)
    } catch (e) {
      setError('Impossible d\'accéder à la caméra. Vérifiez les permissions.')
    }
  }, [])

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null
    setCameraOn(false)
    setAuto(false)
    setDetections([])
    setAnnouncement(null)
    setScene(null)
  }, [])

  useEffect(() => () => { stopCamera() }, [stopCamera])

  /* ── Capture ── */
  const captureFrame = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return
    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width  = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)

    return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', .85))
  }, [])

  const runDetect = useCallback(async () => {
    if (detecting) return
    setDetecting(true)
    try {
      const blob = await captureFrame()
      if (!blob) return
      const result = await detect(blob, SESSION_ID)
      setDetections(result.detections ?? [])
      setScene(result.scene ?? null)
      if (result.announcement) setAnnouncement(result.announcement)
    } catch {
      setError('Erreur de détection. Le backend est-il démarré ?')
    } finally {
      setDetecting(false)
    }
  }, [detecting, captureFrame])

  /* ── Auto mode ── */
  useEffect(() => {
    if (auto && cameraOn) {
      intervalRef.current = setInterval(runDetect, 1500)
    } else {
      clearInterval(intervalRef.current)
    }
    return () => clearInterval(intervalRef.current)
  }, [auto, cameraOn, runDetect])

  return (
    <div className="live-page">
      <Header title="Détection" />

      <AnnouncementBanner
        announcement={announcement}
        onDismiss={() => setAnnouncement(null)}
      />

      {/* Camera viewport */}
      <div className="viewport">
        <video
          ref={videoRef}
          className="viewport-video"
          playsInline
          muted
          aria-label="Flux caméra"
        />
        <canvas ref={canvasRef} className="sr-only" aria-hidden />

        {!cameraOn && (
          <div className="viewport-placeholder">
            <svg className="viewport-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4">
              <path d="M23 7l-7 5 7 5V7z" />
              <rect x="1" y="5" width="15" height="14" rx="2" />
            </svg>
            <p>Caméra inactive</p>
          </div>
        )}

        {cameraOn && detecting && (
          <div className="viewport-scanning" aria-live="polite" aria-label="Analyse en cours">
            <span className="scan-bar" />
          </div>
        )}

        {cameraOn && auto && (
          <span className="live-pill" aria-label="Mode automatique actif">AUTO</span>
        )}
      </div>

      {/* Controls */}
      <div className="live-controls">
        {!cameraOn ? (
          <button className="btn-primary btn-full" onClick={startCamera}>
            Démarrer la caméra
          </button>
        ) : (
          <>
            <button
              className="btn-ghost"
              onClick={stopCamera}
              aria-label="Arrêter la caméra"
            >
              Arrêter
            </button>

            <button
              className="btn-primary btn-capture"
              onClick={runDetect}
              disabled={detecting}
              aria-label="Capturer et analyser"
            >
              {detecting ? (
                <span className="spinner" aria-hidden />
              ) : (
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <circle cx="10" cy="10" r="4" />
                  <path fillRule="evenodd" d="M1 8a7 7 0 1 1 14 0A7 7 0 0 1 1 8zm7-5a5 5 0 1 0 0 10A5 5 0 0 0 8 3z" clipRule="evenodd" />
                </svg>
              )}
              Analyser
            </button>

            <button
              className={`btn-toggle${auto ? ' active' : ''}`}
              onClick={() => setAuto(a => !a)}
              aria-pressed={auto}
              aria-label={auto ? 'Désactiver le mode auto' : 'Activer le mode auto'}
            >
              Auto
            </button>
          </>
        )}
      </div>

      {error && (
        <div className="live-error" role="alert">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-.75-9.75a.75.75 0 0 1 1.5 0v3.5a.75.75 0 0 1-1.5 0v-3.5zm.75 6.5a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5z" clipRule="evenodd" />
          </svg>
          {error}
        </div>
      )}

      {/* Detections list */}
      {detections.length > 0 && (
        <section className="detections-section">
          <div className="section-header">
            <span className="section-title">Objets détectés</span>
            <span className="badge badge-amber">{detections.length}</span>
          </div>
          <div className="det-list">
            {detections.map((d, i) => <DetectionRow key={i} det={d} />)}
          </div>
        </section>
      )}

      {scene && scene.object_count === 0 && (
        <div className="live-empty">
          <span>Aucun objet détecté</span>
        </div>
      )}
    </div>
  )
}
