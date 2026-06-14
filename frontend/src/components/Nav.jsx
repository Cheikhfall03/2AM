import './Nav.css'

const tabs = [
  {
    id: 'live',
    label: 'Détection',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <circle cx="12" cy="12" r="3" />
        <path d="M6.343 6.343A8 8 0 1 0 17.657 17.657" strokeLinecap="round" />
        <path d="M3 3l18 18" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: 'library',
    label: 'Bibliothèque',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <rect x="3" y="5" width="4" height="14" rx="1" />
        <rect x="9" y="3" width="4" height="18" rx="1" />
        <rect x="15" y="7" width="4" height="12" rx="1" />
      </svg>
    ),
  },
]

export default function Nav({ page, onNavigate }) {
  return (
    <nav className="nav" aria-label="Navigation principale">
      {tabs.map((t) => (
        <button
          key={t.id}
          className={`nav-tab${page === t.id ? ' active' : ''}`}
          onClick={() => onNavigate(t.id)}
          aria-current={page === t.id ? 'page' : undefined}
        >
          <span className="nav-icon">{t.icon}</span>
          <span className="nav-label">{t.label}</span>
        </button>
      ))}
    </nav>
  )
}
