import { useEffect, useMemo, useState } from 'react'

import type { FeedItem } from '../types'
import {
  fetchSourceBadge,
  provenanceLinkFor,
  provenanceSourceLinkFor,
  sourceKeyFromContentId,
  type SourceBadge,
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

  const [badge, setBadge] = useState<SourceBadge | null>(null)

  useEffect(() => {
    let cancelled = false
    if (!sourceKey) {
      setBadge(null)
      return () => {
        cancelled = true
      }
    }

    fetchSourceBadge(sourceKey)
      .then((b) => {
        if (!cancelled) setBadge(b)
      })
      .catch(() => {
        // Best-effort only: the feed remains usable even if provenance-graph is down.
        if (!cancelled) setBadge(null)
      })
    return () => {
      cancelled = true
    }
  }, [item.content_id, sourceKey])

  const trustLabel = useMemo(() => {
    if (!badge) return 'Trust: ?'
    return badge.label
  }, [badge])

  const trustText = useMemo(() => {
    if (!badge) return '?'
    return badge.grade_pretty
  }, [badge])

  const badgeGradeClass = useMemo(() => {
    const g = badge?.grade ?? 'UNKNOWN'
    // Normalize to something CSS-friendly.
    return `badge--${g.toLowerCase()}`
  }, [badge])

  const badgeGlyph = useMemo(() => {
    const g = badge?.grade ?? 'UNKNOWN'
    // Visual signal only; does not change semantics.
    if (g === 'A_PLUS' || g === 'A') return '▲'
    if (g === 'B') return '●'
    if (g === 'C') return '◆'
    if (g === 'D' || g === 'F') return '▼'
    return '…'
  }, [badge])

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

        <div
          className={`badge ${badgeGradeClass}${badge?.provisional ? ' badge--provisional' : ''}`}
          aria-label="source trust badge"
        >
          <a
            href={provenanceUrl}
            target="_blank"
            rel="noreferrer"
            title={trustLabel}
          >
            <span className="badgeGlyph" aria-hidden="true">{badgeGlyph}</span>
            Trust: {trustText}
            {badge?.provisional ? (
              <>
                <span className="badgeProvisional" aria-hidden="true"> ~</span>
                <span className="muted"> (provisional)</span>
              </>
            ) : null}{' '}
            <span aria-hidden="true">↗</span>
          </a>
        </div>
      </div>
    </article>
  )
}
