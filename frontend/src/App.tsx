import { useEffect, useState } from 'react'

import { fetchFeed } from './api'
import type { FeedItem } from './types'
import { FeedItemCard } from './components/FeedItemCard'

export function App() {
  const [items, setItems] = useState<FeedItem[]>([])
  const [error, setError] = useState<string | null>(null)

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
        <h1>provenance-feed</h1>
        <p>Chronological feed with a reserved placeholder for provenance (no trust logic implemented).</p>
      </header>

      {error ? (
        <div className="error">{error}</div>
      ) : (
        <div className="list">{items.map((i) => <FeedItemCard key={i.content_id} item={i} />)}</div>
      )}
    </div>
  )
}
