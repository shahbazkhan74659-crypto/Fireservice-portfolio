import { useEditDelete } from '../../lib/useEditDelete'
import type { Certification } from './schema'
import Modal from '../../lib/Modal'
import { DeleteIcon } from '../../lib/Icons'

const ENDPOINT = '/api/admin-hub/certifications/'

interface Props {
  certification: Certification
  onDeleted: (id: number) => void
}

export default function CertificationRow({ certification, onDeleted }: Props) {
  const { dialog, saveState, serverError, openDelete, closeDialog, remove } =
    useEditDelete<Certification>(ENDPOINT, certification.id)

  async function handleDelete() {
    if (await remove()) onDeleted(certification.id)
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
        <button type="button" className="btn btn--primary btn--icon" onClick={openDelete} aria-label="Delete">
          <DeleteIcon />
        </button>

        <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Certificate">
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
