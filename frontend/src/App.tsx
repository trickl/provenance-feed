import { useEffect, useMemo, useState } from 'react'
import { LightDarkToggle } from 'react-light-dark-toggle'

import { fetchFeed } from './api'
import type { FeedItem } from './types'
import { FeedItemCard } from './components/FeedItemCard'
import type { Theme } from './theme'
import { applyTheme, getSystemTheme, loadStoredTheme, storeTheme } from './theme'

export function App() {
  const [items, setItems] = useState<FeedItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [theme, setTheme] = useState<Theme>(() => loadStoredTheme() ?? getSystemTheme())
  const [hasUserTheme, setHasUserTheme] = useState<boolean>(() => loadStoredTheme() !== null)

  const isLight = useMemo(() => theme === 'light', [theme])

  useEffect(() => {
    applyTheme(theme)
  }, [theme])

  // If the user hasn't chosen a theme yet, follow OS changes.
  useEffect(() => {
    if (hasUserTheme) return
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return

    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => setTheme(e.matches ? 'dark' : 'light')

    if (typeof mql.addEventListener === 'function') {
      mql.addEventListener('change', handler)
      return () => mql.removeEventListener('change', handler)
    }

    // Safari < 14
    mql.addListener(handler)
    return () => mql.removeListener(handler)
  }, [hasUserTheme])

  useEffect(() => {
    let cancelled = false
    fetchFeed(50)
      .then((data) => {
        if (cancelled) return
        setItems(data)
      })
      .catch((e: unknown) => {
        if (cancelled) return
        setError(e instanceof Error ? e.message : String(e))
      })

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="page">
      <header className="header">
        <div className="headerRow">
          <div className="headerText">
            <h1>provenance-feed</h1>
            <p>Chronological feed with a best-effort source trust badge from provenance-graph.</p>
          </div>

          <div className="headerControls">
            <LightDarkToggle
              isLight={isLight}
              onToggle={(nextIsLight) => {
                const nextTheme: Theme = nextIsLight ? 'light' : 'dark'
                setTheme(nextTheme)
                storeTheme(nextTheme)
                setHasUserTheme(true)
              }}
              lightBackgroundColor="var(--toggle-bg-light)"
              darkBackgroundColor="var(--toggle-bg-dark)"
              lightBorderColor="var(--toggle-border-light)"
              darkBorderColor="var(--toggle-border-dark)"
              transitionDuration="250ms"
              aria-label="Toggle light/dark theme"
              title="Toggle light/dark theme"
            />
          </div>
        </div>
      </header>

      {error ? (
        <div className="error">{error}</div>
      ) : (
        <div className="list">{items.map((i) => <FeedItemCard key={i.content_id} item={i} />)}</div>
      )}
    </div>
  )
}
