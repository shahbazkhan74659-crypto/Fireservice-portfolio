import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import CertificationManager from './CertificationManager'

const container = document.getElementById('admin-certifications-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <CertificationManager />
    </StrictMode>,
  )
}
