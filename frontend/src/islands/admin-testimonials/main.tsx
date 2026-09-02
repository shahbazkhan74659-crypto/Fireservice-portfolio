import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import TestimonialManager from './TestimonialManager'

const container = document.getElementById('admin-testimonials-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <TestimonialManager />
    </StrictMode>,
  )
}
