export function getCookie(name: string): string | null {
  const match = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
  if (!match) return null
  return decodeURIComponent(match.split('=').slice(1).join('='))
}

export function getCsrfToken(): string {
  const token = getCookie('csrftoken')
  if (!token) {
    throw new Error('CSRF cookie not found — reload the page and try again.')
  }
  return token
}
