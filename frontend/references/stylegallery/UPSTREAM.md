---
description: Read this when you need the synced upstream revision or resync procedure.
---

# StyleGallery upstream snapshot

- Repository: https://github.com/changeroa/StyleGallery
- Revision: 2a9ae14e1ed1e6ebc9ec525a7c305a7cc9830b34
- Sync date (upstream commit): 2026-09-23
- Included: Markdown under patterns/, recipes/, guides/, motion/, design-engineering/, game-ui/, platform-guides/, design-terminology/, layout/; root index.md, CATALOG.md, GUIDE.md; LICENSE-DOCS and NOTICE.
- Excluded: design-engineering/reference-profiles/, game-ui/unity/data/, and all other upstream material.
- Transforms: remove generated maintenance lines; pin excluded relative links, reference definitions and path-like code spans to this revision; add routing cues from the cue overlay where needed; preserve source frontmatter.

## Resync

Check out the desired upstream revision, then from the pack root run `python3 tools/sync-stylegallery.py --upstream PATH` followed by `python3 tools/sync-stylegallery.py --upstream PATH --check` and `python3 tools/check-skills.py --skills frontend`. Review the diff and attribution before updating references elsewhere in the pack.
