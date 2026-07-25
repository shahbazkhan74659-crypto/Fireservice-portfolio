import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import EditableStat from './EditableStat'
import type { SiteSettingField } from './schema'

document.querySelectorAll<HTMLElement>('[data-stat-editor]').forEach((container) => {
  const field = container.dataset.field as SiteSettingField
  const label = container.dataset.label ?? ''
  const suffix = container.dataset.suffix ?? '+'
  const initialValue = Number(container.dataset.value) || 0

  createRoot(container).render(
    <StrictMode>
      <EditableStat field={field} label={label} suffix={suffix} initialValue={initialValue} />
    </StrictMode>,
  )
})
