export type FeedItem = {
  content_id: string
  title: string
  source_name: string
  source_url: string
  published_at: string

  image_url?: string | null
  image_source?: 'rss' | 'page_meta' | 'none' | string | null
  image_last_checked?: string | null
}
