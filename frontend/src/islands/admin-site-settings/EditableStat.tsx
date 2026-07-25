import { useState, type FormEvent } from 'react'
import { editStatValueSchema, type SiteSetting, type SiteSettingField } from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'
import Modal from '../../lib/Modal'

type SaveState = 'idle' | 'saving'

interface Props {
  field: SiteSettingField
  label: string
  suffix?: string
  initialValue: number
}

export default function EditableStat({ field, label, suffix = '+', initialValue }: Props) {
  const [value, setValue] = useState(initialValue)
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState(String(initialValue))
  const [error, setError] = useState<string | null>(null)
  const [serverError, setServerError] = useState<string | null>(null)
  const [saveState, setSaveState] = useState<SaveState>('idle')

  function startEdit() {
    setInput(String(value))
    setError(null)
    setServerError(null)
    setOpen(true)
  }

  function closeModal() {
    setOpen(false)
    setServerError(null)
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = editStatValueSchema.safeParse({ value: input })
    if (!result.success) {
      setError(result.error.issues[0]?.message ?? 'Invalid value.')
      return
    }
    setError(null)
    setSaveState('saving')

    try {
      const res = await fetch('/api/admin-hub/site-settings/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'same-origin',
        body: JSON.stringify({ [field]: result.data.value }),
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        return
      }
      const updated: SiteSetting = await res.json()
      setValue(updated[field])
      setSaveState('idle')
      setOpen(false)
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
    }
  }

  return (
    <div className="cc-years-exp">
      <button
        type="button"
        className="cc-years-exp__value"
        onClick={startEdit}
        aria-label={`Edit ${label}`}
      >
        {value}{suffix && <span className="cc-years-exp__suffix">{suffix}</span>}
      </button>
      <p className="cc-years-exp__label">{label}</p>

      <Modal open={open} onClose={closeModal} title={`Edit ${label}`}>
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`site-setting-${field}`}>{label}</label>
            <input
              id={`site-setting-${field}`}
              type="number"
              min={0}
              max={999999}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {error && <p className="form-note">{error}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={saveState === 'saving'}>
              {saveState === 'saving' ? 'Saving…' : 'Save'}
            </button>
            <button type="button" className="btn btn--outline" onClick={closeModal} disabled={saveState === 'saving'}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
