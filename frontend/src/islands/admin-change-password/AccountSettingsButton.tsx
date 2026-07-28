import { useState, type FormEvent, type ChangeEvent } from 'react'
import {
  changeUsernameSchema,
  type ChangeUsernameInput,
  type ChangeUsernameErrors,
  changePasswordSchema,
  type ChangePasswordInput,
  type ChangePasswordErrors,
  PASSWORD_REQUIREMENTS_HINT,
} from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from '../../lib/api'
import Modal from '../../lib/Modal'

const initialUsername: ChangeUsernameInput = { new_username: '', confirm_username: '' }
const initialPassword: ChangePasswordInput = { old_password: '', new_password: '', confirm_password: '' }

type SectionState = 'idle' | 'submitting'

function UsernameSection() {
  const [values, setValues] = useState<ChangeUsernameInput>(initialUsername)
  const [errors, setErrors] = useState<ChangeUsernameErrors>({})
  const [serverError, setServerError] = useState<string | null>(null)
  const [state, setState] = useState<SectionState>('idle')

  const handleChange =
    (field: keyof ChangeUsernameInput) =>
    (e: ChangeEvent<HTMLInputElement>) =>
      setValues((prev) => ({ ...prev, [field]: e.target.value }))

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = changeUsernameSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: ChangeUsernameErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ChangeUsernameInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await fetch('/api/admin-hub/change-username/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify({ new_username: result.data.new_username }),
      })

      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }

      // The header's username display is server-rendered, not part of this
      // React tree — a full reload is the simplest way to reflect the new
      // name everywhere it appears, same "full navigation over cross-
      // component sync" choice already used by the login form on success.
      window.location.reload()
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h4>Change Username</h4>
      <div className="field">
        <label htmlFor="new_username">New Username</label>
        <input
          id="new_username"
          type="text"
          value={values.new_username}
          onChange={handleChange('new_username')}
          disabled={state === 'submitting'}
          autoComplete="username"
        />
        {errors.new_username && <p className="form-note">{errors.new_username}</p>}
      </div>

      <div className="field">
        <label htmlFor="confirm_username">Confirm New Username</label>
        <input
          id="confirm_username"
          type="text"
          value={values.confirm_username}
          onChange={handleChange('confirm_username')}
          disabled={state === 'submitting'}
          autoComplete="username"
        />
        {errors.confirm_username && <p className="form-note">{errors.confirm_username}</p>}
      </div>

      {serverError && <p className="form-note">{serverError}</p>}

      <div className="logo-card__admin-actions">
        <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
          {state === 'submitting' ? 'Saving…' : 'Save Username'}
        </button>
      </div>
    </form>
  )
}

function PasswordSection() {
  const [values, setValues] = useState<ChangePasswordInput>(initialPassword)
  const [errors, setErrors] = useState<ChangePasswordErrors>({})
  const [serverError, setServerError] = useState<string | null>(null)
  const [state, setState] = useState<SectionState | 'success'>('idle')

  const handleChange =
    (field: keyof ChangePasswordInput) =>
    (e: ChangeEvent<HTMLInputElement>) =>
      setValues((prev) => ({ ...prev, [field]: e.target.value }))

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = changePasswordSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: ChangePasswordErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ChangePasswordInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await fetch('/api/admin-hub/change-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify({
          old_password: result.data.old_password,
          new_password: result.data.new_password,
        }),
      })

      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }

      setValues(initialPassword)
      setState('success')
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  if (state === 'success') {
    return (
      <>
        <h4>Change Password</h4>
        <p className="form-note">Password changed successfully. Use it next time you log in.</p>
        <div className="logo-card__admin-actions">
          <button type="button" className="btn btn--outline" onClick={() => setState('idle')}>Change Again</button>
        </div>
      </>
    )
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h4>Change Password</h4>
      <div className="field">
        <label htmlFor="old_password">Current Password</label>
        <input
          id="old_password"
          type="password"
          value={values.old_password}
          onChange={handleChange('old_password')}
          disabled={state === 'submitting'}
          autoComplete="current-password"
        />
        {errors.old_password && <p className="form-note">{errors.old_password}</p>}
      </div>

      <div className="field">
        <label htmlFor="new_password">New Password</label>
        <input
          id="new_password"
          type="password"
          value={values.new_password}
          onChange={handleChange('new_password')}
          disabled={state === 'submitting'}
          autoComplete="new-password"
        />
        <p className="field__hint">{PASSWORD_REQUIREMENTS_HINT}</p>
        {errors.new_password && <p className="form-note">{errors.new_password}</p>}
      </div>

      <div className="field">
        <label htmlFor="confirm_password">Confirm New Password</label>
        <input
          id="confirm_password"
          type="password"
          value={values.confirm_password}
          onChange={handleChange('confirm_password')}
          disabled={state === 'submitting'}
          autoComplete="new-password"
        />
        {errors.confirm_password && <p className="form-note">{errors.confirm_password}</p>}
      </div>

      {serverError && <p className="form-note">{serverError}</p>}

      <div className="logo-card__admin-actions">
        <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
          {state === 'submitting' ? 'Saving…' : 'Save New Password'}
        </button>
      </div>
    </form>
  )
}

export default function AccountSettingsButton() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button type="button" className="btn btn--outline" onClick={() => setOpen(true)}>
        Account Settings
      </button>

      <Modal open={open} onClose={() => setOpen(false)} title="Account Settings">
        <UsernameSection />
        <hr className="admin-modal-divider" />
        <PasswordSection />
      </Modal>
    </>
  )
}
