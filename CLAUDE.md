# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A two-stage Chrome bookmark organizer. There's no build, package manager or test suite: it's plain Python (stdlib only) plus an unpacked Manifest V3 extension.

1. `classify.py` reads a Chrome profile's bookmarks JSON from disk, runs each bookmark through a rules module, and writes `organizer-extension/plan.js`.
2. `organizer-extension/` (a popup with **Dry run** and **Apply**) loads `plan.js` and applies it through the `chrome.bookmarks` API.

Changes must go through the extension, never by editing the bookmarks file on disk. Synced profiles store bookmarks in `AccountBookmarks`, and Chrome Sync overwrites offline file edits.

## Commands

```sh
python classify.py --profile <signed-in email | "Profile N">          # regenerate plan.js
python classify.py --profile <...> --list                             # also print every bookmark grouped by target
node --check organizer-extension/popup.js                             # quick syntax check (no tests exist)
```

On Windows, run Python with `-I` (isolated mode) if needed. `classify.py` already reconfigures stdout to UTF-8 because bookmark titles are often Cyrillic. Paths assume `%LOCALAPPDATA%\Google\Chrome\User Data` (Windows only; the README says to adjust `USER_DATA` for other platforms).

Applying a plan is manual. In the target Chrome profile: `chrome://extensions` → Developer mode → Load unpacked → `organizer-extension/` → Dry run → Apply.

## Architecture: how the pieces connect

- **Rules contract.** `classify.py` loads `rules.py` if it exists, otherwise `rules.example.py`, by file path via `importlib.util`. The module provides:
  - `RULES`: an ordered list of `(target, predicate(p, t, h, u))`. The first match wins. `p` is the original folder path, `t` is the lowercased title, `h` is the host without `www.`, and `u` is the lowercased URL.
  - optional `OVERRIDES`: `(field, substring, target)` entries, checked before `RULES`.
  - optional `FALLBACK`.

  Targets use `/` for subfolders. The special target `Quick Links` means "loose at the front of the Bookmarks bar".
- **`plan.js` is the interface between the stages.** It defines two globals that `popup.js` uses without importing anything (both are loaded by `popup.html`):
  - `ORDER`: top-level folder order, derived from the order targets first appear in `RULES`, then `OVERRIDES`.
  - `PLAN`: `{url: targetPath}`. It's keyed by URL, so deduplication is implicit: the first occurrence wins in `classify.py`, and the extension removes later nodes with the same URL.
- **Extension behavior (`popup.js`).** When Chrome exposes both local and account roots, it prefers the account (`syncing === true`) roots. It creates the folders under the bookmarks bar, moves the nodes, and reorders the top-level folders after the quick links. Finally it deletes every folder left empty, including empty folders that existed before. URLs that aren't in `PLAN` are left untouched. Dry run creates nothing; it uses `new:<path>` placeholder ids for folders that don't exist yet.

## Public repo: keep personal data out

The repo (`github.com/Lolibai/chrome-booksmarks-extension`, MIT) is public. `.gitignore` excludes `rules.py` (personal rules naming clients and personal docs), `organizer-extension/plan.js` (real bookmark URLs), `backup/` (raw bookmark dumps), `.claude/` and `.mcp.json`. Keep generic examples in `rules.example.py` only. Before committing, check that no personal strings from `rules.py` or `plan.js` leaked into tracked files.
