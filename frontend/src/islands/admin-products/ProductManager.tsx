import { useEffect, useState } from 'react'
import AddProductForm from './AddProductForm'
import ProductCard from './ProductCard'
import Skeleton from '../../lib/Skeleton'
import type { Product } from './schema'

type LoadState = 'loading' | 'loaded' | 'error'

export default function ProductManager() {
  const [products, setProducts] = useState<Product[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false

    fetch('/api/admin-hub/products/', { credentials: 'same-origin' })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.json()
      })
      .then((data: Product[]) => {
        if (cancelled) return
        setProducts(data)
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })

    return () => {
      cancelled = true
    }
  }, [])

  function handleAdded(product: Product) {
    setProducts((prev) => [...prev, product])
  }

  function handleUpdated(updated: Product) {
    setProducts((prev) => prev.map((product) => (product.id === updated.id ? updated : product)))
  }

  function handleDeleted(id: number) {
    setProducts((prev) => prev.filter((product) => product.id !== id))
  }

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
      <AddProductForm onAdded={handleAdded} />
      {products.length === 0 ? (
        <p className="section__sub">No products yet.</p>
      ) : (
        <div className="logo-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onUpdated={handleUpdated} onDeleted={handleDeleted} />
          ))}
        </div>
      )}
    </>
  )
}
