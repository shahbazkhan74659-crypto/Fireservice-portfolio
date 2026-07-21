import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ContactForm from './ContactForm'

const container = document.getElementById('contact-form-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <ContactForm />
    </StrictMode>,
  )
}
