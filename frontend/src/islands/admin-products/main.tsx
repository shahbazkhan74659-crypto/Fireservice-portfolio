import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ProductManager from './ProductManager'

const container = document.getElementById('admin-products-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <ProductManager />
    </StrictMode>,
  )
}
