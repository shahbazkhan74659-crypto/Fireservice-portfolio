# Ownership Transfer Plan — Iconic Techno Service (ITS)

Goal: shift 100% ownership of this project to the client. Developer (Shahbaz)
keeps no standing access after this is complete — any future work happens
through a client-owned identity that the client can revoke at will.

Status legend: `[ ]` pending · `[x]` done

## Steps

1. `[ ]` **Create client's GitHub account.**
   Client sets up their own personal GitHub account (their own email), if they
   don't already have one. Needed as the transfer target for step 2.

2. `[ ]` **Transfer the GitHub repo to the client's account.**
   Original repo: `shahbazkhan74659-crypto/FireService` (private).
   `Settings → Danger Zone → Transfer ownership` on the original repo, target
   = client's new GitHub username. Client must accept the transfer invite by
   email for it to complete.
   - Portfolio safeguard already done: a full mirror of the repo
     (`shahbazkhan74659-crypto/Fireservice-portfolio`) was created and pushed
     under the developer's own account *before* transfer, then made public,
     so the developer keeps a permanent independent copy for portfolio use.
   - After transfer: any deploy key/CI secrets tied to the developer's
     GitHub session need re-issuing under the client's account (see the
     Oracle VM's read-only deploy key, currently registered against the
     pre-transfer repo).

3. `[ ]` **Create a new "developer" Oracle Cloud identity from the client's
   different email.**
   Client provides a second email/Gmail (not the one already used for the
   main Oracle tenancy owner login) that they own and control. A new IAM
   user is created in Oracle Cloud under that email — this becomes the
   identity any future developer work goes through, instead of the
   developer's own personal email.

4. `[ ]` **Give delegate/IAM access to that client-owned developer account.**
   Grant the new IAM user (step 3) the same scoped policy the current
   `deploy-admin` user has (manage instance-family / volume-family /
   virtual-network-family / object-family, plus self-service credential
   management) — enough to operate the VM, nothing tenancy-wide. This
   account is the one used going forward if the client ever needs
   developer help again.

5. `[ ]` **Cancel the developer's own Oracle Cloud delegate access.**
   Revoke/deactivate the existing `deploy-admin` IAM user tied to
   `shahbazkhan74659@gmail.com`: remove its API key (the pair currently at
   `C:\FireService!\x\`), remove it from the `deploy-admin` group/policy, and
   confirm it can no longer authenticate.

6. `[ ]` **Cancel the developer's GoDaddy delegate access.**
   On the client's GoDaddy account (`iconictechnoservice2026`) → Account
   Settings → Delegate Access → revoke the invite currently accepted from the
   developer's own separate GoDaddy account. Removes the developer's DNS
   management access to `iconictechnoservice.com`.

7. `[ ]` **Delete the developer's Oracle Cloud IAM user entirely.**
   Once steps 3–5 are confirmed working (client's new developer identity can
   actually operate the VM), delete the old `deploy-admin` IAM user for
   `shahbazkhan74659@gmail.com` outright rather than leaving it disabled.

8. `[ ]` **Hand over the full original codebase + local secrets via Docker,
   directly onto the client's machine.**
   Covers everything that is gitignored and therefore never reached GitHub —
   the repo transfer (step 2) alone does not carry these over. Plan: create a
   Docker account on the client's machine, package the full local working
   copy (source + the untracked/gitignored files below) into an image/
   container, and transfer it to the client's own Docker account so the
   client ends up with an exact, complete copy — not just what's in git.
   Files this needs to cover (everything currently `.gitignore`d locally):
   - `.env` (live local Django secrets)
   - `essentials.md` (Oracle signup notes incl. client's bank/address details)
   - `.oci_config.txt` / `.oracle_vm_secrets.txt` (Oracle VM credentials)
   - `C:\FireService!\x\` (the developer's Oracle API key pair — superseded
     by step 3's new key anyway, but the folder should still transfer or be
     deleted, not left behind)
   - `~/.ssh/oracle_its_vm` + `.pub` (SSH key used to reach the VM)
   - `~/.ssh/github_deploy_key` (VM's read-only GitHub deploy key)

## Notes / dependencies

- Steps 3–5 should happen in that order — don't cancel the developer's own
  access (5, 7) until the replacement client-owned identity (3–4) is
  confirmed to actually work, or the VM becomes unreachable with no one able
  to fix it.
- Local secrets on the developer's machine tied to the old identity
  (`.oci_config.txt`, `.oracle_vm_secrets.txt`, `C:\FireService!\x\` API key
  pair, `~/.ssh/oracle_its_vm`, `~/.ssh/github_deploy_key`) should be cleaned
  up/rotated once the corresponding access is cancelled.
