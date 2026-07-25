import AddClientLogoForm from './AddClientLogoForm'
import ClientLogoCard from './ClientLogoCard'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { ClientLogo } from './schema'

const ENDPOINT = '/api/admin-hub/client-logos/'

export default function ClientLogoManager() {
  const { items: logos, loadState, add, update, remove } = useCrudList<ClientLogo>(ENDPOINT)

  if (loadState === 'loading') {
    return (
      <div className="logo-grid" aria-hidden="true">
        {Array.from({ length: 5 }).map((_, i) => (
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
    return <p className="form-note">Couldn&apos;t load client logos. Reload the page and try again.</p>
  }

  return (
    <>
      <AddClientLogoForm onAdded={add} />
      {logos.length === 0 ? (
        <p className="section__sub">No client logos yet.</p>
      ) : (
        <div className="logo-grid">
          {logos.map((logo) => (
            <ClientLogoCard key={logo.id} logo={logo} onUpdated={update} onDeleted={remove} />
          ))}
        </div>
      )}
    </>
  )
}
