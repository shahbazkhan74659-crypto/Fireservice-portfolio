import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ClientLogoManager from './ClientLogoManager'

const container = document.getElementById('admin-client-logos-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <ClientLogoManager />
    </StrictMode>,
  )
}
