import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ProcessPhaseManager from './ProcessPhaseManager'

const container = document.getElementById('admin-process-phases-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <ProcessPhaseManager />
    </StrictMode>,
  )
}
