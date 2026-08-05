import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import BlogManager from './BlogManager'

const container = document.getElementById('admin-blog-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <BlogManager />
    </StrictMode>,
  )
}
