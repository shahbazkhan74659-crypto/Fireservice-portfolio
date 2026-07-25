import { useEffect, useState } from 'react'
import AddServiceForm from './AddServiceForm'
import ServiceCard from './ServiceCard'
import Skeleton from '../../lib/Skeleton'
import type { Service } from './schema'

type LoadState = 'loading' | 'loaded' | 'error'

export default function ServiceManager() {
  const [services, setServices] = useState<Service[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false

    fetch('/api/admin-hub/services/', { credentials: 'same-origin' })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.json()
      })
      .then((data: Service[]) => {
        if (cancelled) return
        setServices(data)
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })

    return () => {
      cancelled = true
    }
  }, [])

  function handleAdded(service: Service) {
    setServices((prev) => [...prev, service])
  }

  function handleUpdated(updated: Service) {
    setServices((prev) => prev.map((service) => (service.id === updated.id ? updated : service)))
  }

  function handleDeleted(id: number) {
    setServices((prev) => prev.filter((service) => service.id !== id))
  }

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
      <AddServiceForm onAdded={handleAdded} />
      {services.length === 0 ? (
        <p className="section__sub">No services yet.</p>
      ) : (
        <div className="grid grid--services">
          {services.map((service) => (
            <ServiceCard key={service.id} service={service} onUpdated={handleUpdated} onDeleted={handleDeleted} />
          ))}
        </div>
      )}
    </>
  )
}
