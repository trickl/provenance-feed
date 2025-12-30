import { useMemo, useState } from 'react'

import type { FeedItem } from '../types'
import {
  provenanceLinkFor,
  provenanceSourceLinkFor,
  sourceKeyFromContentId,
} from '../api'

function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString()
}

export function FeedItemCard({ item }: { item: FeedItem }) {
  const sourceKey = useMemo(() => sourceKeyFromContentId(item.content_id), [item.content_id])
  const provenanceUrl = sourceKey ? provenanceSourceLinkFor(sourceKey) : provenanceLinkFor(item.content_id)
  const imageUrl = item.image_url ?? null

  // In dev, aggressively bust caching for the SVG so grade changes are reflected immediately.
  // In prod, we keep the URL stable and rely on server-side revalidation headers.
  const badgeCacheKey = useMemo(
    () => (import.meta.env.DEV ? String(Date.now()) : '1'),
    [sourceKey],
  )

  const badgeSvgUrl = useMemo(() => {
    const base = import.meta.env.VITE_PROVENANCE_GRAPH_BASE_URL ?? 'http://127.0.0.1:8010'
    const trimmed = base.endsWith('/') ? base.slice(0, -1) : base
    if (!sourceKey) return null
    return `${trimmed}/api/v1/badge/source/${encodeURIComponent(sourceKey)}?format=svg&v=${encodeURIComponent(badgeCacheKey)}`
  }, [badgeCacheKey, sourceKey])

  const [badgeImgOk, setBadgeImgOk] = useState(true)

  return (
    <article className="card">
      <div className="item">
        {imageUrl ? (
          <div className="thumbWrap" aria-hidden="true">
            <img className="thumb" src={imageUrl} alt="" loading="lazy" />
          </div>
        ) : null}

        <div className="main">
          <h2 className="title">{item.title}</h2>
          <div className="meta">
            <span>
              Source:{' '}
              <a href={item.source_url} target="_blank" rel="noreferrer">
                {item.source_name}
              </a>
            </span>
            <span>Published: {formatTimestamp(item.published_at)}</span>
          </div>
        </div>

        <a
          className="badge"
          aria-label="View provenance"
          href={provenanceUrl}
          target="_blank"
          rel="noreferrer"
          title="View provenance"
        >
          {badgeSvgUrl && badgeImgOk ? (
            <img
              className="badgeSvg"
              src={badgeSvgUrl}
              alt={`Trust badge for ${item.source_name}`}
              loading="lazy"
              onError={() => setBadgeImgOk(false)}
            />
          ) : (
            <span className="badgeFallback">View provenance ↗</span>
          )}
        </a>
      </div>
    </article>
  )
}
