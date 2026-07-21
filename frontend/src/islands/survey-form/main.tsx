import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import SurveyForm from './SurveyForm'

const container = document.getElementById('survey-form-root')
if (container) {
  createRoot(container).render(
    <StrictMode>
      <SurveyForm />
    </StrictMode>,
  )
}
