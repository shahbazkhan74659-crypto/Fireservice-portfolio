import AddProcessPhaseForm from './AddProcessPhaseForm'
import ProcessPhaseCard from './ProcessPhaseCard'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { ProcessPhase } from './schema'

const ENDPOINT = '/api/admin-hub/process-phases/'

export default function ProcessPhaseManager() {
  const { items: phases, loadState, add, update, remove } = useCrudList<ProcessPhase>(ENDPOINT)

  if (loadState === 'loading') {
    return (
      <div className="logo-grid" aria-hidden="true">
        {Array.from({ length: 7 }).map((_, i) => (
          <div className="logo-card logo-card--admin" key={i}>
            <Skeleton style={{ width: '100%', height: 50 }} />
            <div className="logo-card__admin-actions">
              <Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} />
              <Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (loadState === 'error') {
    return <p className="form-note">Couldn&apos;t load process phase photos. Reload the page and try again.</p>
  }

  return (
    <>
      <AddProcessPhaseForm onAdded={add} />
      {phases.length === 0 ? (
        <p className="section__sub">No process phase photos yet.</p>
      ) : (
        <div className="logo-grid">
          {phases.map((phase) => (
            <ProcessPhaseCard key={phase.id} phase={phase} onUpdated={update} onDeleted={remove} />
          ))}
        </div>
      )}
    </>
  )
}
