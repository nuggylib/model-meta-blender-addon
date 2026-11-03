---
name: version-bumping
description: Use right after creating a new branch in this repo, to give it a new add-on version.
---

# Give each new branch a new add-on version

## Trigger
Use this skill right after creating a new branch (see `.claude/skills/branch-naming/SKILL.md`), before
its first commit. Each branch gets exactly one bump. Later changes on the same branch keep that version
unless the developer asks for another bump.

Skip this skill when the branch won't change anything under `src/` other than `*.md` files (e.g. a
README or CI-only change). Both workflows pass such branches without a bump or a tag.

## Pre-requisites
- The new branch is checked out and was created off an up-to-date `origin/main`.
- `<current>`: the `version` in `src/blender_manifest.toml` on `origin/main`:
  `git show origin/main:src/blender_manifest.toml | sed -n 's/^version = "\(.*\)"$/\1/p'`
- `<part>`: `major`, `minor`, or `patch`, picked by the developer. Always ask; never pick it yourself,
  even when the change looks obvious. Numbers are loosely chosen for now, but they must follow
  semantic versioning.

## Steps
1. Read `<current>`.
2. Ask the developer which part to bump, showing the version each choice produces. For `0.0.2`:
   - `major` → `1.0.0`
   - `minor` → `0.1.0`
   - `patch` → `0.0.3`
3. Build `<new>`: add one to the chosen part and reset every part to its right to `0`.
4. Check that `<new>` isn't already taken: `git tag --list "v<new>"` and
   `git ls-remote --tags origin "v<new>"` both print nothing. If either prints a tag, tell the developer
   and ask again.
5. Set `version = "<new>"` in `src/blender_manifest.toml`. Change nothing else.
6. Commit it on its own, following `.claude/skills/committing/SKILL.md`:
   `chore: bump extension version to <new>`.
7. On the PR, `.github/workflows/version-check.yml` fails unless `<new>` is higher than `main`'s
   version and not yet tagged.
8. Don't create a `v<new>` tag. When the PR is squash-merged, `.github/workflows/tag-release.yml` tags
   the merge commit on `main`. It fails if `v<new>` already exists.

## Verification process
- `git diff origin/main -- src/blender_manifest.toml` changes only the `version` line.
- `<new>` is greater than `<current>`, and its bumped part is one higher, with every part to its right
  set to `0`.
- The developer chose `<part>` in this task.
- `git log --oneline origin/main..HEAD -- src/blender_manifest.toml` lists exactly one commit.
- `git tag --list "v<new>"` prints nothing.

## Example output
Request: "Start a branch for ticket 80, adding bone counts."

After creating `armando/80/bone-counts`, `origin/main` is at `0.0.2`. The developer picks `minor`:

```
chore: bump extension version to 0.1.0
```
