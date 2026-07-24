import { useState, type FormEvent } from 'react'
import { addFireRiskItemSchema, type AddFireRiskItemErrors, type AddFireRiskItemInput, type FireRiskAssessmentItem } from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'
import Modal from '../../lib/Modal'

type SubmitState = 'idle' | 'submitting'

interface Props {
  onAdded: (item: FireRiskAssessmentItem) => void
}

export default function AddFireRiskItemForm({ onAdded }: Props) {
  const [open, setOpen] = useState(false)
  const [text, setText] = useState('')
  const [errors, setErrors] = useState<AddFireRiskItemErrors>({})
  const [state, setState] = useState<SubmitState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function reset() {
    setText('')
    setErrors({})
    setServerError(null)
  }

  function closeModal() {
    reset()
    setOpen(false)
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = addFireRiskItemSchema.safeParse({ text })
    if (!result.success) {
      const fieldErrors: AddFireRiskItemErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof AddFireRiskItemInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await fetch('/api/admin-hub/fire-risk-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify(result.data),
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }
      const created: FireRiskAssessmentItem = await res.json()
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

      <Modal open={open} onClose={closeModal} title="Add Fire Risk Assessment Item">
        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-fire-risk-item-text">Text</label>
            <input
              id="new-fire-risk-item-text"
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.text && <p className="form-note">{errors.text}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Item'}
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
