import { surveyRequestSchema, type SurveyRequestInput } from './schema'
import { useFormSubmit } from '../../lib/useFormSubmit'

const initialValues: SurveyRequestInput = {
  name: '', email: '', address: '', problem: '', whySurvey: '',
}

const ENDPOINT = '/api/survey/'

export default function SurveyForm() {
  const { values, errors, state, serverError, handleChange, handleSubmit } = useFormSubmit(
    surveyRequestSchema,
    ENDPOINT,
    initialValues,
    (data) => ({
      name: data.name,
      email: data.email,
      address: data.address,
      problem: data.problem,
      why_survey: data.whySurvey,
    }),
  )

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
