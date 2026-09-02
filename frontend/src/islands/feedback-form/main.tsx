import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import FeedbackForm from './FeedbackForm'

const container = document.getElementById('feedback-form-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <FeedbackForm />
    </StrictMode>,
  )
}
