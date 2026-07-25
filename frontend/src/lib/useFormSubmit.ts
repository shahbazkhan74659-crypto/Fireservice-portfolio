import { useState, type ChangeEvent, type FormEvent } from 'react'
import type { ZodType } from 'zod'
import { getCsrfToken } from './csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from './api'

type SubmitState = 'idle' | 'submitting' | 'success' | 'error'

type FieldChangeEvent = ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>

interface UseFormSubmitResult<TValues> {
  values: TValues
  setValues: (updater: TValues | ((prev: TValues) => TValues)) => void
  errors: Partial<Record<keyof TValues, string>>
  state: SubmitState
  serverError: string | null
  handleChange: (field: keyof TValues) => (e: FieldChangeEvent) => void
  handleSubmit: (e: FormEvent<HTMLFormElement>) => Promise<void>
}

/**
 * Shared idle|submitting|success|error state machine used by the three
 * public lead-capture forms (Survey, Contact, Consultation): Zod-validate
 * the current values, POST the mapped body as JSON, and track
 * field/server/network errors. Each island keeps its own field set,
 * `initialValues`, and success/error markup — this hook only owns the
 * validate-then-submit plumbing that was previously hand-copied into all
 * three `handleSubmit` functions.
 */
export function useFormSubmit<TValues extends Record<string, unknown>>(
  schema: ZodType<TValues>,
  endpoint: string,
  initialValues: TValues,
  buildBody: (data: TValues) => Record<string, unknown>,
): UseFormSubmitResult<TValues> {
  const [values, setValues] = useState<TValues>(initialValues)
  const [errors, setErrors] = useState<Partial<Record<keyof TValues, string>>>({})
  const [state, setState] = useState<SubmitState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  const handleChange =
    (field: keyof TValues) =>
    (e: FieldChangeEvent) =>
      setValues((prev) => ({ ...prev, [field]: e.target.value }))

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = schema.safeParse(values)
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof TValues, string>> = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof TValues
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify(buildBody(result.data)),
      })

      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('error')
        return
      }

      setState('success')
      setValues(initialValues)
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('error')
    }
  }

  return { values, setValues, errors, state, serverError, handleChange, handleSubmit }
}
