import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import BrochureButton from './BrochureButton'

const container = document.querySelector<HTMLElement>('[data-brochure-root]')
if (container) {
  const initialBrochure = {
    pdf: container.dataset.pdf ?? '',
    image: container.dataset.image ?? '',
  }

  createRoot(container).render(
    <StrictMode>
      <BrochureButton initialBrochure={initialBrochure} />
    </StrictMode>,
  )
}
