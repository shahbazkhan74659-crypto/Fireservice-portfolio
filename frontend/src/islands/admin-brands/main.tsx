import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import BrandManager from './BrandManager'

const container = document.getElementById('admin-brands-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <BrandManager />
    </StrictMode>,
  )
}
