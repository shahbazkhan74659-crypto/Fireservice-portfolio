import { consultationRequestSchema, type ConsultationRequestInput } from './schema'
import { useFormSubmit } from '../../lib/useFormSubmit'

const initialValues: ConsultationRequestInput = {
  name: '', phone: '',
}

const ENDPOINT = '/api/consultation/'

export default function ConsultationForm() {
  const { values, errors, state, serverError, handleChange, handleSubmit } = useFormSubmit(
    consultationRequestSchema,
    ENDPOINT,
    initialValues,
    (data) => ({
      name: data.name,
      phone: data.phone,
    }),
  )

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
