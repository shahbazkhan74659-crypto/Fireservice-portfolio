import { useEffect, useState } from 'react'
import AddBrandForm from './AddBrandForm'
import BrandCard from './BrandCard'
import Skeleton from '../../lib/Skeleton'
import type { Brand } from './schema'

type LoadState = 'loading' | 'loaded' | 'error'

export default function BrandManager() {
  const [brands, setBrands] = useState<Brand[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false

    fetch('/api/admin-hub/brands/', { credentials: 'same-origin' })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.json()
      })
      .then((data: Brand[]) => {
        if (cancelled) return
        setBrands(data)
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })

    return () => {
      cancelled = true
    }
  }, [])

  function handleAdded(brand: Brand) {
    setBrands((prev) => [...prev, brand])
  }

  function handleUpdated(updated: Brand) {
    setBrands((prev) => prev.map((brand) => (brand.id === updated.id ? updated : brand)))
  }

  function handleDeleted(id: number) {
    setBrands((prev) => prev.filter((brand) => brand.id !== id))
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
    return <p className="form-note">Couldn&apos;t load brands. Reload the page and try again.</p>
  }

  return (
    <>
      <AddBrandForm onAdded={handleAdded} />
      {brands.length === 0 ? (
        <p className="section__sub">No brands yet.</p>
      ) : (
        <div className="logo-grid">
          {brands.map((brand) => (
            <BrandCard key={brand.id} brand={brand} onUpdated={handleUpdated} onDeleted={handleDeleted} />
          ))}
        </div>
      )}
    </>
  )
}
