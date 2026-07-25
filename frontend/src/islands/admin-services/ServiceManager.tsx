import AddServiceForm from './AddServiceForm'
import ServiceCard from './ServiceCard'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { Service } from './schema'

const ENDPOINT = '/api/admin-hub/services/'

export default function ServiceManager() {
  const { items: services, loadState, add, update, remove } = useCrudList<Service>(ENDPOINT)

  if (loadState === 'loading') {
    return (
      <div className="grid grid--services" aria-hidden="true">
        {Array.from({ length: 4 }).map((_, i) => (
          <div className="card" key={i}>
            <Skeleton style={{ width: 52, height: 52, borderRadius: 12, marginBottom: 18 }} />
            <Skeleton className="skeleton-text" style={{ width: '70%', height: 20, marginBottom: 12 }} />
            <Skeleton className="skeleton-text" style={{ width: '100%' }} />
            <Skeleton className="skeleton-text" style={{ width: '85%' }} />
          </div>
        ))}
      </div>
    )
  }

  if (loadState === 'error') {
    return <p className="form-note">Couldn&apos;t load services. Reload the page and try again.</p>
  }

  return (
    <>
      <AddServiceForm onAdded={add} />
      {services.length === 0 ? (
        <p className="section__sub">No services yet.</p>
      ) : (
        <div className="grid grid--services">
          {services.map((service) => (
            <ServiceCard key={service.id} service={service} onUpdated={update} onDeleted={remove} />
          ))}
        </div>
      )}
    </>
  )
}
