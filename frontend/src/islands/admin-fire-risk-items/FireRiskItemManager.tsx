import { useEffect, useState } from 'react'
import AddFireRiskItemForm from './AddFireRiskItemForm'
import FireRiskItemRow from './FireRiskItemRow'
import Skeleton from '../../lib/Skeleton'
import type { FireRiskAssessmentItem } from './schema'

type LoadState = 'loading' | 'loaded' | 'error'

export default function FireRiskItemManager() {
  const [items, setItems] = useState<FireRiskAssessmentItem[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false

    fetch('/api/admin-hub/fire-risk-items/', { credentials: 'same-origin' })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.json()
      })
      .then((data: FireRiskAssessmentItem[]) => {
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

  function handleAdded(item: FireRiskAssessmentItem) {
    setItems((prev) => [...prev, item])
  }

  function handleUpdated(updated: FireRiskAssessmentItem) {
    setItems((prev) => prev.map((item) => (item.id === updated.id ? updated : item)))
  }

  function handleDeleted(id: number) {
    setItems((prev) => prev.filter((item) => item.id !== id))
  }

  if (loadState === 'loading') {
    return (
      <div aria-hidden="true">
        {Array.from({ length: 5 }).map((_, i) => (
          <div className="admin-mv-point" key={i}>
            <Skeleton className="skeleton-text" style={{ flex: 1, height: 16, marginBottom: 0 }} />
            <Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} />
            <Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} />
          </div>
        ))}
      </div>
    )
  }

  if (loadState === 'error') {
    return <p className="form-note">Couldn&apos;t load checklist items. Reload the page and try again.</p>
  }

  return (
    <>
      <AddFireRiskItemForm onAdded={handleAdded} />
      {items.length === 0 ? (
        <p className="section__sub">No checklist items yet.</p>
      ) : (
        items.map((item) => (
          <FireRiskItemRow key={item.id} item={item} onUpdated={handleUpdated} onDeleted={handleDeleted} />
        ))
      )}
    </>
  )
}
