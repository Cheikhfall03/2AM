import { useState } from 'react'
import './index.css'
import Nav from './components/Nav'
import Live from './pages/Live'
import Library from './pages/Library'

export default function App() {
  const [page, setPage] = useState('live')

  return (
    <div className="app">
      <main className="page-content">
        {page === 'live'    && <Live />}
        {page === 'library' && <Library />}
      </main>
      <Nav page={page} onNavigate={setPage} />
    </div>
  )
}
