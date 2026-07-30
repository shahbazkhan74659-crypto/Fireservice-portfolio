import { useRef, useState, type FormEvent, type ChangeEvent } from 'react'
import {
  changeUsernameSchema,
  type ChangeUsernameInput,
  type ChangeUsernameErrors,
  changePasswordSchema,
  type ChangePasswordInput,
  type ChangePasswordErrors,
  changeEmailRequestSchema,
  type ChangeEmailRequestInput,
  type ChangeEmailRequestErrors,
  changeEmailOtpSchema,
  type ChangeEmailOtpInput,
  type ChangeEmailOtpErrors,
  PASSWORD_REQUIREMENTS_HINT,
} from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from '../../lib/api'
import Modal from '../../lib/Modal'

const initialUsername: ChangeUsernameInput = { new_username: '', confirm_username: '' }
const initialPassword: ChangePasswordInput = { old_password: '', new_password: '', confirm_password: '' }
const initialEmailRequest: ChangeEmailRequestInput = { new_email: '' }
const initialEmailOtp: ChangeEmailOtpInput = { otp: '' }

type SectionState = 'idle' | 'submitting'
type EmailStep = 'enter-email' | 'enter-otp' | 'confirmed'

async function postJson(url: string, body: unknown) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
    credentials: 'same-origin',
    body: JSON.stringify(body),
  })
}

interface UsernameSectionProps {
  /** Fired once the username is actually saved server-side, so the parent
   * modal can remember it needs to revert this on Cancel/close-without-Done. */
  onSaved: () => void
}

function UsernameSection({ onSaved }: UsernameSectionProps) {
  const [values, setValues] = useState<ChangeUsernameInput>(initialUsername)
  const [errors, setErrors] = useState<ChangeUsernameErrors>({})
  const [serverError, setServerError] = useState<string | null>(null)
  const [state, setState] = useState<SectionState | 'success'>('idle')
  const [savedUsername, setSavedUsername] = useState('')

  const handleChange =
    (field: keyof ChangeUsernameInput) =>
    (e: ChangeEvent<HTMLInputElement>) =>
      setValues((prev) => ({ ...prev, [field]: e.target.value }))

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = changeUsernameSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: ChangeUsernameErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ChangeUsernameInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await postJson('/api/admin-hub/change-username/', { new_username: result.data.new_username })

      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }

      // No reload here — the change is already saved, but it's still
      // provisional until Account Settings' Done button is clicked (Cancel
      // or closing the modal any other way reverts it). The header only
      // needs to reflect the new name once it's actually locked in, which
      // the parent handles by reloading on Done.
      setSavedUsername(result.data.new_username)
      setValues(initialUsername)
      setState('success')
      onSaved()
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  if (state === 'success') {
    return (
      <>
        <h4>Change Username</h4>
        <p className="form-note form-note--success">
          Username changed to <strong>{savedUsername}</strong>.
        </p>
        <div className="logo-card__admin-actions">
          <button type="button" className="btn btn--outline" onClick={() => setState('idle')}>Change Again</button>
        </div>
      </>
    )
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h4>Change Username</h4>
      <div className="field">
        <label htmlFor="new_username">New Username</label>
        <input
          id="new_username"
          type="text"
          value={values.new_username}
          onChange={handleChange('new_username')}
          disabled={state === 'submitting'}
          autoComplete="username"
        />
        {errors.new_username && <p className="form-note">{errors.new_username}</p>}
      </div>

      <div className="field">
        <label htmlFor="confirm_username">Confirm New Username</label>
        <input
          id="confirm_username"
          type="text"
          value={values.confirm_username}
          onChange={handleChange('confirm_username')}
          disabled={state === 'submitting'}
          autoComplete="username"
        />
        {errors.confirm_username && <p className="form-note">{errors.confirm_username}</p>}
      </div>

      {serverError && <p className="form-note">{serverError}</p>}

      <div className="logo-card__admin-actions">
        <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
          {state === 'submitting' ? 'Saving…' : 'Save Username'}
        </button>
      </div>
    </form>
  )
}

interface PasswordSectionProps {
  /** Fired once the password is actually saved server-side, carrying the
   * exact old/new plaintext values so the parent can reverse the change
   * later (old_password becomes the revert's new_password, new_password
   * becomes the revert's old_password) without storing anything itself
   * beyond what the admin already typed into this form. */
  onSaved: (oldPassword: string, newPassword: string) => void
}

function PasswordSection({ onSaved }: PasswordSectionProps) {
  const [values, setValues] = useState<ChangePasswordInput>(initialPassword)
  const [errors, setErrors] = useState<ChangePasswordErrors>({})
  const [serverError, setServerError] = useState<string | null>(null)
  const [state, setState] = useState<SectionState | 'success'>('idle')

  const handleChange =
    (field: keyof ChangePasswordInput) =>
    (e: ChangeEvent<HTMLInputElement>) =>
      setValues((prev) => ({ ...prev, [field]: e.target.value }))

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = changePasswordSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: ChangePasswordErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ChangePasswordInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})
    setState('submitting')

    try {
      const res = await postJson('/api/admin-hub/change-password/', {
        old_password: result.data.old_password,
        new_password: result.data.new_password,
      })

      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }

      onSaved(result.data.old_password, result.data.new_password)
      setValues(initialPassword)
      setState('success')
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  if (state === 'success') {
    return (
      <>
        <h4>Change Password</h4>
        <p className="form-note form-note--success">Password changed successfully. Use it next time you log in.</p>
        <div className="logo-card__admin-actions">
          <button type="button" className="btn btn--outline" onClick={() => setState('idle')}>Change Again</button>
        </div>
      </>
    )
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h4>Change Password</h4>
      <div className="field">
        <label htmlFor="old_password">Current Password</label>
        <input
          id="old_password"
          type="password"
          value={values.old_password}
          onChange={handleChange('old_password')}
          disabled={state === 'submitting'}
          autoComplete="current-password"
        />
        {errors.old_password && <p className="form-note">{errors.old_password}</p>}
      </div>

      <div className="field">
        <label htmlFor="new_password">New Password</label>
        <input
          id="new_password"
          type="password"
          value={values.new_password}
          onChange={handleChange('new_password')}
          disabled={state === 'submitting'}
          autoComplete="new-password"
        />
        <p className="field__hint">{PASSWORD_REQUIREMENTS_HINT}</p>
        {errors.new_password && <p className="form-note">{errors.new_password}</p>}
      </div>

      <div className="field">
        <label htmlFor="confirm_password">Confirm New Password</label>
        <input
          id="confirm_password"
          type="password"
          value={values.confirm_password}
          onChange={handleChange('confirm_password')}
          disabled={state === 'submitting'}
          autoComplete="new-password"
        />
        {errors.confirm_password && <p className="form-note">{errors.confirm_password}</p>}
      </div>

      {serverError && <p className="form-note">{serverError}</p>}

      <div className="logo-card__admin-actions">
        <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
          {state === 'submitting' ? 'Saving…' : 'Save New Password'}
        </button>
      </div>
    </form>
  )
}

interface EmailSectionProps {
  /** Fired once a new email is actually saved server-side (OTP verified),
   * so the parent knows to call the revert endpoint on Cancel/close. */
  onSaved: () => void
}

function EmailSection({ onSaved }: EmailSectionProps) {
  // The checkbox only gates whether the email-change UI is shown — the
  // actual "confirmed" state (and the green tick) is driven by whether an
  // OTP has been successfully verified this session, tracked separately so
  // unticking the box doesn't pretend a real, already-saved confirmation
  // never happened.
  const [checked, setChecked] = useState(false)
  const [step, setStep] = useState<EmailStep>('enter-email')
  const [confirmedEmail, setConfirmedEmail] = useState<string | null>(null)

  const [emailValues, setEmailValues] = useState<ChangeEmailRequestInput>(initialEmailRequest)
  const [emailErrors, setEmailErrors] = useState<ChangeEmailRequestErrors>({})
  const [otpValues, setOtpValues] = useState<ChangeEmailOtpInput>(initialEmailOtp)
  const [otpErrors, setOtpErrors] = useState<ChangeEmailOtpErrors>({})

  const [serverError, setServerError] = useState<string | null>(null)
  const [serverNotice, setServerNotice] = useState<string | null>(null)
  const [state, setState] = useState<SectionState>('idle')

  function handleCheckboxChange(e: ChangeEvent<HTMLInputElement>) {
    setChecked(e.target.checked)
    setServerError(null)
    setServerNotice(null)
  }

  async function requestOtp(email: string) {
    return postJson('/api/admin-hub/change-email/request-otp/', { new_email: email })
  }

  async function handleEmailSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const result = changeEmailRequestSchema.safeParse(emailValues)
    if (!result.success) {
      const fieldErrors: ChangeEmailRequestErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ChangeEmailRequestInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setEmailErrors(fieldErrors)
      return
    }
    setEmailErrors({})
    setState('submitting')

    try {
      const res = await requestOtp(result.data.new_email)
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }
      setState('idle')
      setStep('enter-otp')
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
      const res = await requestOtp(emailValues.new_email)
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

    const result = changeEmailOtpSchema.safeParse(otpValues)
    if (!result.success) {
      const fieldErrors: ChangeEmailOtpErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof ChangeEmailOtpInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setOtpErrors(fieldErrors)
      return
    }
    setOtpErrors({})
    setState('submitting')

    try {
      const res = await postJson('/api/admin-hub/change-email/verify/', {
        new_email: emailValues.new_email,
        otp: result.data.otp,
      })

      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return
      }

      // Verifying the OTP is what saves the new address server-side — no
      // separate "Save Email" step, matching the requested "green tick means
      // it's confirmed" behavior. It's still provisional, though: Cancel (or
      // closing the modal any other way) still reverts it, same as
      // Username/Password, until Done is clicked.
      setConfirmedEmail(emailValues.new_email)
      setOtpValues(initialEmailOtp)
      setState('idle')
      setStep('confirmed')
      onSaved()
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
    }
  }

  function startOver() {
    setStep('enter-email')
    setEmailValues(initialEmailRequest)
    setOtpValues(initialEmailOtp)
    setServerError(null)
    setServerNotice(null)
  }

  return (
    <div className="account-email-section">
      <h4>Change Email</h4>
      <label className="field field--checkbox">
        <input type="checkbox" checked={checked} onChange={handleCheckboxChange} />
        <span>I want to change my registered email</span>
        {confirmedEmail && (
          <span
            className="email-confirmed-tick"
            role="img"
            aria-label={`Email confirmed: ${confirmedEmail}`}
            title={`Confirmed: ${confirmedEmail}`}
          >
            ✓
          </span>
        )}
      </label>

      {checked && step === 'enter-email' && (
        <form onSubmit={handleEmailSubmit} noValidate>
          <div className="field">
            <label htmlFor="new_email">New Email</label>
            <input
              id="new_email"
              type="email"
              value={emailValues.new_email}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setEmailValues({ new_email: e.target.value })}
              disabled={state === 'submitting'}
              autoComplete="email"
            />
            {emailErrors.new_email && <p className="form-note">{emailErrors.new_email}</p>}
          </div>
          {serverError && <p className="form-note">{serverError}</p>}
          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Sending…' : 'Send Code'}
            </button>
          </div>
        </form>
      )}

      {checked && step === 'enter-otp' && (
        <form onSubmit={handleOtpSubmit} noValidate>
          <p className="modal__body">
            Enter the 6-digit code sent to <strong>{emailValues.new_email}</strong>. It expires in 5 minutes.
          </p>
          <div className="field">
            <label htmlFor="email_otp">Verification Code</label>
            <input
              id="email_otp"
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
          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Verifying…' : 'Verify Code'}
            </button>
            <button type="button" className="btn--link" onClick={handleResendOtp} disabled={state === 'submitting'}>
              Resend Code
            </button>
          </div>
        </form>
      )}

      {checked && step === 'confirmed' && confirmedEmail && (
        <p className="form-note form-note--success">
          Email confirmed: <strong>{confirmedEmail}</strong>{' '}
          <button type="button" className="btn--link" onClick={startOver}>Change again</button>
        </p>
      )}
    </div>
  )
}

interface AccountSettingsButtonProps {
  /** The username as rendered on the page when it loaded — the "revert to"
   * target if the admin backs out of a username change without hitting
   * Done. Read once from the mount element's data attribute (see main.tsx),
   * same convention as admin-site-settings' EditableStat. Email needs no
   * equivalent here — AdminHubChangeEmailRevertView restores it server-side
   * from what it stashed when the change was verified, so the frontend
   * never needs to know the original address at all. */
  initialUsername: string
}

/** Tracks what's actually been saved server-side during the current modal
 * session, so Cancel (or any other way of closing the modal) knows exactly
 * what to undo. Kept in a ref, not state, since it's write-only until the
 * moment of a revert/close and shouldn't itself trigger re-renders. */
interface PendingChanges {
  usernameChanged: boolean
  emailChanged: boolean
  /** Set on the first successful password change this session and left
   * alone after — it's the true original, needed as the revert's
   * new_password regardless of how many times the password is re-changed
   * before Cancel/Done. */
  originalPassword: string | null
  /** Updated on every successful password change — it's whatever is
   * currently active in the DB, needed as the revert's old_password. */
  currentPassword: string | null
}

function emptyPendingChanges(): PendingChanges {
  return { usernameChanged: false, emailChanged: false, originalPassword: null, currentPassword: null }
}

export default function AccountSettingsButton({ initialUsername }: AccountSettingsButtonProps) {
  const [open, setOpen] = useState(false)
  const [resetKey, setResetKey] = useState(0)
  const pending = useRef<PendingChanges>(emptyPendingChanges())

  function handleUsernameSaved() {
    pending.current.usernameChanged = true
  }

  function handlePasswordSaved(oldPassword: string, newPassword: string) {
    if (pending.current.originalPassword === null) {
      pending.current.originalPassword = oldPassword
    }
    pending.current.currentPassword = newPassword
  }

  function handleEmailSaved() {
    pending.current.emailChanged = true
  }

  /** Best-effort — if a revert call fails (e.g. a network blip) the modal
   * still closes rather than trapping the admin in it; there's no realistic
   * retry UI worth building for what should be a rare failure on an
   * internal admin tool. */
  async function revertPendingChanges() {
    const p = pending.current
    const tasks: Promise<unknown>[] = []

    if (p.usernameChanged) {
      tasks.push(postJson('/api/admin-hub/change-username/', { new_username: initialUsername }))
    }
    if (p.originalPassword !== null && p.currentPassword !== null) {
      tasks.push(postJson('/api/admin-hub/change-password/', {
        old_password: p.currentPassword,
        new_password: p.originalPassword,
      }))
    }
    if (p.emailChanged) {
      tasks.push(postJson('/api/admin-hub/change-email/revert/', {}))
    }

    if (tasks.length > 0) {
      await Promise.allSettled(tasks)
    }
  }

  function hasPendingChanges() {
    const p = pending.current
    return p.usernameChanged || p.emailChanged || p.currentPassword !== null
  }

  /** Cancel button, Escape key, and overlay click all funnel through here —
   * every way of leaving the modal other than Done reverts whatever was
   * applied this session. */
  async function handleCancel() {
    if (hasPendingChanges()) {
      await revertPendingChanges()
    }
    pending.current = emptyPendingChanges()
    setResetKey((k) => k + 1)
    setOpen(false)
  }

  function handleDone() {
    const usernameChanged = pending.current.usernameChanged
    pending.current = emptyPendingChanges()
    setResetKey((k) => k + 1)
    setOpen(false)

    // The header's username display is server-rendered, not part of this
    // React tree — reload to reflect the now-locked-in name everywhere it
    // appears. Nothing else changed here (password, email) is shown
    // elsewhere on the page, so no reload is needed for those alone.
    if (usernameChanged) {
      window.location.reload()
    }
  }

  return (
    <>
      <button type="button" className="btn btn--outline" onClick={() => setOpen(true)}>
        Account Settings
      </button>

      <Modal open={open} onClose={handleCancel} title="Account Settings" hideCloseButton>
        <UsernameSection key={`username-${resetKey}`} onSaved={handleUsernameSaved} />
        <hr className="admin-modal-divider" />
        <PasswordSection key={`password-${resetKey}`} onSaved={handlePasswordSaved} />
        <hr className="admin-modal-divider" />
        <EmailSection key={`email-${resetKey}`} onSaved={handleEmailSaved} />

        <div className="account-settings-footer">
          <button type="button" className="btn btn--outline" onClick={handleCancel}>Cancel</button>
          <button type="button" className="btn btn--primary" onClick={handleDone}>Done</button>
        </div>
      </Modal>
    </>
  )
}
