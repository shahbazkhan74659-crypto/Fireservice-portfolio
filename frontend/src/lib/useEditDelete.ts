import { useState } from 'react'
import { getCsrfToken } from './csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from './api'

export type EditDeleteDialog = 'none' | 'edit' | 'delete'
type SaveState = 'idle' | 'saving' | 'deleting'

interface UseEditDeleteResult<T> {
  dialog: EditDeleteDialog
  saveState: SaveState
  serverError: string | null
  openEdit: () => void
  openDelete: () => void
  closeDialog: () => void
  save: (body: FormData | Record<string, unknown>) => Promise<T | null>
  remove: () => Promise<boolean>
}

/**
 * Shared PATCH (save)/DELETE (remove) fetch logic used by every Admin Hub
 * "Card"/"Row" component. Handles the edit/delete dialog state, in-flight
 * save/delete state, and server/network error messages; each caller keeps
 * its own field state and markup, and passes either a `FormData` (for
 * image-backed entities) or a plain object (for JSON-only entities) to
 * `save()`. Certification's delete-only UI simply never calls
 * `openEdit()`/`save()` — the hook still supports both, so behavior is
 * preserved exactly.
 */
export function useEditDelete<T>(endpoint: string, id: number): UseEditDeleteResult<T> {
  const [dialog, setDialog] = useState<EditDeleteDialog>('none')
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function openEdit() {
    setServerError(null)
    setDialog('edit')
  }

  function openDelete() {
    setServerError(null)
    setDialog('delete')
  }

  function closeDialog() {
    setDialog('none')
    setServerError(null)
  }

  async function save(body: FormData | Record<string, unknown>): Promise<T | null> {
    setServerError(null)
    setSaveState('saving')

    const isFormData = body instanceof FormData
    try {
      const res = await fetch(`${endpoint}${id}/`, {
        method: 'PATCH',
        headers: isFormData
          ? { 'X-CSRFToken': getCsrfToken() }
          : { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: isFormData ? body : JSON.stringify(body),
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        return null
      }
      const updated: T = await res.json()
      setSaveState('idle')
      setDialog('none')
      return updated
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setSaveState('idle')
      return null
    }
  }

  async function remove(): Promise<boolean> {
    setServerError(null)
    setSaveState('deleting')
    try {
      const res = await fetch(`${endpoint}${id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
      })
      if (!res.ok && res.status !== 204) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        return false
      }
      return true
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setSaveState('idle')
      return false
    }
  }

  return { dialog, saveState, serverError, openEdit, openDelete, closeDialog, save, remove }
}
