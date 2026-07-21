import { useState, type FormEvent, type ChangeEvent } from 'react'
import { surveyRequestSchema, type SurveyRequestInput, type SurveyFormErrors } from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'

const initialValues: SurveyRequestInput = {
  name: '', email: '', address: '', problem: '', whySurvey: '',
}

type SubmitState = 'idle' | 'submitting' | 'success' | 'error'

export default function SurveyForm() {
  const [values, setValues] = useState<SurveyRequestInput>(initialValues)
  const [errors, setErrors] = useState<SurveyFormErrors>({})
  const [state, setState] = useState<SubmitState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  const handleChange =
    (field: keyof SurveyRequestInput) =>
    (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setValues((prev) => ({ ...prev, [field]: e.target.value }))

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = surveyRequestSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: SurveyFormErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof SurveyRequestInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await fetch('/api/survey/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify({
          name: result.data.name,
          email: result.data.email,
          address: result.data.address,
          problem: result.data.problem,
          why_survey: result.data.whySurvey,
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
          Your survey request has been received. Our team will contact you within one business day.
        </p>
      </div>
    )
  }

  return (
    <form className="contact__form" onSubmit={handleSubmit} noValidate autoComplete="off">
      <h3>Request Your Free Survey</h3>

      <div className="form-row">
        <div className="field">
          <label htmlFor="name">Full Name</label>
          <input id="name" type="text" value={values.name} onChange={handleChange('name')} disabled={state === 'submitting'} autoComplete="off" />
          {errors.name && <p className="form-note">{errors.name}</p>}
        </div>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={values.email} onChange={handleChange('email')} disabled={state === 'submitting'} autoComplete="off" />
          {errors.email && <p className="form-note">{errors.email}</p>}
        </div>
      </div>

      <div className="field">
        <label htmlFor="address">Address</label>
        <textarea id="address" rows={2} value={values.address} onChange={handleChange('address')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.address && <p className="form-note">{errors.address}</p>}
      </div>

      <div className="field">
        <label htmlFor="problem">What's the Problem?</label>
        <textarea id="problem" rows={4} value={values.problem} onChange={handleChange('problem')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.problem && <p className="form-note">{errors.problem}</p>}
      </div>

      <div className="field">
        <label htmlFor="whySurvey">Why Should We Survey?</label>
        <textarea id="whySurvey" rows={4} value={values.whySurvey} onChange={handleChange('whySurvey')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.whySurvey && <p className="form-note">{errors.whySurvey}</p>}
      </div>

      <button type="submit" className="btn btn--primary btn--block" disabled={state === 'submitting'}>
        {state === 'submitting' ? 'Submitting…' : 'Submit Request'}
      </button>

      {serverError && <p className="form-note">{serverError}</p>}
    </form>
  )
}
