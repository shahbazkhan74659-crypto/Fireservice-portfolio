import AddProductForm from './AddProductForm'
import ProductCard from './ProductCard'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { Product } from './schema'

const ENDPOINT = '/api/admin-hub/products/'

export default function ProductManager() {
  const { items: products, loadState, add, update, remove } = useCrudList<Product>(ENDPOINT)

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
    return <p className="form-note">Couldn&apos;t load products. Reload the page and try again.</p>
  }

  return (
    <>
      <AddProductForm onAdded={add} />
      {products.length === 0 ? (
        <p className="section__sub">No products yet.</p>
      ) : (
        <div className="logo-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onUpdated={update} onDeleted={remove} />
          ))}
        </div>
      )}
    </>
  )
}
