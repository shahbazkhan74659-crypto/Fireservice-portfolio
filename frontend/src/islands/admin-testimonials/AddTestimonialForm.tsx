import { useState, type FormEvent } from 'react'
import { addTestimonialSchema, type AddTestimonialInput, type Testimonial } from './schema'
import { useAddForm } from '../../lib/useAddForm'
import Modal from '../../lib/Modal'

const ENDPOINT = '/api/admin-hub/testimonials/'

interface Props {
  onAdded: (item: Testimonial) => void
}

export default function AddTestimonialForm({ onAdded }: Props) {
  const { open, errors, state, serverError, openModal, closeModal, submit } =
    useAddForm<AddTestimonialInput, Testimonial>(addTestimonialSchema, ENDPOINT)
  const [name, setName] = useState('')
  const [company, setCompany] = useState('')
  const [quote, setQuote] = useState('')
  const [rating, setRating] = useState('5')

  function resetFields() {
    setName('')
    setCompany('')
    setQuote('')
    setRating('5')
  }

  function handleClose() {
    resetFields()
    closeModal()
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const created = await submit({ name, company, quote, rating }, (data) => data)
    if (created) {
      onAdded(created)
      resetFields()
    }
  }

  return (
    <>
      <div className="client-logos__admin-actions">
        <button type="button" className="btn btn--primary" onClick={openModal}>+ Add</button>
      </div>

      <Modal open={open} onClose={handleClose} title="Add Testimonial">
        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-testimonial-name">Name</label>
            <input
              id="new-testimonial-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>

          <div className="field">
            <label htmlFor="new-testimonial-company">Company (optional)</label>
            <input
              id="new-testimonial-company"
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.company && <p className="form-note">{errors.company}</p>}
          </div>

          <div className="field">
            <label htmlFor="new-testimonial-quote">Quote</label>
            <textarea
              id="new-testimonial-quote"
              rows={4}
              value={quote}
              onChange={(e) => setQuote(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.quote && <p className="form-note">{errors.quote}</p>}
          </div>

          <div className="field">
            <label htmlFor="new-testimonial-rating">Rating</label>
            <select
              id="new-testimonial-rating"
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              disabled={state === 'submitting'}
            >
              {[5, 4, 3, 2, 1].map((n) => (
                <option key={n} value={n}>{n} star{n === 1 ? '' : 's'}</option>
              ))}
            </select>
            {errors.rating && <p className="form-note">{errors.rating}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Testimonial'}
            </button>
            <button type="button" className="btn btn--outline" onClick={handleClose} disabled={state === 'submitting'}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </>
  )
}
