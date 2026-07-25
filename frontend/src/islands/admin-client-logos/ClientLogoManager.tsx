import { useEffect, useState } from 'react'
import AddClientLogoForm from './AddClientLogoForm'
import ClientLogoCard from './ClientLogoCard'
import Skeleton from '../../lib/Skeleton'
import type { ClientLogo } from './schema'

type LoadState = 'loading' | 'loaded' | 'error'

export default function ClientLogoManager() {
  const [logos, setLogos] = useState<ClientLogo[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false

    fetch('/api/admin-hub/client-logos/', { credentials: 'same-origin' })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.json()
      })
      .then((data: ClientLogo[]) => {
        if (cancelled) return
        setLogos(data)
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })

    return () => {
      cancelled = true
    }
  }, [])

  function handleAdded(logo: ClientLogo) {
    setLogos((prev) => [...prev, logo])
  }

  function handleUpdated(updated: ClientLogo) {
    setLogos((prev) => prev.map((logo) => (logo.id === updated.id ? updated : logo)))
  }

  function handleDeleted(id: number) {
    setLogos((prev) => prev.filter((logo) => logo.id !== id))
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
    return <p className="form-note">Couldn&apos;t load client logos. Reload the page and try again.</p>
  }

  return (
    <>
      <AddClientLogoForm onAdded={handleAdded} />
      {logos.length === 0 ? (
        <p className="section__sub">No client logos yet.</p>
      ) : (
        <div className="logo-grid">
          {logos.map((logo) => (
            <ClientLogoCard key={logo.id} logo={logo} onUpdated={handleUpdated} onDeleted={handleDeleted} />
          ))}
        </div>
      )}
    </>
  )
}
