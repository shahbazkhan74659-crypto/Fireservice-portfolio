import { useState, type ChangeEvent, type FormEvent } from 'react'
import {
  editServiceSchema,
  type Service,
  type EditServiceInput,
  type EditServiceErrors,
} from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'
import Modal from '../../lib/Modal'
import { DeleteIcon, EditIcon } from './Icons'

type Dialog = 'none' | 'edit' | 'delete'
type SaveState = 'idle' | 'saving' | 'deleting'

interface Props {
  service: Service
  onUpdated: (service: Service) => void
  onDeleted: (id: number) => void
}

export default function ServiceCard({ service, onUpdated, onDeleted }: Props) {
  const [dialog, setDialog] = useState<Dialog>('none')
  const [name, setName] = useState(service.name)
  const [description, setDescription] = useState(service.description)
  const [file, setFile] = useState<File | null>(null)
  const [errors, setErrors] = useState<EditServiceErrors>({})
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function startEdit() {
    setName(service.name)
    setDescription(service.description)
    setFile(null)
    setErrors({})
    setServerError(null)
    setDialog('edit')
  }

  function closeDialog() {
    setDialog('none')
    setServerError(null)
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null)
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const values: EditServiceInput = { name, description, icon: file ?? undefined }
    const result = editServiceSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: EditServiceErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof EditServiceInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setSaveState('saving')

    const formData = new FormData()
    formData.append('name', result.data.name)
    formData.append('description', result.data.description)
    if (result.data.icon) formData.append('icon', result.data.icon)

    try {
      const res = await fetch(`/api/admin-hub/services/${service.id}/`, {
        method: 'PATCH',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: formData,
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        return
      }
      const updated: Service = await res.json()
      onUpdated(updated)
      setSaveState('idle')
      setDialog('none')
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
    }
  }

  async function handleDelete() {
    setSaveState('deleting')
    setServerError(null)
    try {
      const res = await fetch(`/api/admin-hub/services/${service.id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
      })
      if (!res.ok && res.status !== 204) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        return
      }
      onDeleted(service.id)
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
    }
  }

  return (
    <div className="card">
      <div className="card__icon"><img src={service.icon} alt="" /></div>
      <h3>{service.name}</h3>
      <p>{service.description}</p>

      <div className="logo-card__admin-actions">
        <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
          <EditIcon />
        </button>
        <button type="button" className="btn btn--primary btn--icon" onClick={() => setDialog('delete')} aria-label="Delete">
          <DeleteIcon />
        </button>
      </div>

      <Modal open={dialog === 'edit'} onClose={closeDialog} title="Edit Service">
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`service-name-${service.id}`}>Name</label>
            <input
              id={`service-name-${service.id}`}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor={`service-description-${service.id}`}>Description</label>
            <textarea
              id={`service-description-${service.id}`}
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.description && <p className="form-note">{errors.description}</p>}
          </div>
          <div className="field">
            <label htmlFor={`service-icon-${service.id}`}>Replace Icon (optional)</label>
            <input
              id={`service-icon-${service.id}`}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={saveState === 'saving'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.icon && <p className="form-note">{errors.icon}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={saveState === 'saving'}>
              {saveState === 'saving' ? 'Saving…' : 'Save'}
            </button>
            <button type="button" className="btn btn--outline" onClick={closeDialog} disabled={saveState === 'saving'}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Service">
        <p className="modal__body">Delete &quot;{service.name}&quot;? This can&apos;t be undone.</p>

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
    </div>
  )
}
