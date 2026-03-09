# Branch Cleanup Report (2026-03-09)

## Current Summary

- Base branch: `main` (authoritative branch)
- Current worktree branch: `advisor`
- `git fetch --all --prune` completed on 2026-03-09
- Local branches before cleanup: 23
- Local branches after cleanup: 20
- Remote branches under `origin`: 10 (`origin/HEAD` excluded)
- Linked worktrees: `main`, `advisor`, `builder`, `docs/2026-03-09-constraints-design-262`

## Classification

### Delete Candidate

- `advisor-clean-20260309`
  - Same tip commit as `advisor` (`1ce15b8`)
  - Temporary cleanup branch name
  - Local-only duplicate branch
- `docs/storage-policy-185`
  - Upstream is `[gone]`
  - No branch-only patch remained against `main` in `git log --cherry-pick main...docs/storage-policy-185`
  - Role-ended docs branch
- `feat/227-make-dev-setup`
  - Listed in `git branch --merged main`
  - Local-only temporary feature branch
- `feat/238-discord-webhook-adapter`
  - Upstream is `[gone]`
  - No branch-only patch remained against `main`
  - Role-ended temporary feature branch
- `feat/daily-input-ux-minimal-flow-180`
  - Listed in `git branch --merged main`
  - Issue/feature branch appears complete; remote branch still exists, but local branch is redundant
- `feat/storage-migration-tool-190-clean`
  - Upstream is `[gone]`
  - No branch-only patch remained against `main`
  - `-clean` temporary branch naming
- `fix/2026-03-08-pr184-ui-only`
  - Listed in `git branch --merged main`
  - Local-only PR-derived temporary branch (`ui-only`)

### Hold

- `docs/2026-03-08-quick-mode-contract`
  - Remote still exists
  - Not merged to `main`
  - Recent docs work; active continuation is plausible
- `docs/deterministic-toolchain-baseline-260`
  - Remote still exists
  - No unique patch vs `main`, but not a direct merge ancestor of `main`
  - Safe local deletion is possible later, but evidence is weaker than the delete-candidate set
- `feat/220-codex-notify-hook`
  - Upstream is `[gone]`
  - Branch-only commits remain outside `main`
  - Deleting would risk losing unmerged work
- `feat/issue-234-candidate-tokenization`
  - Remote still exists
  - No unique patch vs `main`, but branch is still tracked and issue-oriented
  - Treated as active until explicitly closed out
- `feat/make-daily-ops-177`
  - Upstream is `[gone]`
  - Branch-only commits remain outside `main`
- `feat/tag-based-candidates-214`
  - Upstream is `[gone]`
  - Branch-only commits remain outside `main`
- `feat/unified-heatmap-candidates-input-flow-187`
  - Upstream is `[gone]`
  - Branch-only commits remain outside `main`
- `fix/2026-03-08-pr184-scope`
  - Ahead/behind its tracked branch (`origin/feat/daily-input-ux-minimal-flow-180`)
  - Branch-only patch remains outside `main`
  - PR-scope derivative branch; needs manual intent confirmation
- `fix/log-form-jsonl-mirror-split-182`
  - Remote still exists
  - Branch-only commits remain outside `main`
- `fix/pr182-scope-only-177`
  - Upstream is `[gone]`
  - Branch-only commits remain outside `main`
- `issue-213-daily-log-ux`
  - Remote still exists
  - No unique patch vs `main`, but issue branch is still present remotely
  - Hold until remote cleanup policy is decided

### Keep

- `main`
  - Authoritative branch
  - Linked worktree
- `ops`
  - Permanent operations branch
- `advisor`
  - Permanent advisor branch
  - Current branch
- `builder`
  - Permanent builder branch
  - Linked worktree
- `docs/2026-03-09-constraints-design-262`
  - Linked worktree in active use
  - Recent design branch with remote tracking

## Remote Residual Notes

- Remaining remote branches after prune are:
  - `origin/advisor`
  - `origin/docs/2026-03-08-quick-mode-contract`
  - `origin/docs/2026-03-09-constraints-design-262`
  - `origin/docs/deterministic-toolchain-baseline-260`
  - `origin/feat/daily-input-ux-minimal-flow-180`
  - `origin/feat/issue-234-candidate-tokenization`
  - `origin/fix/log-form-jsonl-mirror-split-182`
  - `origin/issue-213-daily-log-ux`
  - `origin/main`
  - `origin/ops`
- `fetch --prune` already removed remote-tracking refs whose upstream had disappeared.
- This report only deletes local branches. Remote branch deletion should be handled separately after owner/PR intent is confirmed.

## Deletion Result

- Deleted with `git branch -d`
  - `feat/227-make-dev-setup`
  - `feat/daily-input-ux-minimal-flow-180`
  - `fix/2026-03-08-pr184-ui-only`
- Not deleted because `git branch -d` refused
  - `advisor-clean-20260309`
    - Exact duplicate of `advisor`, but `-d` refused because its upstream is `origin/main` and that upstream does not contain the branch tip
    - Strong `git branch -D` candidate if you want to remove the duplicate ref later
  - `docs/storage-policy-185`
    - `[gone]` and no branch-only patch vs `main`, but not considered fully merged by `git branch -d`
    - Requires explicit `-D` decision
  - `feat/238-discord-webhook-adapter`
    - `[gone]` and no branch-only patch vs `main`, but not considered fully merged by `git branch -d`
    - Requires explicit `-D` decision
  - `feat/storage-migration-tool-190-clean`
    - `[gone]` and no branch-only patch vs `main`, but not considered fully merged by `git branch -d`
    - Requires explicit `-D` decision

## Commands Run

- `git status --short --branch`
- `git remote -v`
- `git fetch --all --prune`
- `git branch -vv`
- `git branch --merged main`
- `git for-each-ref --sort=refname --format='%(refname:short)|%(objectname:short)|%(upstream:short)|%(upstream:trackshort)|%(committerdate:short)|%(subject)' refs/heads`
- `git for-each-ref --sort=refname --format='%(refname:short)|%(objectname:short)|%(committerdate:short)|%(subject)' refs/remotes/origin`
- `for b in $(git for-each-ref --format="%(refname:short)" refs/heads); do git rev-list --left-right --count main..."$b"; git log --cherry-pick --right-only --no-merges --oneline main..."$b"; done`
- `git for-each-ref --format='%(objectname:short) %(refname:short)' refs/heads | sort`
- `git worktree list --porcelain`
- `comm -3 <(git for-each-ref --format="%(refname:short)" refs/heads | sort) <(git for-each-ref --format="%(refname:short)" refs/remotes/origin | sed "s#^origin/##" | grep -v "^HEAD$" | sort)`

## Second Pass (2026-03-09)

### Snapshot

- Local branches after second pass: 16
- Current worktree branch: `advisor`
- Linked worktrees at verification time: `main`, `advisor`, `builder`, `ops`
- Remote branches were not modified

### Re-evaluation of `git branch -d` Failures

- `advisor-clean-20260309`
  - Same tip as `advisor` (`1ce15b8`)
  - `git log main..advisor-clean-20260309` showed one commit because `advisor` itself is ahead of `main`
  - Safe to force-delete because the commit remains reachable from `advisor` and `origin/advisor`
- `docs/storage-policy-185`
  - Upstream already gone
  - `git cherry -v main docs/storage-policy-185` returned `- a31e7fb...`
  - Patch-equivalent content is already reflected in `main`; `git branch -d` failed only on merge shape
  - Force-delete approved
- `feat/238-discord-webhook-adapter`
  - Upstream already gone
  - `git cherry -v main feat/238-discord-webhook-adapter` returned `- 969c0ec...`
  - Patch-equivalent content is already reflected in `main`
  - Force-delete approved
- `feat/storage-migration-tool-190-clean`
  - Upstream already gone
  - `git cherry -v main feat/storage-migration-tool-190-clean` returned `- 6ddbed4...`
  - Patch-equivalent content is already reflected in `main`
  - Force-delete approved

### Force Deleted with `git branch -D`

- `advisor-clean-20260309`
- `docs/storage-policy-185`
- `feat/238-discord-webhook-adapter`
- `feat/storage-migration-tool-190-clean`

### Hold Reclassification

#### Active

- `docs/2026-03-08-quick-mode-contract`
  - Remote still exists
  - One branch-only patch remains outside `main`
- `feat/220-codex-notify-hook`
  - Upstream is gone, but two branch-only patches remain outside `main`
  - Recent notification-related work; deleting would risk loss
- `fix/2026-03-08-pr184-scope`
  - Ahead/behind its tracked branch
  - One branch-only patch remains outside `main`
- `fix/log-form-jsonl-mirror-split-182`
  - Remote still exists
  - Three branch-only patches remain outside `main`

#### Dormant

- `feat/make-daily-ops-177`
  - Upstream is gone
  - Three branch-only patches remain outside `main`, but no remote or linked worktree remains
- `feat/tag-based-candidates-214`
  - Upstream is gone
  - Three branch-only patches remain outside `main`, but no remote or linked worktree remains
- `feat/unified-heatmap-candidates-input-flow-187`
  - Upstream is gone
  - Two branch-only patches remain outside `main`, but no remote or linked worktree remains
- `fix/pr182-scope-only-177`
  - Upstream is gone
  - Four branch-only patches remain outside `main`, but no remote or linked worktree remains

#### Watchlist for Next Cleanup

- `docs/deterministic-toolchain-baseline-260`
  - Remote still exists
  - `git cherry -v main` returned `-`; no branch-only patch remains
  - Likely removable after remote close-out is confirmed
- `feat/issue-234-candidate-tokenization`
  - Remote still exists
  - `git cherry -v main` returned `-`; no branch-only patch remains
  - Likely removable after remote close-out is confirmed
- `issue-213-daily-log-ux`
  - Remote still exists
  - `git cherry -v main` returned `-`; no branch-only patch remains
  - Likely removable after remote close-out is confirmed

### Next Review Candidates

- Review `docs/deterministic-toolchain-baseline-260`, `feat/issue-234-candidate-tokenization`, and `issue-213-daily-log-ux` first once remote cleanup ownership is clear
- Recheck dormant local-only branches after 7 to 14 days of inactivity
- If dormant branches remain unused, inspect with `git log main..BRANCH` and either revive them explicitly or archive/delete them

### Additional Commands Run in Second Pass

- `git log --oneline --decorate main..BRANCH`
- `git log --oneline --decorate BRANCH..main`
- `git diff --stat main...BRANCH`
- `git merge-base main BRANCH`
- `git cherry -v main BRANCH`
- `git branch -D advisor-clean-20260309 docs/storage-policy-185 feat/238-discord-webhook-adapter feat/storage-migration-tool-190-clean`
