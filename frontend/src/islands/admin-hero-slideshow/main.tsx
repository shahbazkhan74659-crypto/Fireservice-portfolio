import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import HeroSlideshowButton from './HeroSlideshowButton'

const container = document.querySelector<HTMLElement>('[data-hero-slideshow-root]')
if (container) {
  const initialDuration = Number(container.dataset.duration) || 5

  createRoot(container).render(
    <StrictMode>
      <HeroSlideshowButton initialDuration={initialDuration} />
    </StrictMode>,
  )
}
