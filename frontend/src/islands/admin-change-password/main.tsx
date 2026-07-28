import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import AccountSettingsButton from './AccountSettingsButton'

// Mounted twice on the page (desktop header actions + drawer footer, same
// pattern as the username/Log Out duplication in adminhub/base.html) — only
// one is visible at a time depending on viewport width. Loop-mounting into
// every match follows the same precedent as admin-site-settings' EditableStat.
document.querySelectorAll<HTMLElement>('[data-change-password-root]').forEach((container) => {
  createRoot(container).render(
    <StrictMode>
      <AccountSettingsButton />
    </StrictMode>,
  )
})
