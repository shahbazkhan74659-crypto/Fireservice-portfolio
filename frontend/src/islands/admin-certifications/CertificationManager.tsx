import { useEffect, useState } from 'react'
import AddCertificationForm from './AddCertificationForm'
import CertificationRow from './CertificationRow'
import Skeleton from '../../lib/Skeleton'
import type { Certification } from './schema'

type LoadState = 'loading' | 'loaded' | 'error'

export default function CertificationManager() {
  const [certifications, setCertifications] = useState<Certification[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')

  useEffect(() => {
    let cancelled = false

    fetch('/api/admin-hub/certifications/', { credentials: 'same-origin' })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.json()
      })
      .then((data: Certification[]) => {
        if (cancelled) return
        setCertifications(data)
        setLoadState('loaded')
      })
      .catch(() => {
        if (!cancelled) setLoadState('error')
      })

    return () => {
      cancelled = true
    }
  }, [])

  function handleAdded(certification: Certification) {
    setCertifications((prev) => [...prev, certification])
  }

  function handleDeleted(id: number) {
    setCertifications((prev) => prev.filter((certification) => certification.id !== id))
  }

  if (loadState === 'loading') {
    return (
      <div className="cert-table-wrap" aria-hidden="true">
        <table className="cert-table">
          <thead>
            <tr>
              <th>Preview</th>
              <th>Certificate</th>
              <th>Description</th>
              <th>Validity / Reg. No.</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 4 }).map((_, i) => (
              <tr key={i}>
                <td className="cert-table__preview"><Skeleton style={{ width: 48, height: 48 }} /></td>
                <td><Skeleton className="skeleton-text" style={{ width: 120 }} /></td>
                <td><Skeleton className="skeleton-text" style={{ width: 160 }} /></td>
                <td><Skeleton className="skeleton-text" style={{ width: 100 }} /></td>
                <td><Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (loadState === 'error') {
    return <p className="form-note">Couldn&apos;t load certificates. Reload the page and try again.</p>
  }

  return (
    <>
      <AddCertificationForm onAdded={handleAdded} />
      {certifications.length === 0 ? (
        <p className="section__sub">No certificates yet.</p>
      ) : (
        <div className="cert-table-wrap">
          <table className="cert-table">
            <thead>
              <tr>
                <th>Preview</th>
                <th>Certificate</th>
                <th>Description</th>
                <th>Validity / Reg. No.</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {certifications.map((certification) => (
                <CertificationRow key={certification.id} certification={certification} onDeleted={handleDeleted} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
