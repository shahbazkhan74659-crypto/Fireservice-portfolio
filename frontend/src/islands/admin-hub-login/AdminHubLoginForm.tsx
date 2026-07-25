import { useState, type FormEvent, type ChangeEvent } from 'react'
import { adminLoginSchema, type AdminLoginInput, type AdminLoginFormErrors } from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from '../../lib/api'

const initialValues: AdminLoginInput = { username: '', password: '' }

type SubmitState = 'idle' | 'submitting' | 'error'

export default function AdminHubLoginForm() {
  const [values, setValues] = useState<AdminLoginInput>(initialValues)
  const [errors, setErrors] = useState<AdminLoginFormErrors>({})
  const [state, setState] = useState<SubmitState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  const handleChange =
    (field: keyof AdminLoginInput) =>
    (e: ChangeEvent<HTMLInputElement>) =>
      setValues((prev) => ({ ...prev, [field]: e.target.value }))

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = adminLoginSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: AdminLoginFormErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof AdminLoginInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await fetch('/api/admin-hub/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify(result.data),
      })

      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('error')
        return
      }

      // Full navigation (not client-side routing) so the session cookie
      // set by the login view is picked up by the next page's request.
      window.location.href = '/admin-hub/home/'
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('error')
    }
  }

  return (
    <form className="contact__form" onSubmit={handleSubmit} noValidate>
      <h3>Admin Login</h3>

      <div className="field">
        <label htmlFor="username">Username</label>
        <input id="username" type="text" value={values.username} onChange={handleChange('username')} disabled={state === 'submitting'} autoComplete="username" />
        {errors.username && <p className="form-note">{errors.username}</p>}
      </div>

      <div className="field">
        <label htmlFor="password">Password</label>
        <input id="password" type="password" value={values.password} onChange={handleChange('password')} disabled={state === 'submitting'} autoComplete="current-password" />
        {errors.password && <p className="form-note">{errors.password}</p>}
      </div>

      <button type="submit" className="btn btn--primary btn--block" disabled={state === 'submitting'}>
        {state === 'submitting' ? 'Logging in…' : 'Log In'}
      </button>

      {serverError && <p className="form-note">{serverError}</p>}
    </form>
  )
}
