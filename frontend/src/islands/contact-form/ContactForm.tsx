import { contactMessageSchema, SERVICE_OPTIONS, type ContactMessageInput } from './schema'
import { useFormSubmit } from '../../lib/useFormSubmit'

const initialValues: ContactMessageInput = {
  name: '', phone: '', email: '', service: SERVICE_OPTIONS[0].value, message: '',
}

const ENDPOINT = '/api/contact/'

export default function ContactForm() {
  const { values, errors, state, serverError, handleChange, handleSubmit } = useFormSubmit(
    contactMessageSchema,
    ENDPOINT,
    initialValues,
    (data) => ({
      name: data.name,
      phone: data.phone,
      email: data.email,
      service: data.service,
      message: data.message ?? '',
    }),
  )

  if (state === 'success') {
    return (
      <div className="contact__form">
        <h3>Thank You</h3>
        <p className="form-note form-note--success">
          Your message has been received. Our team will reach to you in One Business Day
        </p>
      </div>
    )
  }

  return (
    <form className="contact__form" onSubmit={handleSubmit} noValidate autoComplete="off">
      <h3>Send an Enquiry</h3>

      <div className="form-row">
        <div className="field">
          <label htmlFor="name">Full Name</label>
          <input id="name" type="text" value={values.name} onChange={handleChange('name')} disabled={state === 'submitting'} autoComplete="off" />
          {errors.name && <p className="form-note">{errors.name}</p>}
        </div>
        <div className="field">
          <label htmlFor="phone">Phone</label>
          <input id="phone" type="tel" value={values.phone} onChange={handleChange('phone')} disabled={state === 'submitting'} autoComplete="off" />
          {errors.phone && <p className="form-note">{errors.phone}</p>}
        </div>
      </div>

      <div className="field">
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={values.email} onChange={handleChange('email')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.email && <p className="form-note">{errors.email}</p>}
      </div>

      <div className="field">
        <label htmlFor="service">Service Required</label>
        <select id="service" value={values.service} onChange={handleChange('service')} disabled={state === 'submitting'}>
          {SERVICE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        {errors.service && <p className="form-note">{errors.service}</p>}
      </div>

      <div className="field">
        <label htmlFor="message">Message</label>
        <textarea id="message" rows={4} value={values.message} onChange={handleChange('message')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.message && <p className="form-note">{errors.message}</p>}
      </div>

      <button type="submit" className="btn btn--primary btn--block" disabled={state === 'submitting'}>
        {state === 'submitting' ? 'Submitting…' : 'Submit Enquiry'}
      </button>

      {serverError && <p className="form-note">{serverError}</p>}
    </form>
  )
}
