import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import FeedbackWidget from './FeedbackWidget'

const container = document.getElementById('feedback-widget-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <FeedbackWidget />
    </StrictMode>,
  )
}
