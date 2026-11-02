# Model Meta Bridge

## Skills
* Before writing a new skill, read `.claude/skills/skill-writing/SKILL.md`
* Before creating a new branch, read `.claude/skills/branch-naming/SKILL.md`
* Before committing changes, read `.claude/skills/committing/SKILL.md`
* Before running tests locally, read `.claude/skills/running-tests/SKILL.md`

### Code Organization & Documentation Conventions

1. **Separate code by category within `src/`.** Group source files into meaningful category
   subpackages (by domain, feature, or responsibility) rather than placing everything at the top
   level of the package. When adding new code, put it in the directory that matches its purpose,
   and create a new category directory when none fits.
2. **Write a `CLAUDE.md` whenever a new directory is created** — whether it is a direct child of
   `src/` or nested any number of levels below it. Each new directory gets its own
   `CLAUDE.md` describing what the directory holds and any conventions specific to it.
3. **Keep `CLAUDE.md` files current as the project evolves.** When a directory's contents change
   meaningfully (new files, changed responsibilities, new patterns), make a genuine attempt to update
   that directory's `CLAUDE.md` so the documentation stays accurate.

### Code Conventions

#### Comments and docstrings

Default: **none**. The assumed reader knows Python and this codebase, including every
directory's `CLAUDE.md`. Write one only when that reader would still be stuck. This applies equally
to `#` comments, function and class docstrings, and module docstrings, and takes precedence over any
global comment skill.

**Keep:**
- A reason that isn't visible in the code: an outside constraint, an order that matters, a library
  quirk, a deliberate deviation.
  ```python
  # "x" is O_EXCL: a replace would overwrite the file this exists to protect.
  with path.open("x", encoding="utf-8") as f:
  ```
  ```python
  if not isinstance(count, int) or isinstance(count, bool):  # bool is an int
  ```
- A one-line docstring for a contract the signature can't show: what it raises, what the caller
  must do first ("Pass it trimmed."), what `None` means.

**Cut:**
- What a line does, or a name restated in prose.
- Narration of UI flow or behavior the directory's `CLAUDE.md` already covers.
- Multi-paragraph module docstrings. Use one line, or nothing.
- `Args:`/`Returns:` sections that repeat type hints.
- Dates and authors.
- Section banners of any kind, e.g. `# -- name ---` or `# ====`.

**Existing code:** older comments and docstrings were written before these rules, so don't copy
their length. Trim one only when you're already editing that code. Don't do standalone cleanups.

**Check** each comment or docstring with two questions:
1. Would a senior dev who knows this repo be stuck without it? If not, delete it.
2. Does it refer to something that isn't in the repo, like a conversation, plan, review, or ticket?
   If so, replace the comment with a link or reference to that source so there's a breadcrumb trail.

#### Dict merges

Merge dicts with unpacking (`{**a, **b}`), never `|` or `|=`. Unpacking also covers literal keys
(`{**role, "count": 2}`), three or more sources, and non-`dict` mappings, so one form works
everywhere. `|` and `|=` on sets are fine.

### Feature Development Practices

Keep PRs as small as possible by ensuring each branch is purpose-built for a specific sub-task of a feature.

## General Workflow

1. Install this add-on into Blender.
2. Separately, run Model Meta. See the `model-meta` repo for how it works.
