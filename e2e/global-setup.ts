import { execFileSync } from 'node:child_process';
import path from 'node:path';

const REPO_ROOT = path.resolve(__dirname, '..');
const PYTHON = process.platform === 'win32'
  ? path.join(REPO_ROOT, 'venv', 'Scripts', 'python.exe')
  : path.join(REPO_ROOT, 'venv', 'bin', 'python');

async function assertServerUp(url: string, label: string) {
  try {
    await fetch(url);
  } catch {
    throw new Error(
      `${label} doesn't seem to be running at ${url}. ` +
      'This suite runs against your already-running dev servers rather than ' +
      'starting its own — start it before running the e2e suite (see e2e/README.md).'
    );
  }
}

// Runs once before the whole suite. Fails fast with a readable message
// instead of letting every single test time out one-by-one if the dev
// servers aren't up, then seeds the one throwaway admin account the admin
// specs log in as (core/management/commands/e2e_data.py — runs against
// whatever database manage.py is already pointed at, not a separate test DB).
export default async function globalSetup() {
  await assertServerUp('http://localhost:8000/', 'Django (python manage.py runserver)');
  await assertServerUp('http://localhost:5173/', 'Vite (npm run dev, inside frontend/)');

  execFileSync(PYTHON, ['manage.py', 'e2e_data', 'setup'], {
    cwd: REPO_ROOT,
    stdio: 'inherit',
  });
}
