// Must match core/management/commands/e2e_data.py exactly — that command
// (run once by global-setup.ts/global-teardown.ts) is the source of truth
// for this account and marker string; these are copies for the specs to
// reference, not a second source of truth.
export const E2E_USERNAME = 'e2e_admin';
export const E2E_PASSWORD = 'E2eTestAdmin123!';
export const E2E_MARKER = 'E2E Test Runner';
