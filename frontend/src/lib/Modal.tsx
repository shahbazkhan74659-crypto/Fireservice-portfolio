import { useEffect, type MouseEvent, type ReactNode } from 'react'
import { createPortal } from 'react-dom'

interface Props {
  open: boolean
  onClose: () => void
  title?: string
  children: ReactNode
}

export default function Modal({ open, onClose, title, children }: Props) {
  useEffect(() => {
    if (!open) return
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [open, onClose])

  // Body-scroll lock while open, so the page behind the full-screen overlay
  // can't be scrolled. Restores whatever inline overflow value was present
  // before (rather than hardcoding '' back) in case something else is ever
  // also managing body overflow.
  useEffect(() => {
    if (!open) return
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previousOverflow
    }
  }, [open])

  if (!open) return null

  function handleOverlayClick(e: MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) onClose()
  }

  // Rendered via portal straight into <body> — a modal nested inside a card
  // with a hover `transform` (e.g. .logo-card:hover) would otherwise have
  // its `position:fixed` confined to that ancestor's box instead of the
  // viewport, since a `transform` on an ancestor creates a new containing
  // block for fixed descendants.
  return createPortal(
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={title}>
        <button type="button" className="modal__close" onClick={onClose} aria-label="Close">&times;</button>
        {title && <h3 className="modal__title">{title}</h3>}
        {children}
      </div>
    </div>,
    document.body,
  )
}
