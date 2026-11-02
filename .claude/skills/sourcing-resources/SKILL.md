---
name: sourcing-resources
description: Use whenever you are about to pick a library, package, doc page, example, or reference implementation to rely on or recommend.
---

# Source resources and examples from the tool's owner

## Trigger
Use this skill whenever you are about to choose, cite, install, or recommend a resource or example:
a library, package, type stub, plugin, doc page, sample project, or reference implementation. This
covers any tool or platform (Blender, Godot, Unity, Unreal, Python, and so on).

## Pre-requisites
- The tool or platform the resource is for, and the organization that owns it (e.g. Blender →
  Blender Foundation, Godot → Godot Foundation, Unity → Unity Technologies, Unreal → Epic Games).
- The version of that tool in use. Read it from the project (manifest, lockfile, `--version`
  output). If it can't be found, ask.

## Steps
1. Search for candidates. Start with the owner's own channels: official docs, the owner's
   GitHub/GitLab organization, the owner's package registry account, the owner's sample projects.
   Mirrors of official docs (e.g. Context7) count as official content when you give the original page
   URL as the backlink.
2. Keep a candidate only if it meets **all** of the main requirements:
   1. **Owner-maintained, or owner-endorsed.** It is maintained by the owner, or it is a community
      project the owner actively endorses: the owner's own docs or site recommend or link to it.
      Being merely hosted on the owner's marketplace or forum is not endorsement.
   2. **Not deprecated or inactive.** Not archived, not marked deprecated or unmaintained, and it has
      a release or commit within the last 12 months.
   3. **Matches the version in use.** It targets the version from Pre-requisites, not an older or
      newer major version.
3. For each kept candidate, record the evidence: the owner page that maintains or endorses it, the
   date of its latest release or commit, and the version it targets. Give a link for each.
4. If at least one candidate passes, use or recommend it, with its evidence. Stop here.
5. If none pass, tell the user before anything else: say that nothing meets the main requirements,
   and list what you checked and why each failed. Then offer fallbacks, in this order:
   1. **Well-liked community sources.** Not owner-endorsed, but widely used: a public repo with a
      non-zero star count, recent activity, and the matching version.
   2. **Fringe sources.** Only if step 5.1 finds nothing. Open with a clear, prominent warning that
      these are obscure and unvetted.
6. For every fallback, state exactly which main requirements it breaks and how (e.g. "breaks 1: a
   community project; the owner's docs don't mention it"). Give its link, star count, and latest
   activity date.
7. Don't install, import, or build on a fallback until the user picks it.

## Verification process
- Every resource you used or recommended has a link to the owner page that maintains or endorses
  it, its latest release or commit date (within 12 months), and the version it targets.
- If you offered a fallback, the user was told first that nothing met the main requirements, and
  each fallback lists the requirements it breaks.
- No fallback was installed or used before the user chose it.
- A fringe fallback appears only when no well-liked fallback exists, and it carries a warning.

## Example output
Request: "Make my editor resolve `import bpy`."

```
Recommended: `bpy` on PyPI (https://pypi.org/project/bpy/), published by Blender Foundation.
- Owner: Blender's API docs say "A pre-compiled `bpy` module is available via PIP"
  (https://docs.blender.org/api/current/info_advanced_blender_as_bpy.html).
- Active: latest release 5.2.3, 2026-10-22.
- Version: 4.2.x releases match `blender_version_min = "4.2.0"` (Python 3.11).

Rejected: fake-bpy-module (https://github.com/nutti/fake-bpy-module).
- Breaks 1: a community project, not maintained or endorsed by Blender Foundation.
```
