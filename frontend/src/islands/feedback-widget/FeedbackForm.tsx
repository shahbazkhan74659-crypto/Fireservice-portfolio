import { feedbackSchema, type FeedbackInput } from './schema'
import { useFormSubmit } from '../../lib/useFormSubmit'

const ENDPOINT = '/api/testimonials/'

const initialValues: FeedbackInput = {
  name: '', company: '', quote: '', rating: 5,
}

export default function FeedbackForm() {
  const { values, setValues, errors, state, serverError, handleChange, handleSubmit } = useFormSubmit(
    feedbackSchema,
    ENDPOINT,
    initialValues,
    (data) => ({
      name: data.name,
      company: data.company,
      quote: data.quote,
      rating: data.rating,
    }),
  )

  if (state === 'success') {
    return (
      <div className="feedback-widget__success">
        <h4>Thank You</h4>
        <p className="form-note form-note--success">
          Thanks for sharing your experience! It&apos;s pending our review and will appear here once approved.
        </p>
      </div>
    )
  }

  return (
    <form className="feedback-widget__form" onSubmit={handleSubmit} noValidate autoComplete="off">
      <h4>Share Your Experience</h4>

      <div className="field">
        <label htmlFor="feedback-name">Your Name</label>
        <input id="feedback-name" type="text" value={values.name} onChange={handleChange('name')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.name && <p className="form-note">{errors.name}</p>}
      </div>

      <div className="field">
        <label htmlFor="feedback-company">Company (optional)</label>
        <input id="feedback-company" type="text" value={values.company} onChange={handleChange('company')} disabled={state === 'submitting'} autoComplete="off" />
        {errors.company && <p className="form-note">{errors.company}</p>}
      </div>

      <div className="field">
        <label htmlFor="feedback-quote">Your Feedback</label>
        <textarea id="feedback-quote" rows={3} value={values.quote} onChange={handleChange('quote')} disabled={state === 'submitting'} />
        {errors.quote && <p className="form-note">{errors.quote}</p>}
      </div>

      <div className="field">
        <label>Rating</label>
        <div className="feedback-widget__star-input" role="radiogroup" aria-label="Rating">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              role="radio"
              aria-checked={values.rating === n}
              aria-label={`${n} star${n === 1 ? '' : 's'}`}
              className={n <= values.rating ? 'is-filled' : ''}
              onClick={() => setValues((prev) => ({ ...prev, rating: n }))}
              disabled={state === 'submitting'}
            >
              ★
            </button>
          ))}
        </div>
        {errors.rating && <p className="form-note">{errors.rating}</p>}
      </div>

      {serverError && <p className="form-note">{serverError}</p>}

      <button type="submit" className="btn btn--primary btn--block" disabled={state === 'submitting'}>
        {state === 'submitting' ? 'Sending…' : 'Submit Feedback'}
      </button>
    </form>
  )
}
