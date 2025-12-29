import type { FeedItem } from './types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function fetchFeed(limit = 50): Promise<FeedItem[]> {
  const url = new URL('/api/feed', API_BASE)
  url.searchParams.set('limit', String(limit))
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`Failed to fetch feed (${res.status})`)
  }
  return (await res.json()) as FeedItem[]
}

export function provenanceLinkFor(contentId: string): string {
  const base = import.meta.env.VITE_PROVENANCE_URL_BASE ?? 'https://provenance.example/item'
  return `${base}/${encodeURIComponent(contentId)}`
}
