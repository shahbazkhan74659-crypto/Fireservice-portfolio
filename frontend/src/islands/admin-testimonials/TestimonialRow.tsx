import { useState, type FormEvent } from 'react'
import {
  editTestimonialSchema,
  type Testimonial,
  type EditTestimonialInput,
  type EditTestimonialErrors,
} from './schema'
import { useEditDelete } from '../../lib/useEditDelete'
import Modal from '../../lib/Modal'
import { DeleteIcon, EditIcon } from '../../lib/Icons'

const ENDPOINT = '/api/admin-hub/testimonials/'

interface Props {
  item: Testimonial
  onUpdated: (item: Testimonial) => void
  onDeleted: (id: number) => void
}

export default function TestimonialRow({ item, onUpdated, onDeleted }: Props) {
  const { dialog, saveState, serverError, openEdit, openDelete, closeDialog, save, remove } =
    useEditDelete<Testimonial>(ENDPOINT, item.id)
  const [name, setName] = useState(item.name)
  const [company, setCompany] = useState(item.company)
  const [quote, setQuote] = useState(item.quote)
  const [rating, setRating] = useState(String(item.rating))
  const [errors, setErrors] = useState<EditTestimonialErrors>({})

  function startEdit() {
    setName(item.name)
    setCompany(item.company)
    setQuote(item.quote)
    setRating(String(item.rating))
    setErrors({})
    openEdit()
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const result = editTestimonialSchema.safeParse({ name, company, quote, rating })
    if (!result.success) {
      const fieldErrors: EditTestimonialErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof EditTestimonialInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})

    const updated = await save(result.data)
    if (updated) onUpdated(updated)
  }

  async function handleDelete() {
    if (await remove()) onDeleted(item.id)
  }

  return (
    <div className="admin-mv-point">
      <span className="admin-mv-point__text">
        {item.name}{item.company && ` — ${item.company}`} ({item.rating}★)
      </span>

      <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
        <EditIcon />
      </button>
      <button type="button" className="btn btn--primary btn--icon" onClick={openDelete} aria-label="Delete">
        <DeleteIcon />
      </button>

      <Modal open={dialog === 'edit'} onClose={closeDialog} title="Edit Testimonial">
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`testimonial-name-${item.id}`}>Name</label>
            <input
              id={`testimonial-name-${item.id}`}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>

          <div className="field">
            <label htmlFor={`testimonial-company-${item.id}`}>Company (optional)</label>
            <input
              id={`testimonial-company-${item.id}`}
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.company && <p className="form-note">{errors.company}</p>}
          </div>

          <div className="field">
            <label htmlFor={`testimonial-quote-${item.id}`}>Quote</label>
            <textarea
              id={`testimonial-quote-${item.id}`}
              rows={4}
              value={quote}
              onChange={(e) => setQuote(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.quote && <p className="form-note">{errors.quote}</p>}
          </div>

          <div className="field">
            <label htmlFor={`testimonial-rating-${item.id}`}>Rating</label>
            <select
              id={`testimonial-rating-${item.id}`}
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              disabled={saveState === 'saving'}
            >
              {[5, 4, 3, 2, 1].map((n) => (
                <option key={n} value={n}>{n} star{n === 1 ? '' : 's'}</option>
              ))}
            </select>
            {errors.rating && <p className="form-note">{errors.rating}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={saveState === 'saving'}>
              {saveState === 'saving' ? 'Saving…' : 'Save'}
            </button>
            <button type="button" className="btn btn--outline" onClick={closeDialog} disabled={saveState === 'saving'}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Testimonial">
        <p className="modal__body">Delete the testimonial from &quot;{item.name}&quot;? This can&apos;t be undone.</p>

        {serverError && <p className="form-note">{serverError}</p>}

        <div className="logo-card__admin-actions">
          <button type="button" className="btn btn--primary" onClick={handleDelete} disabled={saveState === 'deleting'}>
            {saveState === 'deleting' ? 'Deleting…' : 'Yes, Delete'}
          </button>
          <button type="button" className="btn btn--outline" onClick={closeDialog} disabled={saveState === 'deleting'}>
            Cancel
          </button>
        </div>
      </Modal>
    </div>
  )
}
