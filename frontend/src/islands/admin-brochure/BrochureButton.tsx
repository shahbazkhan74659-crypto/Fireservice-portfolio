import { useRef, useState, type ChangeEvent } from 'react'
import { pdfFileSchema, type Brochure } from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from '../../lib/api'
import Modal from '../../lib/Modal'

const ENDPOINT = '/api/admin-hub/brochure/'

type BusyState = 'idle' | 'busy'

interface Props {
  initialBrochure: Brochure
}

export default function BrochureButton({ initialBrochure }: Props) {
  const [open, setOpen] = useState(false)
  const [brochure, setBrochure] = useState(initialBrochure)
  const [fileName, setFileName] = useState<string | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)
  const [serverError, setServerError] = useState<string | null>(null)
  const [state, setState] = useState<BusyState>('idle')
  // The PDF URL as it was before any replacement this modal session — used
  // by Cancel to restore it. Doesn't change on re-open until Done commits.
  const originalPdfUrl = useRef(initialBrochure.pdf)
  const replaced = useRef(false)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  function resetFileInput() {
    setFileName(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  function openModal() {
    resetFileInput()
    setFileError(null)
    setServerError(null)
    setOpen(true)
  }

  async function uploadPdf(file: File): Promise<boolean> {
    setServerError(null)
    setState('busy')
    const formData = new FormData()
    formData.append('pdf', file)
    try {
      const res = await fetch(ENDPOINT, {
        method: 'PATCH',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: formData,
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setState('idle')
        return false
      }
      const updated: Brochure = await res.json()
      setBrochure(updated)
      setState('idle')
      return true
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setState('idle')
      return false
    }
  }

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null
    // Deliberately not reset to '' here (unlike AddSlideControl) — leaving
    // it be lets the native "Choose File" control show the real filename
    // instead of reverting to "No file chosen" right after a pick, which
    // read as contradicting the "Selected: …" text below it.
    if (!file) return

    const result = pdfFileSchema.safeParse(file)
    if (!result.success) {
      setFileError(result.error.issues[0]?.message ?? 'Invalid file.')
      return
    }
    setFileError(null)
    setFileName(file.name)

    if (await uploadPdf(result.data)) {
      replaced.current = true
    }
  }

  /** Escape/overlay-click and the Cancel button all funnel here — same
   * "provisional until Done" behavior as Account Settings: a replacement
   * made this session is applied immediately (so the preview reflects it),
   * but backing out any other way than Done reverts it by re-uploading the
   * PDF that was active before this modal session touched it. */
  async function handleCancel() {
    if (replaced.current) {
      setState('busy')
      try {
        const res = await fetch(originalPdfUrl.current, { credentials: 'same-origin' })
        const blob = await res.blob()
        const originalFile = new File([blob], 'brochure.pdf', { type: 'application/pdf' })
        await uploadPdf(originalFile)
      } catch {
        // Best-effort, same posture as Account Settings' revertPendingChanges()
        // — if this fails (e.g. a network blip) the replacement stands rather
        // than trapping the admin in the modal.
      }
      replaced.current = false
      setState('idle')
    }
    resetFileInput()
    setFileError(null)
    setServerError(null)
    setOpen(false)
  }

  function handleDone() {
    originalPdfUrl.current = brochure.pdf
    replaced.current = false
    setOpen(false)
  }

  return (
    <>
      <button type="button" className="cc-btn" onClick={openModal}>Brochure</button>

      <Modal open={open} onClose={handleCancel} title="Brochure" hideCloseButton>
        <div className="brochure-preview">
          <img src={brochure.image} alt="Brochure first page preview" />
        </div>

        <p className="modal__body">Replace the Brochure</p>

        <div className="field">
          <label htmlFor="brochure-pdf-file">Choose PDF</label>
          <input
            ref={fileInputRef}
            id="brochure-pdf-file"
            type="file"
            accept="application/pdf"
            autoComplete="off"
            onChange={handleFileChange}
            disabled={state === 'busy'}
          />
          {fileName && <p className="form-note form-note--success">Selected: {fileName}</p>}
          {fileError && <p className="form-note">{fileError}</p>}
        </div>

        {serverError && <p className="form-note">{serverError}</p>}

        <div className="account-settings-footer">
          <button type="button" className="btn btn--outline" onClick={handleCancel} disabled={state === 'busy'}>
            Cancel
          </button>
          <button type="button" className="btn btn--primary" onClick={handleDone} disabled={state === 'busy'}>
            Done
          </button>
        </div>
      </Modal>
    </>
  )
}
