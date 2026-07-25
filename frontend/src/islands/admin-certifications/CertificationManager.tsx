import AddCertificationForm from './AddCertificationForm'
import CertificationRow from './CertificationRow'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { Certification } from './schema'

const ENDPOINT = '/api/admin-hub/certifications/'

export default function CertificationManager() {
  const { items: certifications, loadState, add, remove } = useCrudList<Certification>(ENDPOINT)

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
      <AddCertificationForm onAdded={add} />
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
                <CertificationRow key={certification.id} certification={certification} onDeleted={remove} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
