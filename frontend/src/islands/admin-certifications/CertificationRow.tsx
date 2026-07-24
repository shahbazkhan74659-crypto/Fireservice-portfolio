import { useState } from 'react'
import type { Certification } from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'
import Modal from '../../lib/Modal'
import { DeleteIcon } from './Icons'

type SaveState = 'idle' | 'deleting'

interface Props {
  certification: Certification
  onDeleted: (id: number) => void
}

export default function CertificationRow({ certification, onDeleted }: Props) {
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function closeDialog() {
    setConfirmOpen(false)
    setServerError(null)
  }

  async function handleDelete() {
    setSaveState('deleting')
    setServerError(null)
    try {
      const res = await fetch(`/api/admin-hub/certifications/${certification.id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
      })
      if (!res.ok && res.status !== 204) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        return
      }
      onDeleted(certification.id)
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
    }
  }

  return (
    <tr>
      <td className="cert-table__preview">
        <a href={certification.image} target="_blank" rel="noopener" aria-label={`View full ${certification.name} certificate`}>
          <img src={certification.image} alt={certification.name} />
        </a>
      </td>
      <td className="cert-table__name">{certification.name}</td>
      <td className="cert-table__desc">{certification.description}</td>
      <td className="cert-table__meta">{certification.meta}</td>
      <td className="cert-table__action">
        <button type="button" className="btn btn--primary btn--icon" onClick={() => setConfirmOpen(true)} aria-label="Delete">
          <DeleteIcon />
        </button>

        <Modal open={confirmOpen} onClose={closeDialog} title="Delete Certificate">
          <p className="modal__body">Delete &quot;{certification.name}&quot;? This can&apos;t be undone.</p>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="button" className="btn btn--primary" onClick={handleDelete} disabled={saveState === 'deleting'}>
              {saveState === 'deleting' ? 'Deleting…' : 'Yes, Delete'}
            </button>
            <button type="button" className="btn btn--outline" onClick={closeDialog} disabled={saveState === 'deleting'}>
              Cancel
            </button>
          </div>
        </Modal>
      </td>
    </tr>
  )
}
