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
      <div className="phase-admin-list" aria-hidden="true">
        {Array.from({ length: 7 }).map((_, i) => (
          <div className="phase-admin-row" key={i}>
            <div className="phase-admin-row__head">
              <Skeleton style={{ width: 70, height: 18 }} />
              <div className="logo-card__admin-actions">
                <Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} />
                <Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} />
              </div>
            </div>
            <Skeleton style={{ width: '100%', height: 140 }} />
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
        <div className="phase-admin-list">
          {phases.map((phase) => (
            <ProcessPhaseCard key={phase.id} phase={phase} onUpdated={update} onDeleted={remove} />
          ))}
        </div>
      )}
    </>
  )
}
