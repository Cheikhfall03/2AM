import { useEffect, useState } from 'react'
import { health } from '../api'
import './Header.css'

export default function Header({ title }) {
  const [online, setOnline] = useState(null)

  useEffect(() => {
    let alive = true
    const check = async () => {
      try {
        await health()
        if (alive) setOnline(true)
      } catch {
        if (alive) setOnline(false)
      }
    }
    check()
    const id = setInterval(check, 8000)
    return () => { alive = false; clearInterval(id) }
  }, [])

  return (
    <header className="header">
      <div className="header-brand">
        <span className="header-logo">2AM</span>
        {title && <span className="header-sep">/</span>}
        {title && <span className="header-title">{title}</span>}
      </div>
      <div className="header-status">
        {online === null
          ? <span className="status-dot connecting" title="Connexion…" />
          : online
          ? <span className="status-dot online" title="Backend connecté" />
          : <span className="status-dot offline" title="Backend hors ligne" />
        }
      </div>
    </header>
  )
}
