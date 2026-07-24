import { useState, type ChangeEvent, type FormEvent } from 'react'
import { addBrandSchema, type AddBrandErrors, type AddBrandInput, type Brand } from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'
import Modal from '../../lib/Modal'

type SubmitState = 'idle' | 'submitting'

interface Props {
  onAdded: (brand: Brand) => void
}

export default function AddBrandForm({ onAdded }: Props) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [errors, setErrors] = useState<AddBrandErrors>({})
  const [state, setState] = useState<SubmitState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function reset() {
    setName('')
    setFile(null)
    setErrors({})
    setServerError(null)
  }

  function closeModal() {
    reset()
    setOpen(false)
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null)
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const values = { name, image: file }
    const result = addBrandSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: AddBrandErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof AddBrandInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    const formData = new FormData()
    formData.append('name', result.data.name)
    formData.append('image', result.data.image)

    try {
      const res = await fetch('/api/admin-hub/brands/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: formData,
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }
      const created: Brand = await res.json()
      onAdded(created)
      reset()
      setOpen(false)
      setState('idle')
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setState('idle')
    }
  }

  return (
    <>
      <div className="client-logos__admin-actions">
        <button type="button" className="btn btn--primary" onClick={() => setOpen(true)}>+ Add</button>
      </div>

      <Modal open={open} onClose={closeModal} title="Add Brand">
        <form className="logo-add-form" onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-brand-name">Name</label>
            <input
              id="new-brand-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-brand-file">Brand Logo Image</label>
            <input
              id="new-brand-file"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={state === 'submitting'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.image && <p className="form-note">{errors.image}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Brand'}
            </button>
            <button type="button" className="btn btn--outline" onClick={closeModal} disabled={state === 'submitting'}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </>
  )
}
