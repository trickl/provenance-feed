import type { FeedItem } from '../types'
import { provenanceLinkFor } from '../api'

function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString()
}

export function FeedItemCard({ item }: { item: FeedItem }) {
  const provenanceUrl = provenanceLinkFor(item.content_id)
  const imageUrl = item.image_url ?? null

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

        <div className="badge" aria-label="provenance context badge">
          <a
            href={provenanceUrl}
            target="_blank"
            rel="noreferrer"
            title="View provenance"
          >
            View provenance <span aria-hidden="true">↗</span>
          </a>
        </div>
      </div>
    </article>
  )
}
