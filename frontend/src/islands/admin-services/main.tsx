import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ServiceManager from './ServiceManager'

const container = document.getElementById('admin-services-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <ServiceManager />
    </StrictMode>,
  )
}
