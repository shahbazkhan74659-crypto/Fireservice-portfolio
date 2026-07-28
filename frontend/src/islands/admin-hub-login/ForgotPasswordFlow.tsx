import { useState, type FormEvent, type ChangeEvent } from 'react'
import {
  forgotPasswordEmailSchema,
  type ForgotPasswordEmailInput,
  type ForgotPasswordEmailErrors,
  forgotPasswordOtpSchema,
  type ForgotPasswordOtpInput,
  type ForgotPasswordOtpErrors,
  forgotPasswordResetSchema,
  type ForgotPasswordResetInput,
  type ForgotPasswordResetErrors,
  PASSWORD_REQUIREMENTS_HINT,
} from './forgotPasswordSchema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from '../../lib/api'
import Modal from '../../lib/Modal'

type Step = 'email' | 'otp' | 'reset'
type SubmitState = 'idle' | 'submitting'

const initialEmail: ForgotPasswordEmailInput = { email: '' }
const initialOtp: ForgotPasswordOtpInput = { otp: '' }
const initialReset: ForgotPasswordResetInput = { new_password: '', confirm_password: '' }

async function postJson(url: string, body: unknown) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
    credentials: 'same-origin',
    body: JSON.stringify(body),
  })
}

interface Props {
  /** True when the login form's own Username field is empty — the trigger
   * button stays disabled until the admin has typed a username, per an
   * explicit UI-gate requirement (the username itself isn't sent to the
   * server as part of the reset flow, only the email is). */
  disabled: boolean
}

export default function ForgotPasswordFlow({ disabled }: Props) {
  const [open, setOpen] = useState(false)
  const [step, setStep] = useState<Step>('email')
  const [email, setEmail] = useState('')
  const [resetToken, setResetToken] = useState('')

  const [emailValues, setEmailValues] = useState(initialEmail)
  const [emailErrors, setEmailErrors] = useState<ForgotPasswordEmailErrors>({})
  const [otpValues, setOtpValues] = useState(initialOtp)
  const [otpErrors, setOtpErrors] = useState<ForgotPasswordOtpErrors>({})
  const [resetValues, setResetValues] = useState(initialReset)
  const [resetErrors, setResetErrors] = useState<ForgotPasswordResetErrors>({})

  const [state, setState] = useState<SubmitState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)
  const [serverNotice, setServerNotice] = useState<string | null>(null)

  function resetAll() {
    setStep('email')
    setEmail('')
    setResetToken('')
    setEmailValues(initialEmail)
    setEmailErrors({})
    setOtpValues(initialOtp)
    setOtpErrors({})
    setResetValues(initialReset)
    setResetErrors({})
    setState('idle')
    setServerError(null)
    setServerNotice(null)
  }

  function handleClose() {
    setOpen(false)
    resetAll()
  }

  async function handleEmailSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = forgotPasswordEmailSchema.safeParse(emailValues)
    if (!result.success) {
      const fieldErrors: ForgotPasswordEmailErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ForgotPasswordEmailInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setEmailErrors(fieldErrors)
      return
    }
    setEmailErrors({})
    setState('submitting')

    try {
      const res = await postJson('/api/admin-hub/forgot-password/request-otp/', { email: result.data.email })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }
      setEmail(result.data.email)
      setState('idle')
      setStep('otp')
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  async function handleResendOtp() {
    setServerError(null)
    setServerNotice(null)
    setState('submitting')

    try {
      const res = await postJson('/api/admin-hub/forgot-password/request-otp/', { email })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }
      setServerNotice('A new code has been sent.')
      setState('idle')
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  async function handleOtpSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)
    setServerNotice(null)

    const result = forgotPasswordOtpSchema.safeParse(otpValues)
    if (!result.success) {
      const fieldErrors: ForgotPasswordOtpErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ForgotPasswordOtpInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setOtpErrors(fieldErrors)
      return
    }
    setOtpErrors({})
    setState('submitting')

    try {
      const res = await postJson('/api/admin-hub/forgot-password/verify-otp/', { email, otp: result.data.otp })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }
      const data: { reset_token: string } = await res.json()
      setResetToken(data.reset_token)
      setState('idle')
      setStep('reset')
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  async function handleResetSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = forgotPasswordResetSchema.safeParse(resetValues)
    if (!result.success) {
      const fieldErrors: ForgotPasswordResetErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ForgotPasswordResetInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setResetErrors(fieldErrors)
      return
    }
    setResetErrors({})
    setState('submitting')

    try {
      const res = await postJson('/api/admin-hub/forgot-password/reset/', {
        reset_token: resetToken,
        new_password: result.data.new_password,
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }
      // Full navigation back to the login page — same "reload over
      // client-side sync" convention the login/username forms already use,
      // and matches the agreed spec's "redirect back to Admin Hub login".
      window.location.href = '/admin-hub/'
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  return (
    <>
      <button
        type="button"
        className="btn btn--outline-red btn--block"
        onClick={() => setOpen(true)}
        disabled={disabled}
        title={disabled ? 'Enter your username first.' : undefined}
      >
        Forgot Password?
      </button>

      <Modal open={open} onClose={handleClose} title="Reset Your Password" className="modal--lead">
        {step === 'email' && (
          <form onSubmit={handleEmailSubmit} noValidate>
            <p className="modal__body">
              Enter the email address registered to your Admin Hub account. We&rsquo;ll send a
              one-time verification code to that address to confirm it&rsquo;s really you.
            </p>
            <div className="field">
              <label htmlFor="forgot_email">Email</label>
              <input
                id="forgot_email"
                type="email"
                value={emailValues.email}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setEmailValues({ email: e.target.value })}
                disabled={state === 'submitting'}
                autoComplete="email"
              />
              {emailErrors.email && <p className="form-note">{emailErrors.email}</p>}
            </div>
            {serverError && <p className="form-note">{serverError}</p>}
            <button type="submit" className="btn btn--primary btn--block" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Sending…' : 'Send Code'}
            </button>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={handleOtpSubmit} noValidate>
            <p className="modal__body">
              Enter the 6-digit code sent to <strong>{email}</strong>. It expires in 5 minutes.
            </p>
            <div className="field">
              <label htmlFor="forgot_otp">Verification Code</label>
              <input
                id="forgot_otp"
                type="text"
                inputMode="numeric"
                maxLength={6}
                value={otpValues.otp}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setOtpValues({ otp: e.target.value })}
                disabled={state === 'submitting'}
                autoComplete="one-time-code"
              />
              {otpErrors.otp && <p className="form-note">{otpErrors.otp}</p>}
            </div>
            {serverNotice && <p className="form-note form-note--success">{serverNotice}</p>}
            {serverError && <p className="form-note">{serverError}</p>}
            <button type="submit" className="btn btn--primary btn--block" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Verifying…' : 'Verify Code'}
            </button>
            <p className="auth-card__forgot">
              <button type="button" className="btn--link" onClick={handleResendOtp} disabled={state === 'submitting'}>
                Resend Code
              </button>
            </p>
          </form>
        )}

        {step === 'reset' && (
          <form onSubmit={handleResetSubmit} noValidate>
            <p className="modal__body">Choose a new password for your account.</p>
            <div className="field">
              <label htmlFor="forgot_new_password">New Password</label>
              <input
                id="forgot_new_password"
                type="password"
                value={resetValues.new_password}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setResetValues((prev) => ({ ...prev, new_password: e.target.value }))
                }
                disabled={state === 'submitting'}
                autoComplete="new-password"
              />
              <p className="field__hint">{PASSWORD_REQUIREMENTS_HINT}</p>
              {resetErrors.new_password && <p className="form-note">{resetErrors.new_password}</p>}
            </div>
            <div className="field">
              <label htmlFor="forgot_confirm_password">Confirm New Password</label>
              <input
                id="forgot_confirm_password"
                type="password"
                value={resetValues.confirm_password}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setResetValues((prev) => ({ ...prev, confirm_password: e.target.value }))
                }
                disabled={state === 'submitting'}
                autoComplete="new-password"
              />
              {resetErrors.confirm_password && <p className="form-note">{resetErrors.confirm_password}</p>}
            </div>
            {serverError && <p className="form-note">{serverError}</p>}
            <button type="submit" className="btn btn--primary btn--block" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Saving…' : 'Reset Password'}
            </button>
          </form>
        )}
      </Modal>
    </>
  )
}
