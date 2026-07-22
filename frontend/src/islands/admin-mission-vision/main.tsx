import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import MissionVisionManager from './MissionVisionManager'

const container = document.getElementById('admin-mission-vision-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <MissionVisionManager />
    </StrictMode>,
  )
}
