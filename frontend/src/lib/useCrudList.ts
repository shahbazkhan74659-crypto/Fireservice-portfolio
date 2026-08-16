import { useEffect, useState } from 'react'

export type LoadState = 'loading' | 'loaded' | 'error'

interface UseCrudListResult<T> {
  items: T[]
  loadState: LoadState
  add: (item: T) => void
  update: (item: T) => void
  remove: (id: number) => void
}

/**
 * Shared fetch-on-mount + local add/update/remove state management used by
 * every Admin Hub "Manager" component (Client Logos, Products,
 * Services, Fire Risk Assessment Items, Mission & Vision, Certifications).
 * Each Manager still owns its own loading-skeleton/grid/table markup and
 * error copy — this hook only centralizes the data-fetching and list
 * mutation logic that was previously hand-copied into every one of them.
 */
export function useCrudList<T extends { id: number }>(endpoint: string): UseCrudListResult<T> {
  const [items, setItems] = useState<T[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false

    setLoadState('loading')

    fetch(endpoint, { credentials: 'same-origin' })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.json()
      })
      .then((data: T[]) => {
        if (cancelled) return
        setItems(data)
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })

    return () => {
      cancelled = true
    }
  }, [endpoint])

  function add(item: T) {
    setItems((prev) => [...prev, item])
  }

  function update(updated: T) {
    setItems((prev) => prev.map((item) => (item.id === updated.id ? updated : item)))
  }

  function remove(id: number) {
    setItems((prev) => prev.filter((item) => item.id !== id))
  }

  return { items, loadState, add, update, remove }
}
