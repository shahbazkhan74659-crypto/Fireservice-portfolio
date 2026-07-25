import AddFireRiskItemForm from './AddFireRiskItemForm'
import FireRiskItemRow from './FireRiskItemRow'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { FireRiskAssessmentItem } from './schema'

const ENDPOINT = '/api/admin-hub/fire-risk-items/'

export default function FireRiskItemManager() {
  const { items, loadState, add, update, remove } = useCrudList<FireRiskAssessmentItem>(ENDPOINT)

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
      <AddFireRiskItemForm onAdded={add} />
      {items.length === 0 ? (
        <p className="section__sub">No checklist items yet.</p>
      ) : (
        items.map((item) => (
          <FireRiskItemRow key={item.id} item={item} onUpdated={update} onDeleted={remove} />
        ))
      )}
    </>
  )
}
