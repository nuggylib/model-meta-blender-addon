# `.github/`

GitHub configuration: the PR template and CI workflows.

- `pull_request_template.md`: default PR body. GitHub only applies it from `main`.
- `workflows/version-check.yml`: on PRs into `main`, fails unless the manifest `version` is higher
  than `main`'s and `v<version>` isn't tagged. Passes without a bump when nothing under `src/` changed
  except `*.md` files. See `.claude/skills/version-bumping/SKILL.md`.
- `workflows/tag-release.yml`: on each push to `main` (a squash merge), tags the commit
  `v<manifest version>`. Fails if that tag exists. Skips when nothing under `src/` changed except
  `*.md` files.
- `workflows/qa_signoff.yml`: fails a PR until the `- [x] **Author:**` box in its body is ticked.
  Brought over from model-meta.

## Conventions

- The `**Author:**` marker is shared by `pull_request_template.md` and the `qa_signoff.yml` grep.
  Change both together, or the check fails on every PR.
- Pass the PR body through `env:`, never into a `run:` script directly.
- A check can only be marked required in branch protection after it has run once.
