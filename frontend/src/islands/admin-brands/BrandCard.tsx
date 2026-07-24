import { useState, type ChangeEvent, type FormEvent } from 'react'
import {
  editBrandSchema,
  type Brand,
  type EditBrandInput,
  type EditBrandErrors,
} from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'
import Modal from '../../lib/Modal'
import { DeleteIcon, EditIcon } from './Icons'

type Dialog = 'none' | 'edit' | 'delete'
type SaveState = 'idle' | 'saving' | 'deleting'

interface Props {
  brand: Brand
  onUpdated: (brand: Brand) => void
  onDeleted: (id: number) => void
}

export default function BrandCard({ brand, onUpdated, onDeleted }: Props) {
  const [dialog, setDialog] = useState<Dialog>('none')
  const [name, setName] = useState(brand.name)
  const [file, setFile] = useState<File | null>(null)
  const [errors, setErrors] = useState<EditBrandErrors>({})
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function startEdit() {
    setName(brand.name)
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

    const values: EditBrandInput = { name, image: file ?? undefined }
    const result = editBrandSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: EditBrandErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof EditBrandInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setSaveState('saving')

    const formData = new FormData()
    formData.append('name', result.data.name)
    if (result.data.image) formData.append('image', result.data.image)

    try {
      const res = await fetch(`/api/admin-hub/brands/${brand.id}/`, {
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
      const updated: Brand = await res.json()
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
      const res = await fetch(`/api/admin-hub/brands/${brand.id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
      })
      if (!res.ok && res.status !== 204) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        return
      }
      onDeleted(brand.id)
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
    }
  }

  return (
    <div className="logo-card logo-card--admin">
      <img src={brand.image} alt={brand.name} />

      <div className="logo-card__admin-actions">
        <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
          <EditIcon />
        </button>
        <button type="button" className="btn btn--primary btn--icon" onClick={() => setDialog('delete')} aria-label="Delete">
          <DeleteIcon />
        </button>
      </div>

      <Modal open={dialog === 'edit'} onClose={closeDialog} title="Edit Brand">
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`brand-name-${brand.id}`}>Name</label>
            <input
              id={`brand-name-${brand.id}`}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor={`brand-file-${brand.id}`}>Replace Image (optional)</label>
            <input
              id={`brand-file-${brand.id}`}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={saveState === 'saving'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.image && <p className="form-note">{errors.image}</p>}
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

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Brand">
        <p className="modal__body">Delete &quot;{brand.name}&quot;? This can&apos;t be undone.</p>

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
