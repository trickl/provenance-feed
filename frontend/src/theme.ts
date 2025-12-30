export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'provenance-feed.theme'

export function getSystemTheme(): Theme {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function loadStoredTheme(): Theme | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (raw === 'light' || raw === 'dark') return raw
    return null
  } catch {
    return null
  }
}

export function storeTheme(theme: Theme): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, theme)
  } catch {
    // best-effort only
  }
}

export function hasStoredTheme(): boolean {
  return loadStoredTheme() !== null
}

export function applyTheme(theme: Theme): void {
  // Keep the DOM mutation tiny and predictable.
  document.documentElement.dataset.theme = theme
}
