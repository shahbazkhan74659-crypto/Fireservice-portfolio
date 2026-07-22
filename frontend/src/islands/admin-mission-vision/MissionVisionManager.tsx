import { useEffect, useState } from 'react'
import MissionVisionCard from './MissionVisionCard'
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
    return <p className="section__sub">Loading Mission &amp; Vision…</p>
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
