import { useCallback, useEffect, useRef, useState } from 'react'
import Header from '../components/Header'
import { describe } from '../api'
import './Live.css'

const SESSION_ID = `session-${Date.now()}`

let _currentSource = null
let _audioPlaying  = false

async function playBlob(ctx, blob) {
  if (!ctx || ctx.state === 'closed') return
  if (_audioPlaying) return           // ne pas superposer les sons
  try {
    const buf     = await blob.arrayBuffer()
    const decoded = await ctx.decodeAudioData(buf)
    if (_currentSource) { try { _currentSource.stop() } catch {} }
    const src  = ctx.createBufferSource()
    src.buffer = decoded
    src.connect(ctx.destination)
    _audioPlaying  = true
    src.onended    = () => { _audioPlaying = false }
    src.start(0)
    _currentSource = src
  } catch { _audioPlaying = false }
}

function AnnouncementBanner({ scene, onDismiss }) {
  if (!scene) return null
  const urgent = scene.phraseFr.startsWith('Attention')
  return (
    <div className={`announcement announcement-${urgent ? 'urgent' : 'info'}`} role="alert" aria-live="assertive">
      <div className="announcement-main">
        <span className="announcement-phrase">{scene.phraseWo}</span>
        <span className="announcement-label">{scene.phraseFr}</span>
      </div>
      <button className="announcement-close" onClick={onDismiss} aria-label="Fermer">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
        </svg>
      </button>
    </div>
  )
}

const SILENCE = 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA='

export default function Live() {
  const videoRef    = useRef(null)
  const canvasRef   = useRef(null)
  const streamRef   = useRef(null)
  const intervalRef = useRef(null)
  const audioCtxRef = useRef(null)

  const [cameraOn,    setCameraOn]   = useState(false)
  const [auto,        setAuto]       = useState(false)
  const [detecting,   setDetecting]  = useState(false)
  const [scene,       setScene]      = useState(null)
  const [detections,  setDetections] = useState([])
  const [error,       setError]      = useState(null)

  /* ── Déverrouillage audio mobile (geste utilisateur requis) ── */
  const unlockAudio = useCallback(() => {
    if (audioCtxRef.current) return
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    audioCtxRef.current = ctx
    // Joue un silence pour débloquer l'autoplay sur iOS/Android
    const sil = new Audio(SILENCE)
    sil.play().catch(() => {})
    if (ctx.state === 'suspended') ctx.resume()
  }, [])

  /* ── Camera ── */
  const startCamera = useCallback(async () => {
    unlockAudio()
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

  /* ── Dessin des cadres YOLO sur le canvas overlay ── */
  const overlayRef = useRef(null)
  const drawBoxes = useCallback((dets) => {
    const video   = videoRef.current
    const overlay = overlayRef.current
    if (!overlay || !video) return
    overlay.width  = video.videoWidth  || video.clientWidth
    overlay.height = video.videoHeight || video.clientHeight
    const ctx = overlay.getContext('2d')
    ctx.clearRect(0, 0, overlay.width, overlay.height)
    dets.forEach(d => {
      if (!d.bbox) return
      const [x1, y1, x2, y2] = d.bbox
      const urgent = d.distance_m !== null && d.distance_m <= 1.5
      ctx.strokeStyle = urgent ? '#ef4444' : '#22c55e'
      ctx.lineWidth   = 2
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
      ctx.fillStyle = urgent ? '#ef4444cc' : '#22c55ecc'
      ctx.font = 'bold 13px sans-serif'
      const label = d.distance_m !== null
        ? `${d.label_fr} ${d.distance_m.toFixed(1)}m`
        : d.label_fr
      ctx.fillRect(x1, y1 - 18, ctx.measureText(label).width + 8, 18)
      ctx.fillStyle = '#fff'
      ctx.fillText(label, x1 + 4, y1 - 4)
    })
  }, [])

  const runDetect = useCallback(async () => {
    if (detecting) return
    setDetecting(true)
    try {
      const blob = await captureFrame()
      if (!blob) return
      const result = await describe(blob, SESSION_ID)
      if (result) {
        setScene(result)
        setDetections(result.detections ?? [])
        drawBoxes(result.detections ?? [])
        playBlob(audioCtxRef.current, result.audioBlob)
      }
    } catch {
      setError('Erreur de détection. Le backend est-il démarré ?')
    } finally {
      setDetecting(false)
    }
  }, [detecting, captureFrame])

  /* ── Keep-alive : ping toutes les 9 min pour garder Render éveillé ── */
  useEffect(() => {
    const id = setInterval(() => fetch('https://twoam.onrender.com/health').catch(() => {}), 9 * 60 * 1000)
    return () => clearInterval(id)
  }, [])

  /* ── Boucle live : enchaîne les détections, réessaie en cas d'erreur ── */
  useEffect(() => {
    if (!auto || !cameraOn) return
    let active = true

    async function loop() {
      while (active) {
        const blob = await captureFrame()
        if (!blob || !active) break
        try {
          const result = await describe(blob, SESSION_ID)
          if (!active) break
          if (result) {
            setScene(result)
            setDetections(result.detections ?? [])
            drawBoxes(result.detections ?? [])
            playBlob(audioCtxRef.current, result.audioBlob)
          }
          setError(null)
        } catch {
          if (!active) break
          setError('Connexion au backend en cours...')
          await new Promise(r => setTimeout(r, 3000))
        }
      }
      setDetecting(false)
    }

    setDetecting(true)
    loop()
    return () => { active = false }
  }, [auto, cameraOn, captureFrame])

  return (
    <div className="live-page">
      <Header title="Détection" />

      <AnnouncementBanner scene={scene} onDismiss={() => setScene(null)} />

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
        <canvas ref={overlayRef} className="viewport-overlay" aria-hidden />

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

      {!scene && cameraOn && !detecting && (
        <div className="live-empty">
          <span>En attente d'objets…</span>
        </div>
      )}
    </div>
  )
}
