import { useState, type FormEvent, type ChangeEvent } from 'react'
import { consultationRequestSchema, type ConsultationRequestInput, type ConsultationFormErrors } from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'

const initialValues: ConsultationRequestInput = {
  name: '', phone: '',
}

type SubmitState = 'idle' | 'submitting' | 'success' | 'error'

export default function ConsultationForm() {
  const [values, setValues] = useState<ConsultationRequestInput>(initialValues)
  const [errors, setErrors] = useState<ConsultationFormErrors>({})
  const [state, setState] = useState<SubmitState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  const handleChange =
    (field: keyof ConsultationRequestInput) =>
    (e: ChangeEvent<HTMLInputElement>) =>
      setValues((prev) => ({ ...prev, [field]: e.target.value }))

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = consultationRequestSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: ConsultationFormErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ConsultationRequestInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await fetch('/api/consultation/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify({
          name: result.data.name,
          phone: result.data.phone,
        }),
      })

      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('error')
        return
      }

      setState('success')
      setValues(initialValues)
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setState('error')
    }
  }

  if (state === 'success') {
    return (
      <div className="contact__form">
        <h3>Thank You</h3>
        <p className="form-note form-note--success">
          Thanks! One of our experts will call you back shortly.
        </p>
      </div>
    )
  }

  return (
    <form className="contact__form" onSubmit={handleSubmit} noValidate autoComplete="off">
      <h3>Request a Callback</h3>

      <div className="field">
        <label htmlFor="name">Full Name</label>
        <input id="name" type="text" value={values.name} onChange={handleChange('name')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.name && <p className="form-note">{errors.name}</p>}
      </div>

      <div className="field">
        <label htmlFor="phone">Phone Number</label>
        <input id="phone" type="tel" value={values.phone} onChange={handleChange('phone')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.phone && <p className="form-note">{errors.phone}</p>}
      </div>

      <button type="submit" className="btn btn--primary btn--block" disabled={state === 'submitting'}>
        {state === 'submitting' ? 'Sending…' : 'Request Callback'}
      </button>

      {serverError && <p className="form-note">{serverError}</p>}
    </form>
  )
}
