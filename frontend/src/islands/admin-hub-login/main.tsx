import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import AdminHubLoginForm from './AdminHubLoginForm'

const container = document.getElementById('admin-hub-login-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <AdminHubLoginForm />
    </StrictMode>,
  )
}
