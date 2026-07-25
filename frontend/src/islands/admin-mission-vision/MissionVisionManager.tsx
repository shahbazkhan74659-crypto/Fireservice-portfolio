import { useEffect, useState } from 'react'
import MissionVisionCard from './MissionVisionCard'
import Skeleton from '../../lib/Skeleton'
import type { MissionVisionItem } from './schema'

type LoadState = 'loading' | 'loaded' | 'error'

export default function MissionVisionManager() {
  const [items, setItems] = useState<MissionVisionItem[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false

    fetch('/api/admin-hub/mission-vision/', { credentials: 'same-origin' })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.json()
      })
      .then((data: MissionVisionItem[]) => {
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
  }, [])

  function handleUpdated(updated: MissionVisionItem) {
    setItems((prev) => prev.map((item) => (item.id === updated.id ? updated : item)))
  }

  function handleDeleted(id: number) {
    setItems((prev) => prev.filter((item) => item.id !== id))
  }

  if (loadState === 'loading') {
    return (
      <div className="grid grid--mission" aria-hidden="true">
        {Array.from({ length: 2 }).map((_, i) => (
          <div className="card admin-mv-card" key={i}>
            <Skeleton className="skeleton-text" style={{ width: '50%', height: 22, marginBottom: 16 }} />
            <Skeleton className="skeleton-text" style={{ width: '100%' }} />
            <Skeleton className="skeleton-text" style={{ width: '95%' }} />
            <Skeleton className="skeleton-text" style={{ width: '80%', marginBottom: 16 }} />
            {Array.from({ length: 3 }).map((__, j) => (
              <Skeleton className="skeleton-text" style={{ width: `${70 - j * 10}%` }} key={j} />
            ))}
          </div>
        ))}
      </div>
    )
  }

  if (loadState === 'error') {
    return <p className="form-note">Couldn&apos;t load Mission &amp; Vision. Reload the page and try again.</p>
  }

  if (items.length === 0) {
    return <p className="section__sub">No Mission &amp; Vision items left. All items have been deleted.</p>
  }

  return (
    <div className="grid grid--mission">
      {items.map((item) => (
        <MissionVisionCard key={item.id} item={item} onUpdated={handleUpdated} onDeleted={handleDeleted} />
      ))}
    </div>
  )
}
