import { execFileSync } from 'node:child_process';
import path from 'node:path';

const REPO_ROOT = path.resolve(__dirname, '..');
const PYTHON = process.platform === 'win32'
  ? path.join(REPO_ROOT, 'venv', 'Scripts', 'python.exe')
  : path.join(REPO_ROOT, 'venv', 'bin', 'python');

// Runs once after the whole suite (even on failure) — removes the
// throwaway e2e_admin account and every marker-tagged row the specs
// created (leads, the test Brand), so repeat runs never accumulate junk
// in the real dev database this suite runs against.
export default async function globalTeardown() {
  execFileSync(PYTHON, ['manage.py', 'e2e_data', 'teardown'], {
    cwd: REPO_ROOT,
    stdio: 'inherit',
  });
}
