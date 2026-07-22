import { useState, type ChangeEvent, type FormEvent } from 'react'
import {
  editClientLogoSchema,
  type ClientLogo,
  type EditClientLogoInput,
  type EditClientLogoErrors,
} from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'
import { DeleteIcon, EditIcon } from './Icons'

type Mode = 'view' | 'edit' | 'confirm-delete'
type SaveState = 'idle' | 'saving' | 'deleting'

interface Props {
  logo: ClientLogo
  onUpdated: (logo: ClientLogo) => void
  onDeleted: (id: number) => void
}

export default function ClientLogoCard({ logo, onUpdated, onDeleted }: Props) {
  const [mode, setMode] = useState<Mode>('view')
  const [name, setName] = useState(logo.name)
  const [file, setFile] = useState<File | null>(null)
  const [errors, setErrors] = useState<EditClientLogoErrors>({})
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function startEdit() {
    setName(logo.name)
    setFile(null)
    setErrors({})
    setServerError(null)
    setMode('edit')
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null)
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const values: EditClientLogoInput = { name, image: file ?? undefined }
    const result = editClientLogoSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: EditClientLogoErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof EditClientLogoInput
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
      const res = await fetch(`/api/admin-hub/client-logos/${logo.id}/`, {
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
      const updated: ClientLogo = await res.json()
      onUpdated(updated)
      setSaveState('idle')
      setMode('view')
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
    }
  }

  async function handleDelete() {
    setSaveState('deleting')
    setServerError(null)
    try {
      const res = await fetch(`/api/admin-hub/client-logos/${logo.id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
      })
      if (!res.ok && res.status !== 204) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        setMode('view')
        return
      }
      onDeleted(logo.id)
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
      setMode('view')
    }
  }

  if (mode === 'edit') {
    return (
      <div className="logo-card logo-card--admin">
        <img src={logo.image} alt={logo.name} />
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`logo-name-${logo.id}`}>Name</label>
            <input
              id={`logo-name-${logo.id}`}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor={`logo-file-${logo.id}`}>Replace Image (optional)</label>
            <input
              id={`logo-file-${logo.id}`}
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
            <button type="button" className="btn btn--outline" onClick={() => setMode('view')} disabled={saveState === 'saving'}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    )
  }

  return (
    <div className="logo-card logo-card--admin">
      <img src={logo.image} alt={logo.name} />

      {serverError && <p className="form-note">{serverError}</p>}

      <div className="logo-card__admin-actions">
        {mode === 'confirm-delete' ? (
          <>
            <span className="admin-mv-confirm-text">Delete?</span>
            <button type="button" className="btn btn--primary" onClick={handleDelete} disabled={saveState === 'deleting'}>
              {saveState === 'deleting' ? 'Deleting…' : 'Yes'}
            </button>
            <button type="button" className="btn btn--outline" onClick={() => setMode('view')} disabled={saveState === 'deleting'}>
              Cancel
            </button>
          </>
        ) : (
          <>
            <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
              <EditIcon />
            </button>
            <button type="button" className="btn btn--primary btn--icon" onClick={() => setMode('confirm-delete')} aria-label="Delete">
              <DeleteIcon />
            </button>
          </>
        )}
      </div>
    </div>
  )
}
