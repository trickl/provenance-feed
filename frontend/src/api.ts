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
  const base = import.meta.env.VITE_PROVENANCE_GRAPH_BASE_URL ?? 'http://127.0.0.1:8010'
  const trimmed = base.endsWith('/') ? base.slice(0, -1) : base
  return `${trimmed}/explain/${encodeURIComponent(contentId)}`
}

export function sourceKeyFromContentId(contentId: string): string | null {
  const idx = contentId.indexOf(':')
  if (idx <= 0) return null
  return contentId.slice(0, idx)
}

export function provenanceSourceLinkFor(sourceKey: string): string {
  const base = import.meta.env.VITE_PROVENANCE_GRAPH_BASE_URL ?? 'http://127.0.0.1:8010'
  const trimmed = base.endsWith('/') ? base.slice(0, -1) : base
  return `${trimmed}/source/${encodeURIComponent(sourceKey)}`
}

export type SourceBadge = {
  source_key: string
  grade: string
  grade_pretty: string
  provisional: boolean
  label: string
  href: string
}

const BADGE_TTL_MS = 10 * 60 * 1000

type BadgeCacheEntry = {
  expiresAt: number
  value?: SourceBadge
  inFlight?: Promise<SourceBadge>
}

const badgeCache = new Map<string, BadgeCacheEntry>()

export async function fetchSourceBadge(
  sourceKey: string,
): Promise<SourceBadge> {
  const now = Date.now()
  const cached = badgeCache.get(sourceKey)
  if (cached?.value && cached.expiresAt > now) {
    return cached.value
  }
  if (cached?.inFlight) {
    return cached.inFlight
  }

  const base = import.meta.env.VITE_PROVENANCE_GRAPH_BASE_URL ?? 'http://127.0.0.1:8010'
  const trimmed = base.endsWith('/') ? base.slice(0, -1) : base
  const url = `${trimmed}/api/v1/badge/source/${encodeURIComponent(sourceKey)}`

  // NOTE: Do not attach AbortSignal here.
  // In React 18 dev StrictMode, effects intentionally mount/unmount twice;
  // aborting an in-flight request can cancel a shared cached Promise and cause
  // permanent fallbacks to "?".
  const p = fetch(url)
    .then(async (res) => {
      if (!res.ok) {
        throw new Error(`Failed to fetch badge (${res.status})`)
      }
      return (await res.json()) as SourceBadge
    })
    .then((badge) => {
      badgeCache.set(sourceKey, { expiresAt: Date.now() + BADGE_TTL_MS, value: badge })
      return badge
    })
    .catch((e) => {
      // Remove failed in-flight promise so later attempts can retry.
      badgeCache.delete(sourceKey)
      throw e
    })

  badgeCache.set(sourceKey, { expiresAt: now + BADGE_TTL_MS, inFlight: p })
  return p
}
