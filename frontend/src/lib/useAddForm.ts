import { useState } from 'react'
import type { ZodType } from 'zod'
import { getCsrfToken } from './csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from './api'

type SubmitState = 'idle' | 'submitting'

interface UseAddFormResult<TInput, TCreated> {
  open: boolean
  errors: Partial<Record<keyof TInput, string>>
  state: SubmitState
  serverError: string | null
  openModal: () => void
  closeModal: () => void
  submit: (values: unknown, buildBody: (data: TInput) => FormData | Record<string, unknown>) => Promise<TCreated | null>
}

/**
 * Shared Zod-validate-then-POST logic used by every Admin Hub "AddXForm"
 * component. Field state and markup stay in each caller; this hook owns the
 * open/errors/submitting/server-error state and the fetch itself. Callers
 * provide a `buildBody` function so image-backed entities can submit
 * `FormData` while text-only entities (Fire Risk Items, Mission & Vision)
 * submit plain JSON — the hook picks the right `Content-Type`/body shape
 * based on what's returned.
 */
export function useAddForm<TInput extends Record<string, unknown>, TCreated>(
  schema: ZodType<TInput>,
  endpoint: string,
): UseAddFormResult<TInput, TCreated> {
  type TErrors = Partial<Record<keyof TInput, string>>
  const [open, setOpen] = useState(false)
  const [errors, setErrors] = useState<TErrors>({})
  const [state, setState] = useState<SubmitState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function openModal() {
    setErrors({})
    setServerError(null)
    setOpen(true)
  }

  function closeModal() {
    setErrors({})
    setServerError(null)
    setOpen(false)
  }

  async function submit(
    values: unknown,
    buildBody: (data: TInput) => FormData | Record<string, unknown>,
  ): Promise<TCreated | null> {
    setServerError(null)

    const result = schema.safeParse(values)
    if (!result.success) {
      const fieldErrors: TErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof TInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return null
    }
    setErrors({})
    setState('submitting')

    const body = buildBody(result.data)
    const isFormData = body instanceof FormData

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: isFormData
          ? { 'X-CSRFToken': getCsrfToken() }
          : { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: isFormData ? body : JSON.stringify(body),
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return null
      }
      const created: TCreated = await res.json()
      setState('idle')
      setOpen(false)
      return created
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
      return null
    }
  }

  return { open, errors, state, serverError, openModal, closeModal, submit }
}
