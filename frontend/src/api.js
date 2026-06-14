const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8001'

async function json(res) {
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const health    = ()            => fetch(`${BASE}/health`).then(json)
export const listMapping = ()          => fetch(`${BASE}/api/v1/mapping`).then(json)
export const audioUrl  = (label)       => `${BASE}/api/v1/audio/${encodeURIComponent(label)}`

export const updateMapping = (label, body) =>
  fetch(`${BASE}/api/v1/mapping/${encodeURIComponent(label)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(json)

export const uploadAudio = (label, file) => {
  const fd = new FormData()
  fd.append('file', file, file.name)
  return fetch(`${BASE}/api/v1/audio/${encodeURIComponent(label)}`, {
    method: 'POST', body: fd,
  }).then(json)
}

export const deleteAudio = (label) =>
  fetch(`${BASE}/api/v1/audio/${encodeURIComponent(label)}`, { method: 'DELETE' }).then(json)

export const detect = (blob, sessionId = 'default') => {
  const fd = new FormData()
  fd.append('file', blob, 'frame.jpg')
  return fetch(`${BASE}/api/v1/detect?session_id=${encodeURIComponent(sessionId)}`, {
    method: 'POST', body: fd,
  }).then(json)
}
