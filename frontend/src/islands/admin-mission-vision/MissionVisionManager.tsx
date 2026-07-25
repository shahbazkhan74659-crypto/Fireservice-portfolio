import MissionVisionCard from './MissionVisionCard'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { MissionVisionItem } from './schema'

const ENDPOINT = '/api/admin-hub/mission-vision/'

export default function MissionVisionManager() {
  const { items, loadState, update, remove } = useCrudList<MissionVisionItem>(ENDPOINT)

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
        <MissionVisionCard key={item.id} item={item} onUpdated={update} onDeleted={remove} />
      ))}
    </div>
  )
}
