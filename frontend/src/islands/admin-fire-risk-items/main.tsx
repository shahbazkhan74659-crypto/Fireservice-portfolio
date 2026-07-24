import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import FireRiskItemManager from './FireRiskItemManager'

const container = document.getElementById('admin-fire-risk-items-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <FireRiskItemManager />
    </StrictMode>,
  )
}
