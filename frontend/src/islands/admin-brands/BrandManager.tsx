import { useEffect, useState } from 'react'
import AddBrandForm from './AddBrandForm'
import BrandCard from './BrandCard'
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
    return <p className="section__sub">Loading brands…</p>
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
