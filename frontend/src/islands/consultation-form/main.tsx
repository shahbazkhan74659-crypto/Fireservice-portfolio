import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ConsultationForm from './ConsultationForm'

const container = document.getElementById('consultation-form-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <ConsultationForm />
    </StrictMode>,
  )
}
