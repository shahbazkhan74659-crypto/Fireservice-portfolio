import { useEffect, useState } from 'react'
import FeedbackForm from './FeedbackForm'
import Modal from '../../lib/Modal'
import type { Testimonial } from './schema'

const ENDPOINT = '/api/testimonials/'

function renderStars(rating: number) {
  return '★'.repeat(rating) + '☆'.repeat(5 - rating)
}

export default function FeedbackWidget() {
  const [open, setOpen] = useState(false)
  const [testimonials, setTestimonials] = useState<Testimonial[]>([])

  useEffect(() => {
    let cancelled = false
    fetch(ENDPOINT, { credentials: 'same-origin' })
      .then((res) => (res.ok ? res.json() : []))
      .then((data: Testimonial[]) => {
        if (!cancelled) setTestimonials(data)
      })
      .catch(() => {
        // Silently ignore — the widget still works for submitting new
        // feedback even if the existing-testimonials list fails to load.
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <>
      <button type="button" className="feedback-widget__toggle" onClick={() => setOpen(true)}>
        Share Your Experience
      </button>

      <Modal open={open} onClose={() => setOpen(false)} title="Share Your Experience" className="modal--feedback">
        {testimonials.length > 0 && (
          <div className="feedback-widget__list">
            {testimonials.map((item) => (
              <div className="feedback-widget__item" key={item.id}>
                <p className="feedback-widget__stars">{renderStars(item.rating)}</p>
                <p className="feedback-widget__quote">&ldquo;{item.quote}&rdquo;</p>
                <p className="feedback-widget__name">
                  {item.name}{item.company && ` — ${item.company}`}
                </p>
              </div>
            ))}
          </div>
        )}

        <FeedbackForm />
      </Modal>
    </>
  )
}
