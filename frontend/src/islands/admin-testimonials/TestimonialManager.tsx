import AddTestimonialForm from './AddTestimonialForm'
import TestimonialRow from './TestimonialRow'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { Testimonial } from './schema'

const ENDPOINT = '/api/admin-hub/testimonials/'

export default function TestimonialManager() {
  const { items, loadState, add, update, remove } = useCrudList<Testimonial>(ENDPOINT)

  if (loadState === 'loading') {
    return (
      <div aria-hidden="true">
        {Array.from({ length: 3 }).map((_, i) => (
          <div className="admin-mv-point" key={i}>
            <Skeleton className="skeleton-text" style={{ flex: 1, height: 16, marginBottom: 0 }} />
            <Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} />
            <Skeleton style={{ width: 38, height: 38, borderRadius: 10 }} />
          </div>
        ))}
      </div>
    )
  }

  if (loadState === 'error') {
    return <p className="form-note">Couldn&apos;t load testimonials. Reload the page and try again.</p>
  }

  return (
    <>
      <AddTestimonialForm onAdded={add} />
      {items.length === 0 ? (
        <p className="section__sub">No testimonials yet.</p>
      ) : (
        items.map((item) => (
          <TestimonialRow key={item.id} item={item} onUpdated={update} onDeleted={remove} />
        ))
      )}
    </>
  )
}
