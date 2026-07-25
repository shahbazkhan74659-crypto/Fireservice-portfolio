import AddBrandForm from './AddBrandForm'
import BrandCard from './BrandCard'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { Brand } from './schema'

const ENDPOINT = '/api/admin-hub/brands/'

export default function BrandManager() {
  const { items: brands, loadState, add, update, remove } = useCrudList<Brand>(ENDPOINT)

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
    return <p className="form-note">Couldn&apos;t load brands. Reload the page and try again.</p>
  }

  return (
    <>
      <AddBrandForm onAdded={add} />
      {brands.length === 0 ? (
        <p className="section__sub">No brands yet.</p>
      ) : (
        <div className="logo-grid">
          {brands.map((brand) => (
            <BrandCard key={brand.id} brand={brand} onUpdated={update} onDeleted={remove} />
          ))}
        </div>
      )}
    </>
  )
}
